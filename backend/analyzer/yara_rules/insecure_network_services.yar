/*
    Insecure Legacy Network Service Detection Rules
    ----------------------------------------------------
    Purpose : Identify unencrypted or weakly-authenticated legacy network
              services embedded in the firmware, establishing the device's
              network attack surface. Supports the Vulnerability Assessment
              Report's network-exposure findings.
    Project : Automated Firmware Analysis on DLMS/COSEM Protocol
*/

rule FTP_Server_Present
{
    meta:
        description = "Firmware includes a built-in FTP server (unencrypted file transfer and authentication)"
        severity    = "high"
        reference   = "Observed in Relion670 (ppc670.x): ftpdTask, 'VxWorks (%s) FTP server ready'"
    strings:
        $ftpd_task = "ftpdTask"
        $ftp_ready = "FTP server ready" nocase
        $ftp_sec   = "FTP server security" nocase
    condition:
        any of them
}

rule TFTP_Service_Present
{
    meta:
        description = "Firmware includes TFTP client/server functionality - TFTP has no authentication by protocol design"
        severity    = "high"
        reference   = "Observed in Relion670 (ppc670.x): tftpGet, tftpPut, tftpXfer"
    strings:
        $tftp_get  = "tftpGet"
        $tftp_put  = "tftpPut"
        $tftp_xfer = "tftpXfer"
        $tftp_task = "tftpTask"
    condition:
        any of them
}

rule Legacy_SNMP_Present
{
    meta:
        description = "Firmware includes SNMP support - v1/v2c SNMP uses weak community-string authentication"
        severity    = "medium"
        reference   = "Observed in Relion670 (ppc670.x): COM581_SNMP_SUPPORT"
    strings:
        $snmp_support = "SNMP_SUPPORT"
        $snmp_generic = "SNMP" fullword
    condition:
        any of them
}

rule No_Encrypted_Management_Protocol
{
    meta:
        description = "Firmware shows insecure management protocols (FTP/TFTP/SNMP) with no evidence of HTTPS or SSH strings - indicates reliance on unencrypted channels for management/update"
        severity    = "high"
        note        = "This rule expresses an absence-based heuristic; confirm manually before reporting, since encrypted service strings may be stored differently (e.g. inside a compressed/encrypted region)"
    strings:
        $https = "https" nocase
        $ssh   = "SSH-2.0" nocase
    condition:
        (FTP_Server_Present or TFTP_Service_Present or Legacy_SNMP_Present)
        and not (
            $https or $ssh
        )
}

rule Insecure_Network_Services_Combined_Flag
{
    meta:
        description = "Consolidated insecure-network-service verdict for report generation"
        severity    = "high"
        action      = "Flag in Vulnerability Assessment Report under 'Insecure Network Protocol Usage'"
    condition:
        FTP_Server_Present or TFTP_Service_Present or Legacy_SNMP_Present
}
