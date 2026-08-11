"""
yara_scanner.py - Wraps the bundled YARA ruleset (Phase 2, Pattern Matching step).
"""

import os
import glob

RULES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "yara_rules")

_compiled_rules = None
_compile_error = None

YARA_RULE_CWE_MAP = {
    "Weak_Hash_MD5": "CWE-327",
    "Weak_Hash_SHA1": "CWE-327",
    "Weak_Cipher_DES_RC4": "CWE-327",
    "Weak_Random_Number_Generation": "CWE-338",
    "Deprecated_Crypto_Combined_Flag": "CWE-327",
    "Unsafe_String_Functions": "CWE-120",
    "Unsafe_Memory_Functions": "CWE-120",
    "Unsafe_Format_String_Risk": "CWE-134",
    "Unsafe_Functions_Combined_Flag": "CWE-120",
    "Plaintext_Password_In_Format_String": "CWE-532",
    "Verbose_Authentication_Errors": "CWE-203",
    "Legacy_Debug_Login_Shell": "CWE-306",
    "Hardcoded_Credential_Keywords": "CWE-798",
    "Authentication_Weakness_Combined_Flag": "CWE-798",
    "FTP_Server_Present": "CWE-319",
    "TFTP_Service_Present": "CWE-306",
    "Legacy_SNMP_Present": "CWE-319",
    "No_Encrypted_Management_Protocol": "CWE-319",
    "Insecure_Network_Services_Combined_Flag": "CWE-319",
}


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
        cwe = YARA_RULE_CWE_MAP.get(m.rule)
        if not cwe:
            # Leave protocol/identification rules without a CWE, otherwise fallback to CWE-000
            if m.rule.startswith("DLMS_COSEM") or m.rule.startswith("IEC61850") or m.rule.startswith("RTOS_") or m.rule.startswith("Vendor_") or m.rule.startswith("Architecture_"):
                cwe = None
            else:
                cwe = "CWE-000"

        result["matches"].append({
            "rule": m.rule,
            "cwe": cwe,
            "severity": m.meta.get("severity") or m.meta.get("confidence") or "info",
            "description": m.meta.get("description", ""),
            "action": m.meta.get("action"),
        })

    result["success"] = True
    return result
