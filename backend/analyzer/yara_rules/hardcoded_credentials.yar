/*
    Hardcoded Credentials / Authentication Weakness Detection Rules
    -------------------------------------------------------------------
    Purpose : Flag patterns associated with hardcoded credentials, verbose
              authentication error messages (username enumeration), and
              plaintext credential handling. Supports the "bypassable
              authentication" criterion in the Vulnerability Assessment
              Report deliverable.
    Project : Automated Firmware Analysis on DLMS/COSEM Protocol
*/

rule Plaintext_Password_In_Format_String
{
    meta:
        description = "Binary embeds the literal password value into a debug/log format string, risking plaintext credential exposure in logs"
        severity    = "high"
        reference   = "Observed in Relion670 (ppc670.x): 'ftpXfer: host:%s user:%s passwd:%s ...' and 'Failed to add FTP user %s with password %s'"
    strings:
        $fmt1 = "password:%s" nocase
        $fmt2 = "passwd:%s" nocase
        $fmt3 = "with password %s" nocase
        $fmt4 = "Failed to encrypt FTP passwd" nocase
    condition:
        any of them
}

rule Verbose_Authentication_Errors
{
    meta:
        description = "Binary distinguishes 'wrong password' from 'user not found' style errors, which can enable username enumeration if surfaced over the network"
        severity    = "medium"
    strings:
        $wrong_pw   = "wrong Password" nocase
        $not_found  = "not found" nocase
        $wrong_user = "Wrong old password" nocase
        $login_incorrect = "Login incorrect" nocase
    condition:
        2 of them
}

rule Legacy_Debug_Login_Shell
{
    meta:
        description = "Binary contains a legacy VxWorks-style debug login/shell interface (rlogin/iam), which historically lacks modern authentication hardening"
        severity    = "medium"
        reference   = "Observed in Relion670 (ppc670.x): '<VxWorks login:', 'iam \"user\"[,\"passwd\"]', rlogin command help text"
    strings:
        $vxworks_login = "VxWorks login" nocase
        $iam_cmd       = "iam" fullword
        $rlogin        = "rlogin" fullword
        $shell_login   = "shellLogin"
    condition:
        2 of them
}

rule Hardcoded_Credential_Keywords
{
    meta:
        description = "Generic scan for hardcoded credential / default-account keywords worth manual review"
        severity    = "low"
        note        = "High false-positive rate by design - intended as a broad triage signal, not a standalone finding"
    strings:
        $default_pw   = "default password" nocase
        $default_cred = "default credential" nocase
        $admin_pw     = "admin123" nocase
        $root_pw      = "toor" nocase
        $factory_pw   = "factory default" nocase
    condition:
        any of them
}

rule Authentication_Weakness_Combined_Flag
{
    meta:
        description = "Consolidated authentication-weakness verdict for report generation"
        severity    = "high"
        action      = "Flag in Vulnerability Assessment Report under 'Bypassable / Weak Authentication'"
    condition:
        Plaintext_Password_In_Format_String or Legacy_Debug_Login_Shell or Hardcoded_Credential_Keywords
}
