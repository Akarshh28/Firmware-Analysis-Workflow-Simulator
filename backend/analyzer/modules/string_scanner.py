"""
string_scanner.py - Categorized string/keyword extraction (Phase 2, Step A).

Runs `strings -a` once per file and filters the output against every
keyword category in config.py, rather than shelling out to grep once per
category (fewer subprocess calls, faster on large binaries).
"""

import re
import subprocess

from config import KEYWORD_CATEGORIES


def extract_raw_strings(path: str, min_len: int = 4, timeout: int = 120):
    """Return (success, list_of_strings_or_error_message)."""
    try:
        result = subprocess.run(
            ["strings", "-a", "-n", str(min_len), path],
            capture_output=True, text=True, timeout=timeout,
        )
        if result.returncode != 0:
            return False, f"strings command failed with exit code {result.returncode}"
        return True, result.stdout.splitlines()
    except FileNotFoundError:
        return False, "'strings' tool not installed"
    except subprocess.TimeoutExpired:
        return False, f"strings extraction timed out after {timeout}s (file may be very large)"
    except Exception as e:
        return False, f"unexpected error running strings: {e}"


def scan_strings(path: str):
    """
    Returns a dict:
        {
          "success": bool,
          "error": str or None,
          "total_strings": int,
          "matches": { category: [matched_string, ...], ... }   # capped per category
        }
    """
    result = {"success": False, "error": None, "total_strings": 0, "matches": {}}

    ok, strings_or_err = extract_raw_strings(path)
    if not ok:
        result["error"] = strings_or_err
        return result

    all_strings = strings_or_err
    result["total_strings"] = len(all_strings)

    compiled = {
        cat: [re.compile(pat, re.IGNORECASE) for pat in patterns]
        for cat, patterns in KEYWORD_CATEGORIES.items()
    }

    matches = {cat: [] for cat in KEYWORD_CATEGORIES}
    MAX_PER_CATEGORY = 50  # cap so the report stays readable

    for line in all_strings:
        for cat, patterns in compiled.items():
            if len(matches[cat]) >= MAX_PER_CATEGORY:
                continue
            for pat in patterns:
                if pat.search(line):
                    if cat == "network_services":
                        line_lower = line.lower()
                        if any(domain in line_lower for domain in ["digicert.com", "verisign.com", "symantec.com", "thawte.com", "geotrust.com", "globalsign.com"]):
                            continue
                    matches[cat].append(line.strip()[:200])
                    break

    result["matches"] = {cat: vals for cat, vals in matches.items() if vals}
    result["success"] = True
    return result
