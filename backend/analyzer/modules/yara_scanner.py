"""
yara_scanner.py - Wraps the bundled YARA ruleset (Phase 2, Pattern Matching step).
"""

import os
import glob

RULES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "yara_rules")

_compiled_rules = None
_compile_error = None


def _load_rules():
    global _compiled_rules, _compile_error
    if _compiled_rules is not None or _compile_error is not None:
        return  # already attempted

    try:
        import yara
    except ImportError:
        _compile_error = "yara-python is not installed (pip install yara-python --break-system-packages)"
        return

    yar_files = glob.glob(os.path.join(RULES_DIR, "*.yar"))
    if not yar_files:
        _compile_error = f"no .yar rule files found in {RULES_DIR}"
        return

    filepaths = {os.path.basename(f): f for f in yar_files}
    try:
        _compiled_rules = yara.compile(filepaths=filepaths)
    except Exception as e:
        _compile_error = f"YARA ruleset failed to compile: {e}"


def scan_with_yara(path: str):
    """
    Returns a dict:
        {
          "success": bool,
          "error": str or None,
          "matches": [ {"rule": str, "severity": str, "description": str, "action": str or None}, ... ]
        }
    """
    result = {"success": False, "error": None, "matches": []}

    _load_rules()
    if _compile_error is not None:
        result["error"] = _compile_error
        return result

    try:
        matches = _compiled_rules.match(path)
    except Exception as e:
        result["error"] = f"YARA scan failed on this file: {e}"
        return result

    for m in matches:
        result["matches"].append({
            "rule": m.rule,
            "severity": m.meta.get("severity") or m.meta.get("confidence") or "info",
            "description": m.meta.get("description", ""),
            "action": m.meta.get("action"),
        })

    result["success"] = True
    return result
