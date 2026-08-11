"""
extractor.py - File identification and recursive container extraction.

Design goal: NEVER let one bad file crash the whole run. Every subprocess
call is wrapped so a failure produces a clear, categorized status string
instead of an unhandled exception.
"""

import os
import shutil
import subprocess
from dataclasses import dataclass, field
from typing import List, Optional

from config import CONTAINER_SIGNATURES, MAX_RECURSION_DEPTH, DOCUMENT_EXTENSIONS


@dataclass
class ArtifactNode:
    """One file discovered during the walk - either the original input,
    or something produced by extracting an archive."""
    path: str
    depth: int
    file_type: str = ""          # raw `file` command output
    status: str = "pending"      # pending | ok | skipped | error
    status_detail: str = ""      # human-readable reason
    container_kind: Optional[str] = None   # zip / msi / cab / gzip / tar / None
    children: List["ArtifactNode"] = field(default_factory=list)


def run_cmd(cmd, timeout=120):
    """Run a subprocess command, returning (success, stdout, stderr_or_reason).
    Never raises - all failure modes are converted to a clean error string."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout
        )
        if result.returncode != 0:
            return False, result.stdout, f"exit code {result.returncode}: {result.stderr.strip()[:300]}"
        return True, result.stdout, ""
    except FileNotFoundError:
        return False, "", f"required tool not installed: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return False, "", f"timed out after {timeout}s (file may be too large or tool hung)"
    except PermissionError:
        return False, "", "permission denied running tool"
    except Exception as e:  # last-resort catch-all, still labelled clearly
        return False, "", f"unexpected error running {cmd[0]}: {e}"


def identify_file(path: str) -> tuple:
    """Return (success, file_type_string_or_error)."""
    if not os.path.isfile(path):
        return False, "not a regular file (missing or is a directory)"
    ok, out, err = run_cmd(["file", "-b", path], timeout=30)
    if not ok:
        return False, f"'file' command failed: {err}"
    return True, out.strip()


def classify_container(file_type: str) -> Optional[str]:
    """Match the `file` output against known container signatures."""
    for signature, kind in CONTAINER_SIGNATURES.items():
        if signature.lower() in file_type.lower():
            return kind
    return None


def is_known_document(path: str) -> bool:
    return os.path.splitext(path)[1].lower() in DOCUMENT_EXTENSIONS


def extract_zip(path: str, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    ok, out, err = run_cmd(["unzip", "-o", path, "-d", out_dir], timeout=180)
    if not ok:
        return False, f"zip extraction failed: {err}"
    return True, ""


def extract_cab(path: str, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    ok, out, err = run_cmd(["cabextract", "-d", out_dir, path], timeout=180)
    if not ok:
        return False, f"cab extraction failed: {err}"
    return True, ""


def _binwalk_extract_args(base_args):
    """Add --run-as=root unconditionally to avoid any permission checking bugs
    on Render."""
    return [base_args[0], "--run-as=root"] + base_args[1:]


def extract_msi_via_binwalk(path: str, out_dir: str):
    """MSI installers in this project have consistently turned out to wrap
    a Cabinet archive; binwalk -e is the reliable way to carve it out."""
    os.makedirs(out_dir, exist_ok=True)
    args = _binwalk_extract_args(["binwalk", "--dd=.*", "-e", "-C", out_dir, path])
    ok, out, err = run_cmd(args, timeout=300)
    if not ok:
        return False, f"binwalk extraction failed: {err}"
    # binwalk creates a subfolder named _<basename>.extracted
    extracted_dir = os.path.join(out_dir, f"_{os.path.basename(path)}.extracted")
    if not os.path.isdir(extracted_dir):
        return False, "binwalk ran but produced no extracted directory (installer may not contain a known embedded format)"
    return True, ""


def extract_generic_binwalk(path: str, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    args = _binwalk_extract_args(["binwalk", "-e", "-C", out_dir, path])
    ok, out, err = run_cmd(args, timeout=300)
    if not ok:
        return False, f"binwalk extraction failed: {err}"
    extracted_dir = os.path.join(out_dir, f"_{os.path.basename(path)}.extracted")
    if not os.path.isdir(extracted_dir):
        return False, "binwalk ran but found nothing to extract"
    return True, ""


EXTRACTORS = {
    "zip": extract_zip,
    "cab": extract_cab,
    "msi": extract_msi_via_binwalk,
    "gzip": extract_generic_binwalk,
    "tar": extract_generic_binwalk,
}


def find_new_files(out_dir: str, already_seen: set) -> List[str]:
    found = []
    for root, _dirs, files in os.walk(out_dir):
        for fname in files:
            fpath = os.path.join(root, fname)
            if fpath in already_seen:
                continue
            # Skip zero-byte files: these are almost always artifacts of a
            # partial/failed extraction (e.g. a truncated CAB), not real
            # content. Analyzing them just produces noisy, misleading
            # "entropy scan failed: file is empty" errors downstream.
            try:
                if os.path.getsize(fpath) == 0:
                    already_seen.add(fpath)
                    continue
            except OSError:
                continue
            found.append(fpath)
            already_seen.add(fpath)
    return found


def walk_and_extract(root_path: str, work_dir: str, max_depth: int = MAX_RECURSION_DEPTH) -> ArtifactNode:
    """
    Recursively identify and extract root_path, returning a tree of
    ArtifactNode results. Every node gets a status so the report can show
    exactly what happened (or went wrong) at every step - nothing is
    silently swallowed.
    """
    root = ArtifactNode(path=root_path, depth=0)
    _process_node(root, work_dir, max_depth, seen_paths=set())
    return root


def _process_node(node: ArtifactNode, work_dir: str, max_depth: int, seen_paths: set):
    seen_paths.add(node.path)

    if node.depth > max_depth:
        node.status = "skipped"
        node.status_detail = f"max recursion depth ({max_depth}) reached"
        return

    ok, file_type_or_err = identify_file(node.path)
    if not ok:
        node.status = "error"
        node.status_detail = f"file identification failed: {file_type_or_err}"
        return
    node.file_type = file_type_or_err

    if is_known_document(node.path):
        node.status = "skipped"
        node.status_detail = "recognized non-firmware document type (pdf/xlsx/png/etc.) - not analyzed"
        return

    container_kind = classify_container(node.file_type)
    node.container_kind = container_kind

    if container_kind is None:
        # Not a container we know how to unpack further. Treat this as an
        # analyzable leaf regardless of exact type - a raw/unrecognized
        # binary blob (e.g. a flash dump with no ELF header) still needs
        # an entropy + strings + YARA pass; only symbol/disassembly will
        # gracefully skip itself later if the format isn't executable.
        node.status = "ok"
        if "ELF" in node.file_type or "PE32" in node.file_type or "executable" in node.file_type.lower():
            node.status_detail = "leaf binary ready for analysis"
        else:
            node.status_detail = (
                f"unrecognized/non-executable file type ('{node.file_type}') - "
                f"not a known archive format, so treated as a raw leaf for "
                f"entropy/string/YARA analysis. Symbol/disassembly stage will "
                f"likely report 'no symbols' for this file, which is expected."
            )
        return

    extractor = EXTRACTORS.get(container_kind)
    if extractor is None:
        node.status = "error"
        node.status_detail = f"no extractor implemented for container kind '{container_kind}'"
        return

    out_dir = os.path.join(work_dir, os.path.basename(node.path) + "_extracted")
    ok, err = extractor(node.path, out_dir)
    if not ok:
        node.status = "error"
        node.status_detail = err
        return

    node.status = "ok"
    node.status_detail = f"extracted as {container_kind}"

    new_files = find_new_files(out_dir, seen_paths)
    if not new_files:
        node.status_detail += " (but no files were found inside)"
        return

    for fpath in sorted(new_files):
        child = ArtifactNode(path=fpath, depth=node.depth + 1)
        node.children.append(child)
        _process_node(child, work_dir, max_depth, seen_paths)


def flatten_tree(node: ArtifactNode) -> List[ArtifactNode]:
    """Flatten the artifact tree into a single list (pre-order)."""
    out = [node]
    for child in node.children:
        out.extend(flatten_tree(child))
    return out
