/*
    RTOS / Platform Identification Rules
    ----------------------------------------
    Purpose : Establish execution context (RTOS, architecture) for a
              firmware sample early in the automated pipeline, so later
              rules and reporting can be scoped correctly. This is a
              triage layer, not a vulnerability signal by itself.
    Project : Automated Firmware Analysis on DLMS/COSEM Protocol
*/

rule RTOS_VxWorks
{
    meta:
        description = "Firmware runs on VxWorks RTOS"
        confidence  = "high"
        reference   = "Observed in Relion670 (ppc670.x): 'VxWorks operating system version', WIND kernel string"
    strings:
        $vxworks     = "VxWorks" fullword
        $wind_kernel = "WIND kernel" nocase
        $wind_river  = "Wind River Systems" nocase
    condition:
        any of them
}

rule RTOS_FreeRTOS
{
    meta:
        description = "Firmware runs on FreeRTOS - relevant for future ESP32/STM32-based DLMS test targets"
        confidence  = "high"
    strings:
        $freertos = "FreeRTOS" nocase
        $tskIdle  = "vTaskDelay"
    condition:
        any of them
}

rule Architecture_PowerPC
{
    meta:
        description = "Firmware targets PowerPC architecture"
        confidence  = "medium"
    strings:
        $ppc1 = "PowerPC" nocase
        $ppc2 = "PPC" fullword
    condition:
        any of them
}

rule Vendor_ABB_Hitachi
{
    meta:
        description = "Firmware carries ABB / Hitachi Energy authorship/copyright strings"
        confidence  = "high"
        reference   = "Observed in Relion670: 'Copyright (c) 2004 ABB Automation Ltd.', 'ABB Power Technologies AB'"
    strings:
        $abb1 = "ABB Automation" nocase
        $abb2 = "ABB Power Technologies" nocase
        $abb3 = "Hitachi Energy" nocase
        $abb4 = "ABB Asea Brown Boveri" nocase
    condition:
        any of them
}
