/*
    DLMS/COSEM Protocol Detection Rules
    ------------------------------------
    Purpose : Identify whether a firmware binary implements the DLMS/COSEM
              metering protocol, and distinguish genuine implementations
              from firmware that only shares the underlying ACSE
              association layer (e.g. IEC 61850 MMS).
    Project : Automated Firmware Analysis on DLMS/COSEM Protocol
    Author  : Internship project - firmware security analysis
*/

import "math"

rule DLMS_COSEM_Literal_Strings
{
    meta:
        description = "Firmware contains explicit DLMS or COSEM literal strings"
        confidence  = "high"
        reference   = "IEC 62056 / DLMS UA specification"
    strings:
        $dlms  = "DLMS" nocase
        $cosem = "COSEM" nocase
        $iec62056 = "IEC 62056" nocase
        $iec62056b = "IEC62056" nocase
    condition:
        any of them
}

rule DLMS_COSEM_OBIS_Code_Pattern
{
    meta:
        description = "Binary contains OBIS-code-shaped strings (A.B.C.D.E.F), the DLMS/COSEM object naming scheme"
        confidence  = "high"
        note        = "Matches dotted 6-group numeric patterns such as 1.0.1.8.0.255"
    strings:
        $obis = /[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/
    condition:
        $obis
}

rule DLMS_COSEM_Service_Primitives
{
    meta:
        description = "Binary contains DLMS/COSEM application-layer service primitive names (GET/SET/ACTION)"
        confidence  = "high"
    strings:
        $get_req    = "GET-REQUEST" nocase
        $get_resp   = "GET-RESPONSE" nocase
        $set_req    = "SET-REQUEST" nocase
        $set_resp   = "SET-RESPONSE" nocase
        $action_req = "ACTION-REQUEST" nocase
        $action_resp = "ACTION-RESPONSE" nocase
    condition:
        2 of them
}

rule ACSE_Association_Layer_Generic
{
    meta:
        description = "Binary implements the ACSE association layer (AARQ/AARE/RLRQ/RLRE/ABRT). This layer is shared by DLMS/COSEM and IEC 61850 MMS - match alone does NOT confirm DLMS/COSEM. Combine with DLMS_COSEM_* rules or exclude with IEC61850 rules to disambiguate."
        confidence  = "medium"
        note        = "Observed in Relion670 firmware (ppc670.x) where it belonged to IEC 61850 MMS, not DLMS/COSEM"
    strings:
        $aarq = "AARQ" nocase
        $aare = "AARE" nocase
        $rlrq = "RLRQ" nocase
        $rlre = "RLRE" nocase
        $decode_aarq = "decode_aarq"
        $decode_aare = "decode_aare"
        $aarq_apdu   = "aarq_apdu"
        $aare_apdu   = "aare_apdu"
    condition:
        3 of them
}

rule DLMS_COSEM_Security_Suite_Indicators
{
    meta:
        description = "Binary references DLMS Security Suite mechanisms (AES-GCM, ECDSA) used for authenticated/encrypted DLMS sessions"
        confidence  = "medium"
        reference   = "DLMS UA Green Book - Security Suite 0/1/2"
    strings:
        $aes_gcm = "AES-GCM" nocase
        $aesgcm  = "AESGCM" nocase
        $ecdsa   = "ECDSA" nocase
        $suite0  = "Security Suite 0" nocase
        $suite1  = "Security Suite 1" nocase
        $suite2  = "Security Suite 2" nocase
    condition:
        any of them
}

rule DLMS_COSEM_Confirmed_Implementation
{
    meta:
        description = "High-confidence verdict: firmware genuinely implements DLMS/COSEM (not just a shared ACSE layer)"
        confidence  = "high"
        action      = "Proceed to Phase 3 protocol-specific testing (OBIS mapping, security suite verification, APDU fuzzing)"
    condition:
        DLMS_COSEM_Literal_Strings or
        (DLMS_COSEM_OBIS_Code_Pattern and DLMS_COSEM_Service_Primitives) or
        (ACSE_Association_Layer_Generic and DLMS_COSEM_OBIS_Code_Pattern)
}
