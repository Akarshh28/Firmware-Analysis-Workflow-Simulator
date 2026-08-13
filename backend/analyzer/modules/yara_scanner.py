"""
yara_scanner.py - Wraps the bundled YARA ruleset (Phase 2, Pattern Matching step).
"""

import os
import glob
from modules.obis_registry import lookup_obis_meaning

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
    "Exploit_MS15_077_078": "CWE-119",
    "Exploit_MS15_077_078_HackingTeam": "CWE-119",
    "CVE_2015_1701_Taihou": "CWE-269",
}


def _load_rules():
    global _compiled_rules, _compile_error
    if _compiled_rules is not None or _compile_error is not None:
        return  # already attempted

    try:
        # pyrefly: ignore [missing-import]
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
        severity = m.meta.get("severity") or m.meta.get("confidence") or "info"
        description = m.meta.get("description", "")

        # --- PRODUCTION PATCH: Contextual Severity Downgrade ---
        if not cwe:
            if any(m.rule.startswith(prefix) for prefix in ["DLMS_COSEM", "IEC61850", "RTOS_", "Vendor_", "Architecture_"]):
                cwe = None
                severity = "info" # Protocol detection is just info, not a medium/high risk
            else:
                cwe = "CWE-000"
        
        # Downgrade "Unsafe Function Imports" to INFO or LOW unless specific bad usage is found
        if m.rule in ["Unsafe_String_Functions", "Unsafe_Memory_Functions"]:
            severity = "low"
            description += " (Note: Presence of function import does not guarantee exploitation)"

        if m.rule == "DLMS_COSEM_OBIS_Code_Pattern":
            valid_obis_found = False
            for string_match in m.strings:
                # older yara-python: string_match is a tuple (offset, identifier, data)
                # newer yara-python: string_match is an object with .instances
                instances = getattr(string_match, 'instances', [])
                if not instances and isinstance(string_match, tuple):
                    # handle older yara-python
                    string_data = string_match[2]
                    try:
                        decoded = string_data.decode("utf-8") if isinstance(string_data, bytes) else string_data
                        is_known, meaning = lookup_obis_meaning(decoded)
                        if is_known:
                            valid_obis_found = True
                            result["matches"].append({
                                "rule": "DLMS_COSEM_OBIS_Code_Known",
                                "cwe": None,
                                "severity": "high",
                                "description": f"OBIS code {decoded} found — {meaning}",
                                "action": m.meta.get("action"),
                            })
                    except Exception:
                        pass
                else:
                    # handle newer yara-python
                    for instance in instances:
                        string_data = instance.matched_data
                        try:
                            decoded = string_data.decode("utf-8") if isinstance(string_data, bytes) else string_data
                            is_known, meaning = lookup_obis_meaning(decoded)
                            if is_known:
                                valid_obis_found = True
                                result["matches"].append({
                                    "rule": "DLMS_COSEM_OBIS_Code_Known",
                                    "cwe": None,
                                    "severity": "high",
                                    "description": f"OBIS code {decoded} found — {meaning}",
                                    "action": m.meta.get("action"),
                                })
                        except Exception:
                            pass
            # If we appended high severity known codes, we still keep the original match but at info severity

        result["matches"].append({
            "rule": m.rule,
            "cwe": cwe,
            "severity": severity,
            "description": description,
            "action": m.meta.get("action"),
        })

    result["success"] = True
    return result