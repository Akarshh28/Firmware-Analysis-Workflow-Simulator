"""
symbol_analyzer.py - Dynamic symbol-table extraction and TARGETED disassembly.

This is the automated version of what was done manually on Relion670:
  1. Pull the full symbol table (objdump -t).
  2. Cross-reference symbol names against whatever the strings/YARA pass
     already flagged as suspicious for THIS specific file (not a fixed
     list decided in advance).
  3. Disassemble only those specific functions - never the whole binary -
     so the pipeline stays fast and doesn't need Ghidra/GUI tools that
     have proven unstable in the VM.

The architecture is auto-detected from `file` output so this works
unmodified on PowerPC (Relion670-style), ARM, MIPS, or x86 binaries -
the objdump binary used is picked automatically per config.ARCH_OBJDUMP_MAP.
"""

import re
import shutil
import subprocess

from config import (
    ARCH_OBJDUMP_MAP, SUSPICIOUS_SYMBOL_KEYWORDS,
    MAX_SYMBOLS_TO_DISASSEMBLE, MAX_FUNCTION_DISASSEMBLE_SIZE,
)

SYMTAB_LINE_RE = re.compile(
    r"^(?P<addr>[0-9a-fA-F]+)\s+\S+\s+\S+\s+\S+\s+(?P<size>[0-9a-fA-F]+)\s+(?P<name>\S+)"
)


def pick_objdump_binary(file_type: str) -> str:
    """Choose the correct objdump variant for this architecture. Falls back
    to plain 'objdump' if nothing matches (works for native x86 binaries)."""
    for signature, binary_name in ARCH_OBJDUMP_MAP:
        if signature.lower() in file_type.lower():
            return binary_name
    return "objdump"


def get_symbol_table(path: str, objdump_bin: str):
    """
    Returns (success, symbols_or_error).
    symbols is a list of dicts: {"address": int, "size": int, "name": str}
    """
    if shutil.which(objdump_bin) is None:
        return False, (
            f"required disassembler '{objdump_bin}' is not installed on this "
            f"system. Install the matching binutils cross-toolchain package "
            f"(e.g. 'sudo apt-get install binutils-powerpc-linux-gnu') and re-run."
        )

    try:
        result = subprocess.run(
            [objdump_bin, "-t", path],
            capture_output=True, text=True, timeout=120,
        )
    except subprocess.TimeoutExpired:
        return False, "symbol table extraction timed out (binary may be very large)"
    except Exception as e:
        return False, f"unexpected error extracting symbol table: {e}"

    if result.returncode != 0:
        return False, f"{objdump_bin} -t failed: {result.stderr.strip()[:300]}"

    symbols = []
    for line in result.stdout.splitlines():
        m = SYMTAB_LINE_RE.match(line)
        if not m:
            continue
        try:
            symbols.append({
                "address": int(m.group("addr"), 16),
                "size": int(m.group("size"), 16),
                "name": m.group("name"),
            })
        except ValueError:
            continue  # malformed line, skip rather than crash

    if not symbols:
        return False, (
            "symbol table extraction ran but found no symbols - the binary "
            "may be stripped (no debug/function names available)"
        )
    return True, symbols


def flag_suspicious_symbols(symbols, extra_keywords=None):
    """Cross-reference symbol names against the suspicious-keyword list,
    PLUS any extra keywords pulled from this file's own strings/YARA
    findings (e.g. a category name like 'unsafe_functions' contributes
    strcpy/memcpy as keywords automatically)."""
    keywords = list(SUSPICIOUS_SYMBOL_KEYWORDS)
    if extra_keywords:
        keywords.extend(k.lower() for k in extra_keywords)

    flagged = []
    seen_names = set()
    for sym in symbols:
        name_lower = sym["name"].lower()
        for kw in keywords:
            if kw in name_lower and sym["name"] not in seen_names:
                flagged.append(sym)
                seen_names.add(sym["name"])
                break

    return flagged[:MAX_SYMBOLS_TO_DISASSEMBLE]


def disassemble_symbol(path: str, objdump_bin: str, symbol: dict):
    """Disassemble a single function using its address/size from the
    symbol table. Returns (success, disassembly_text_or_error)."""
    start = symbol["address"]
    size = min(symbol["size"], MAX_FUNCTION_DISASSEMBLE_SIZE) or 64
    stop = start + size

    try:
        result = subprocess.run(
            [objdump_bin, "-d",
             f"--start-address=0x{start:x}", f"--stop-address=0x{stop:x}", path],
            capture_output=True, text=True, timeout=60,
        )
    except subprocess.TimeoutExpired:
        return False, "disassembly timed out"
    except Exception as e:
        return False, f"unexpected error during disassembly: {e}"

    if result.returncode != 0:
        return False, f"objdump failed: {result.stderr.strip()[:300]}"
    if not result.stdout.strip():
        return False, "objdump produced no output for this address range"
    return True, result.stdout


def analyze_symbols(path: str, file_type: str, extra_keywords=None):
    """
    Full pipeline step: pick objdump, pull symbol table, flag suspicious
    symbols, disassemble each. Never raises.

    Returns:
        {
          "success": bool,
          "error": str or None,           # error at the symbol-table stage
          "objdump_used": str,
          "total_symbols": int,
          "flagged_symbols": [
              {"name": str, "address": str, "size": int,
               "disassembly_status": "ok"|"error",
               "disassembly": str or error message}
          ]
        }
    """
    result = {
        "success": False, "error": None, "objdump_used": "",
        "total_symbols": 0, "flagged_symbols": [],
    }

    objdump_bin = pick_objdump_binary(file_type)
    result["objdump_used"] = objdump_bin

    ok, symbols_or_err = get_symbol_table(path, objdump_bin)
    if not ok:
        result["error"] = symbols_or_err
        return result

    symbols = symbols_or_err
    result["total_symbols"] = len(symbols)

    flagged = flag_suspicious_symbols(symbols, extra_keywords)
    for sym in flagged:
        ok, disasm_or_err = disassemble_symbol(path, objdump_bin, sym)
        flagged_entry = {
            "name": sym["name"],
            "address": hex(sym["address"]),
            "size": sym["size"],
            "disassembly_status": "ok" if ok else "error",
            "disassembly": disasm_or_err if ok else f"[not disassembled] {disasm_or_err}",
        }
        result["flagged_symbols"].append(flagged_entry)

    result["success"] = True
    return result
