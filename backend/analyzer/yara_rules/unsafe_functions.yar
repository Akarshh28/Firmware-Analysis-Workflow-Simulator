/*
    Unsafe Function Usage Detection Rules
    ----------------------------------------
    Purpose : Flag calls to C standard library functions historically
              associated with buffer overflows and memory-corruption
              vulnerabilities. Supports denial-of-service / memory-safety
              findings in the Vulnerability Assessment Report deliverable.
    Project : Automated Firmware Analysis on DLMS/COSEM Protocol
*/

rule Unsafe_String_Functions
{
    meta:
        description = "Binary calls unbounded string functions prone to buffer overflow"
        severity    = "high"
        reference   = "strcpy confirmed present in Relion670 (ppc670.x) via disassembly at LioBackDoorListNode constructor"
    strings:
        $strcpy  = "strcpy" fullword
        $strcat  = "strcat" fullword
        $sprintf = "sprintf" fullword
        $gets    = "gets" fullword
        $vsprintf = "vsprintf" fullword
    condition:
        any of them
}

rule Unsafe_Memory_Functions
{
    meta:
        description = "Binary calls raw memory-copy functions without visible bounds context (manual review needed to confirm length validation)"
        severity    = "medium"
    strings:
        $memcpy  = "memcpy" fullword
        $memmove = "memmove" fullword
        $bcopy   = "bcopy" fullword
    condition:
        any of them
}

rule Unsafe_Format_String_Risk
{
    meta:
        description = "Binary uses printf-family functions with externally influenced format strings possible (manual review needed at each call site)"
        severity    = "medium"
    strings:
        $printf  = "printf" fullword
        $fprintf = "fprintf" fullword
        $syslog  = "syslog" fullword
    condition:
        any of them
}

rule Unsafe_Functions_Combined_Flag
{
    meta:
        description = "Consolidated unsafe-function-usage verdict for report generation"
        severity    = "high"
        action      = "Flag in Vulnerability Assessment Report under 'Potential Buffer Overflow / DoS' - cross-reference disassembly to confirm exploitability"
    condition:
        Unsafe_String_Functions or Unsafe_Memory_Functions
}
