"""
config.py - Central configuration for the firmware analysis pipeline.

Keeping every keyword list / threshold / mapping in one file makes it easy
to extend the tool for a new device (REB500, REX670, GE, Siemens, ...)
without touching the pipeline logic itself.
"""

# --- Recursion / extraction limits -----------------------------------------
MAX_RECURSION_DEPTH = 6          # how deep to unpack nested archives
MAX_FILE_SIZE_FOR_ENTROPY = 200 * 1024 * 1024   # 200 MB safety cap

# --- File types we recognise as "not firmware" (skip analysis, just log) ---
DOCUMENT_EXTENSIONS = {".pdf", ".xlsx", ".xls", ".docx", ".png", ".jpg",
                        ".jpeg", ".txt", ".ini", ".cfg", ".xml", ".csv"}

# --- Archive / container extractors ----------------------------------------
# Each entry: file-command substring -> handler name used in extractor.py
CONTAINER_SIGNATURES = {
    "Zip archive data": "zip",
    "MSI Installer": "msi",
    "Composite Document File": "msi",
    "Microsoft Cabinet archive data": "cab",
    "gzip compressed data": "gzip",
    "tar archive": "tar",
}

# --- Keyword categories for the strings scan --------------------------------
KEYWORD_CATEGORIES = {
    "dlms_cosem": [
        r"\bDLMS\b", r"\bCOSEM\b", r"IEC[\s_-]?62056",
        r"GET-REQUEST", r"SET-REQUEST", r"ACTION-REQUEST",
        r"\bOBIS\b",
    ],
    "iec61850": [
        r"IEC[\s_-]?61850", r"\bGOOSE\b", r"\bMMS\b(?!\w)",
        r"Report Control Block", r"IEC61850_DAI",
    ],
    "acse_association": [
        r"\bAARQ\b", r"\bAARE\b", r"\bRLRQ\b", r"\bRLRE\b",
        r"decode_aarq", r"decode_aare",
    ],
    "weak_crypto": [
        r"\bMD5\b", r"\bSHA1\b", r"\bDES\b", r"\bRC4\b",
        r"md5\.cpp", r"weak", r"deprecated",
    ],
    "unsafe_functions": [
        r"\bstrcpy\b", r"\bstrcat\b", r"\bsprintf\b", r"\bgets\b",
        r"\bmemcpy\b", r"\bmemmove\b",
    ],
    "auth_credentials": [
        r"password", r"passwd", r"\blogin\b", r"\badmin\b",
        r"backdoor", r"debug.?mode", r"default.?cred", r"hardcode",
    ],
    "network_services": [
        r"\bftp\b", r"\btelnet\b", r"\bhttp\b", r"\bsnmp\b",
        r"\bssh\b", r"\btftp\b",
    ],
    "rtos_platform": [
        r"VxWorks", r"FreeRTOS", r"WIND kernel", r"Wind River",
    ],
}

# Symbols worth pulling out of the symbol table and disassembling
# individually once flagged by the strings/YARA pass. Matched
# case-insensitively as substrings against symbol names.
SUSPICIOUS_SYMBOL_KEYWORDS = [
    "backdoor", "bypass", "debug", "hidden", "telnet",
    "unsafe", "secret",
    "strcpy", "strcat", "sprintf", "gets", "memcpy",
]

# Max number of symbols to auto-disassemble per binary (safety cap so the
# pipeline can't get stuck trying to disassemble thousands of matches).
MAX_SYMBOLS_TO_DISASSEMBLE = 25

# Max bytes of a single function to disassemble (safety cap).
MAX_FUNCTION_DISASSEMBLE_SIZE = 4096

# --- Architecture -> cross-objdump binary mapping ---------------------------
# 'file' command output substring -> objdump binary to use.
# Extend this table as new architectures are encountered.
ARCH_OBJDUMP_MAP = [
    ("PowerPC", "powerpc-linux-gnu-objdump"),
    ("ARM",     "arm-linux-gnueabi-objdump"),
    ("MIPS",    "mips-linux-gnu-objdump"),
    ("x86-64",  "objdump"),
    ("Intel 80386", "objdump"),
]

# --- Entropy thresholds ------------------------------------------------------
ENTROPY_WINDOW_SIZE = 4096       # bytes per sliding-window sample
ENTROPY_HIGH_THRESHOLD = 7.5     # out of 8.0 - above this = likely compressed/encrypted
ENTROPY_MIN_RUN_WINDOWS = 8      # need this many consecutive high-entropy windows to flag a region
