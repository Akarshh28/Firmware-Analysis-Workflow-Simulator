import re
import subprocess

from config import KEYWORD_CATEGORIES

_ACCEPTABLE_BOUNDARY_CHARS = set(' \t_./:\\-,()[]"\'@')

def has_clean_boundary(line: str, match_start: int, match_end: int) -> bool:
    """Reject a match if the character immediately before/after it is an
    unusual symbol (#, $, <, >, !, ~, ;, {, }, +, |, etc.) - a strong
    signal this is binary noise coincidentally containing the keyword,
    not a genuine identifier/string."""
    before = line[match_start - 1] if match_start > 0 else ' '
    after = line[match_end] if match_end < len(line) else ' '
    for ch in (before, after):
        if ch.isalnum():
            continue  # e.g. "MD5Init" - keyword touching more letters is fine
        if ch not in _ACCEPTABLE_BOUNDARY_CHARS:
            return False
    return True

def extract_raw_strings(path: str, min_len: int = 4, timeout: int = 120):
    try:
        result = subprocess.run(
            ["strings", "-a", "-n", str(min_len), path],
            capture_output=True, text=True, timeout=timeout,
        )
        if result.returncode != 0:
            return False, f"strings command failed with exit code {result.returncode}"
        return True, result.stdout.splitlines()
    except Exception as e:
        return False, f"unexpected error running strings: {e}"

def is_false_positive(cat: str, line: str) -> bool:
    """Filters out UI prompts, standard library strings, and safe domains."""
    line_lower = line.lower()
    
    # 1. Filter out safe domains and PKI infrastructure
    if cat == "network_services":
        safe_domains = ["digicert", "verisign", "symantec", "thawte", "geotrust", "w3.org", "microsoft", "symcb", "symcd", ".crl", ".ocsp", "cacerts", "crl.", "ocsp."]
        if any(domain in line_lower for domain in safe_domains):
            return True
            
        # Ignore isolated short garbage strings common in packed binaries
        if len(line.strip()) <= 5:
            return True

    # 2. Filter out UI Labels and Logs for Credentials
    if cat == "auth_credentials":
        # Ignore UI prompt formats (e.g., "Password: ", "Login failed.")
        ignore_prompts = ["wrong password", "login failed", "enter password", "password:", "user name", "invalid", "error:"]
        if any(prompt in line_lower for prompt in ignore_prompts):
            return True
        # Ignore long descriptive sentences (usually installer text or logs)
        if len(line.split()) > 10: 
            return True

    # 3. Filter out system paths
    if "c:\\" in line_lower or "/usr/lib" in line_lower or "/flash/" in line_lower:
        return True

    return False

def scan_strings(path: str):
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

    matches = {cat: set() for cat in KEYWORD_CATEGORIES} # Using set to avoid duplicates
    MAX_PER_CATEGORY = 20  # Reduced to 20 for cleaner reports

    for line in all_strings:
        line_clean = line.strip()
        for cat, patterns in compiled.items():
            if len(matches[cat]) >= MAX_PER_CATEGORY:
                continue
            for pat in patterns:
                m = pat.search(line_clean)
                if m and has_clean_boundary(line_clean, m.start(), m.end()):
                    if not is_false_positive(cat, line_clean):
                        matches[cat].add(line_clean[:200])
                    break # Matched this category, move to next string

    result["matches"] = {cat: list(vals) for cat, vals in matches.items() if vals}
    result["success"] = True
    return result