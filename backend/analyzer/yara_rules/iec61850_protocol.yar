/*
    IEC 61850 Protocol Detection Rules
    ------------------------------------
    Purpose : Identify IEC 61850 (GOOSE/MMS/RCB) implementations in relay
              firmware. Used as a comparison/exclusion signal against
              DLMS/COSEM - protection relays frequently implement IEC 61850
              instead of DLMS/COSEM, and this rule set helps the automation
              pipeline correctly label such firmware rather than misreading
              the shared ACSE layer as DLMS/COSEM.
    Project : Automated Firmware Analysis on DLMS/COSEM Protocol
*/

rule IEC61850_Stack_Present
{
    meta:
        description = "Firmware contains a compiled IEC 61850 communication stack"
        confidence  = "high"
        reference   = "Observed in Hitachi/ABB Relion670 (ppc670.x)"
    strings:
        $iec61850_lit = "IEC61850-8-1"
        $iec61850_gen = "IEC61850" nocase
        $goose        = "GOOSE" nocase
        $mms_pdu      = "MMS PDU" nocase
        $rcb          = "Report Control Block" nocase
        $read_dai     = "Read_IEC61850_DAI"
        $write_dai    = "Write_IEC61850_DAI"
    condition:
        3 of them
}

rule IEC61850_Without_DLMS
{
    meta:
        description = "Firmware implements IEC 61850 and shows no DLMS/COSEM-specific evidence - classify as IEC 61850 device, not a DLMS/COSEM target"
        confidence  = "high"
        action      = "Exclude from Phase 3 DLMS/COSEM-specific testing; retain as comparison sample"
    condition:
        IEC61850_Stack_Present
}
