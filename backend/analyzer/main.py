#!/usr/bin/env python3
"""
main.py - Automated Firmware Analysis CLI (DLMS/COSEM project).

Pipeline per file:
    [identify] -> [extract if container] -> (repeat recursively) ->
    [entropy scan] -> [string scan] -> [YARA scan] -> [targeted symbol disassembly]
    -> [protocol verdict] -> [report]

Design principle: one file's failure at any stage never stops the run.
Every stage catches its own errors and records a clear, specific reason
in the report instead of raising.

Usage:
    python3 main.py --input /path/to/firmware_folder_or_file --output ./report
    python3 main.py --input update_670_1.1.27_MR.msi --output ./report --skip-symbols
"""

import argparse
import hashlib
import os
import shutil
import sys
import tempfile

from modules.extractor import walk_and_extract, flatten_tree
from modules.entropy_analysis import analyze_entropy
from modules.string_scanner import scan_strings
from modules.yara_scanner import scan_with_yara
from modules.symbol_analyzer import analyze_symbols
from modules.report_generator import build_file_report, write_json_report, write_markdown_report

# Dedup cache: content signature -> path of the file whose full result was
# actually computed. The same physical firmware file often appears many
# times across a corpus (nested inside multiple installers/zips that all
# ship the same sub-component) - re-running strings/YARA/objdump on an
# identical file every time wastes a lot of runtime for zero new
# information, so subsequent occurrences are recorded as duplicates
# pointing back at the canonical result instead of being fully re-analyzed.
_content_signature_cache = {}


def compute_signature(path: str, sample_bytes: int = 1024 * 1024):
    """(size, md5-of-first-sample_bytes) - cheap enough to run on every
    file without hashing huge binaries in full, good enough to catch the
    'literally the same file re-extracted elsewhere' case that dominates
    firmware corpora full of nested/duplicated installers."""
    try:
        size = os.path.getsize(path)
        h = hashlib.md5()
        with open(path, "rb") as f:
            h.update(f.read(sample_bytes))
        return (size, h.hexdigest())
    except OSError:
        return None


def is_binary_leaf(node) -> bool:
    """A node is worth running entropy/strings/YARA/symbols on if it's an
    'ok' leaf (executable) rather than a container or a skipped document."""
    return node.status == "ok" and node.container_kind is None


def analyze_leaf(node, skip_symbols: bool):
    # Dedup check: has this exact content already been fully analyzed
    # somewhere else in the corpus?
    sig = compute_signature(node.path)
    if sig is not None and sig in _content_signature_cache:
        canonical_path = _content_signature_cache[sig]
        print(f"  [DUPLICATE] {node.path} - identical content already analyzed at {canonical_path}, skipping re-analysis")
        return build_file_report(
            artifact_path=node.path,
            file_type=node.file_type,
            extraction_status=f"skipped: duplicate content, identical to already-analyzed file '{canonical_path}'",
        )
    if sig is not None:
        _content_signature_cache[sig] = node.path

    print(f"  Analyzing: {node.path}")

    entropy_result = analyze_entropy(node.path)
    if not entropy_result["success"]:
        print(f"    [WARN] Entropy scan failed: {entropy_result['error']}")

    string_result = scan_strings(node.path)
    if not string_result["success"]:
        print(f"    [WARN] String scan failed: {string_result['error']}")

    yara_result = scan_with_yara(node.path)
    if not yara_result["success"]:
        print(f"    [WARN] YARA scan failed: {yara_result['error']}")

    symbol_result = None
    if not skip_symbols:
        extra_keywords = []
        if string_result.get("success"):
            # Feed anything found in the unsafe_functions / auth_credentials
            # categories back in as extra symbol-name search terms - this
            # is what makes the objdump target "dynamic" per file instead
            # of a fixed guess list.
            for cat in ("unsafe_functions", "auth_credentials"):
                extra_keywords.extend(string_result["matches"].get(cat, []))
        symbol_result = analyze_symbols(node.path, node.file_type, extra_keywords=extra_keywords)
        if not symbol_result["success"]:
            print(f"    [WARN] Symbol analysis failed: {symbol_result['error']}")

    return build_file_report(
        artifact_path=node.path,
        file_type=node.file_type,
        extraction_status=f"{node.status}: {node.status_detail}",
        entropy_result=entropy_result,
        string_result=string_result,
        yara_result=yara_result,
        symbol_result=symbol_result,
    )


