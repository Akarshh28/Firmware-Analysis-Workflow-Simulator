import re

# Production-grade DLMS/COSEM OBIS Code Parser (IEC 62056-61)
# OBIS Code Format: A.B.C.D.E.F

class OBISParser:
    OBIS_REGEX = re.compile(r'\b(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})\b')

    # Value Group A: Medium
    MEDIUMS = {
        0: "Abstract",
        1: "Electricity",
        4: "Heat Cost Allocator",
        5: "Cooling",
        6: "Heat",
        7: "Gas",
        8: "Cold Water",
        9: "Hot Water",
    }

    # Value Group C for Electricity (A=1) - Measurement Purpose
    ELEC_MEASUREMENTS = {
        1: "Active Energy Import (+A)",
        2: "Active Energy Export (-A)",
        3: "Reactive Energy Import (+R)",
        4: "Reactive Energy Export (-R)",
        9: "Apparent Energy Import (+VA)",
        10: "Apparent Energy Export (-VA)",
        13: "Power Factor",
        14: "Supply Frequency",
        31: "L1 Current",
        32: "L1 Voltage",
        51: "L2 Current",
        52: "L2 Voltage",
        71: "L3 Current",
        72: "L3 Voltage",
        91: "Neutral Current",
        94: "Total Active Power"
    }
    
    # Abstract Objects (A=0)
    ABSTRACT_OBJECTS = {
        (96, 1): "Device ID / Serial Number",
        (96, 2): "Configuration Changes Count",
        (96, 3): "Firmware Version",
        (96, 5): "Hardware Version",
        (96, 50): "Tamper/Fraud Status",
        (97, 97): "Error Register"
    }

    @classmethod
    def parse(cls, code_str: str) -> dict:
        """
        Parses an OBIS code string and returns its semantic meaning and access level.
        """
        parts = code_str.split('.')
        if len(parts) != 6:
            return {"name": "Invalid Code", "access": "Unknown"}

        try:
            a, b, c, d, e, f = map(int, parts)
        except ValueError:
            return {"name": "Invalid Formatting", "access": "Unknown"}

        name = "Unknown Object"
        access = "Read" # Default heuristic

        # Parse Group A=0 (Abstract objects like Device ID, Errors)
        if a == 0:
            name = cls.ABSTRACT_OBJECTS.get((c, d), f"Abstract Object (Group C={c}, D={d})")
            if c == 96 and d == 2:
                access = "Read/Write" # Configurations are often writeable
        
        # Parse Group A=1 (Electricity)
        elif a == 1:
            measurement = cls.ELEC_MEASUREMENTS.get(c, f"Electricity Metric {c}")
            
            # Group D: Processing type (Time integral, Maximum, etc.)
            processing = ""
            if d == 8:
                processing = " (Time Integral)"
            elif d == 7:
                processing = " (Instantaneous)"
            elif d == 2:
                processing = " (Cumulative Maximum)"
            elif d == 6:
                processing = " (Maximum)"

            # Group E: Tariff
            tariff = f" Tariff {e}" if e > 0 else " Total"

            name = f"{measurement}{processing}{tariff}"
            access = "Read"

        else:
            medium = cls.MEDIUMS.get(a, f"Medium {a}")
            name = f"{medium} Object (C={c}, D={d})"

        return {
            "code": code_str,
            "name": name,
            "access": access
        }

    @classmethod
    def extract_from_text(cls, text: str) -> list:
        """
        Extracts all valid OBIS codes from a text block and parses their meaning.
        """
        matches = cls.OBIS_REGEX.findall(text)
        codes = []
        for match in matches:
            code_str = ".".join(match)
            parsed = cls.parse(code_str)
            codes.append(parsed)
        return codes

if __name__ == "__main__":
    # Test cases
    print(OBISParser.parse("1.0.1.8.0.255"))
    print(OBISParser.parse("1.0.32.7.0.255"))
    print(OBISParser.parse("0.0.96.1.0.255"))
    print(OBISParser.parse("7.0.3.8.0.255"))
