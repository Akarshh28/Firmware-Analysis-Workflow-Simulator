/*
    Weak / Deprecated Cryptography Detection Rules
    ------------------------------------------------
    Purpose : Flag use of cryptographic algorithms considered weak or
              broken by modern standards. Directly supports the
              "weak cryptographic storage" criterion in the project's
              Vulnerability Assessment Report deliverable.
    Project : Automated Firmware Analysis on DLMS/COSEM Protocol
*/

rule Weak_Hash_MD5
{
    meta:
        description = "Firmware compiles in MD5, a cryptographically broken hash algorithm (collision attacks known)"
        severity    = "high"
        reference   = "Observed in Relion670 (ppc670.x) via embedded md5.cpp source string"
    strings:
        $md5_src   = "md5.cpp" nocase
        $md5_name  = "MD5" fullword
        $md5_func  = "MD5Update"
        $md5_init  = "MD5Init"
        $md5_final = "MD5Final"
    condition:
        any of them
}

rule Weak_Hash_SHA1
{
    meta:
        description = "Firmware references SHA1, a deprecated hash algorithm (practical collisions demonstrated since 2017)"
        severity    = "medium"
        reference   = "Observed in Relion670 (ppc670.x) via SHA1 OCTET strings"
    strings:
        $sha1_name  = "SHA1" fullword
        $sha1_octet = "SHA1" nocase
        $sha1_init  = "SHA1Init"
        $sha1_final = "SHA1Final"
    condition:
        any of them
}

rule Weak_Cipher_DES_RC4
{
    meta:
        description = "Firmware references DES or RC4, both considered cryptographically weak/broken"
        severity    = "high"
    strings:
        $des  = "DES" fullword
        $des3 = "3DES" fullword
        $rc4  = "RC4" fullword
        $rc4_ks = "RC4_set_key"
    condition:
        any of them
}

rule Weak_Random_Number_Generation
{
    meta:
        description = "Firmware uses predictable/non-cryptographic random number generators (rand/srand) where secure randomness may be required (e.g. session tokens, nonces)"
        severity    = "medium"
    strings:
        $rand  = "rand" fullword
        $srand = "srand" fullword
        $random = "random" fullword
    condition:
        2 of them
}

rule Deprecated_Crypto_Combined_Flag
{
    meta:
        description = "Consolidated weak-cryptography verdict for report generation"
        severity    = "high"
        action      = "Flag in Vulnerability Assessment Report under 'Weak Cryptographic Storage'"
    condition:
        Weak_Hash_MD5 or Weak_Hash_SHA1 or Weak_Cipher_DES_RC4
}
