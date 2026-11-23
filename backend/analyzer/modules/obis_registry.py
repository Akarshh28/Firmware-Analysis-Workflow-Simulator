"""
obis_registry.py - Static reference table of real, standardized OBIS codes.
"""

OBIS_CODE_REGISTRY = {
    "1.0.1.8.0.255": "Active energy import (A+) total",
    "1.0.2.8.0.255": "Active energy export (A-) total",
    "1.0.3.8.0.255": "Reactive energy import (Q+) total",
    "1.0.4.8.0.255": "Reactive energy export (Q-) total",
    "1.0.32.7.0.255": "Instantaneous voltage, L1",
    "1.0.52.7.0.255": "Instantaneous voltage, L2",
    "1.0.72.7.0.255": "Instantaneous voltage, L3",
    "1.0.31.7.0.255": "Instantaneous current, L1",
    "1.0.51.7.0.255": "Instantaneous current, L2",
    "1.0.71.7.0.255": "Instantaneous current, L3",
    "1.0.14.7.0.255": "Instantaneous supply frequency",
    "0.0.1.0.0.255":  "Clock / date-time object",
    "0.0.96.1.0.255": "Meter serial number",
    "0.0.96.1.1.255": "Manufacturer identification",
    "0.0.96.2.0.255": "Program/firmware version",
    "0.0.96.3.10.255": "Disconnect control (remote disconnect switch)",
    "0.0.96.11.0.255": "Power failure event counter",
    "0.0.96.11.1.255": "Power failure event log",
    "0.0.40.0.0.255": "Client SAP (Service Access Point) assignment",
    "0.0.42.0.0.255": "COSEM logical device name",
    "0.0.43.0.0.255": "Security setup object (Suite 0/1/2 configuration)",
    "0.0.44.0.0.255": "Image transfer object (firmware update via DLMS)",
}

def lookup_obis_meaning(obis_code_str: str):
    """
    Check a matched OBIS-shaped string against the real registry.
    Returns (is_known: bool, meaning: str | None).
    """
    normalized = obis_code_str.strip()
    if normalized in OBIS_CODE_REGISTRY:
        return True, OBIS_CODE_REGISTRY[normalized]
    return False, None