def collect_input_files(input_path: str):
    if os.path.isfile(input_path):
        return [input_path]
    if os.path.isdir(input_path):
        files = []
        for root, _dirs, names in os.walk(input_path):
            for name in names:
                files.append(os.path.join(root, name))
        return sorted(files)
    return []


def main():
    parser = argparse.ArgumentParser(description="Automated firmware analysis pipeline (DLMS/COSEM project)")
    parser.add_argument("--input", required=True, help="Firmware file OR folder to scan")
    parser.add_argument("--output", default="./analysis_report", help="Output directory for reports")
    parser.add_argument("--max-depth", type=int, default=6, help="Max archive extraction recursion depth")
    parser.add_argument("--skip-symbols", action="store_true",
                         help="Skip symbol-table/disassembly stage (faster, avoids objdump crashes on huge binaries)")
    parser.add_argument("--work-dir", default=None,
                         help="Directory to extract archives into (default: a temp dir, auto-cleaned)")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"[FATAL] Input path does not exist: {args.input}")
        sys.exit(1)

    input_files = collect_input_files(args.input)
    if not input_files:
        print(f"[FATAL] No files found under: {args.input}")
        sys.exit(1)

    print(f"Found {len(input_files)} top-level file(s) to process.\n")

    work_dir = args.work_dir or tempfile.mkdtemp(prefix="fw_analysis_")
    cleanup_work_dir = args.work_dir is None
    os.makedirs(work_dir, exist_ok=True)

    all_reports = []
    fatal_errors = []

    for i, fpath in enumerate(input_files, 1):
        print(f"[{i}/{len(input_files)}] {fpath}")
        try:
            tree_root = walk_and_extract(fpath, work_dir, max_depth=args.max_depth)
        except Exception as e:
            # Catch-all so ONE catastrophically broken file cannot kill the run.
            msg = f"unexpected fatal error during extraction: {e}"
            print(f"  [ERROR] {msg}")
            fatal_errors.append({"path": fpath, "error": msg})
            all_reports.append(build_file_report(fpath, "unknown", f"error: {msg}"))
            continue

        all_nodes = flatten_tree(tree_root)
        for node in all_nodes:
            if node.status == "error":
                print(f"  [ERROR] {node.path}: {node.status_detail}")
                all_reports.append(build_file_report(node.path, node.file_type, f"error: {node.status_detail}"))
            elif node.status == "skipped":
                print(f"  [SKIP]  {node.path}: {node.status_detail}")
                all_reports.append(build_file_report(node.path, node.file_type, f"skipped: {node.status_detail}"))
            elif is_binary_leaf(node):
                try:
                    report = analyze_leaf(node, skip_symbols=args.skip_symbols)
                except Exception as e:
                    msg = f"unexpected fatal error during analysis: {e}"
                    print(f"  [ERROR] {node.path}: {msg}")
                    report = build_file_report(node.path, node.file_type, f"error: {msg}")
                all_reports.append(report)
            # 'ok' container nodes (already extracted, children queued) need no report line

    os.makedirs(args.output, exist_ok=True)
    json_path = os.path.join(args.output, "report.json")
    md_path = os.path.join(args.output, "report.md")
    write_json_report(all_reports, json_path)
    write_markdown_report(all_reports, md_path)

    print(f"\nDone. {len(all_reports)} file result(s) recorded.")
    if fatal_errors:
        print(f"{len(fatal_errors)} file(s) had fatal errors - see report for details.")
    print(f"JSON report:     {json_path}")
    print(f"Markdown report: {md_path}")

    if cleanup_work_dir:
        shutil.rmtree(work_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
