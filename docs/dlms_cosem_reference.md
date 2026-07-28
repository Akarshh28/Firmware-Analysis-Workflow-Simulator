# DLMS/COSEM Protocol Security Reference

This reference is compiled for security researchers, students, and engineers analyzing smart meter firmware.

## 1. Protocol Architecture Overview

DLMS (Device Language Message Specification) / COSEM (Companion Specification for Energy Metering) is the global standard for smart utility meter data exchange.

*   **DLMS (Application Layer)**: Defines the messaging syntax and services.
*   **COSEM (Object Model)**: Defines the object-oriented structure representing meter data (registers, profiles, scheduling).
*   **OBIS (Object Identification System)**: Codes representing the physical quantities.

### Example OBIS Codes
- `1.0.1.8.0.255` -> Active Import Energy ($A+$) Total
- `1.0.2.8.0.255` -> Active Export Energy ($A-$) Total
- `1.0.31.7.0.255` -> Instantaneous L1 Current

---

## 2. DLMS/COSEM Security Suites

DLMS specifies security mechanisms categorized into three "Security Suites":

| Security Suite | Cryptographic Primitives | Key Sizes | Description |
| :--- | :--- | :--- | :--- |
| **Suite 0** | AES-GCM-128 / ECDSA P-256 | 128-bit symmetric / 256-bit asymmetric | Default modern utility security profile. |
| **Suite 1** | AES-GCM-256 / ECDSA P-384 | 256-bit symmetric / 384-bit asymmetric | High security. |
| **Suite 2** | AES-GCM-256 / ECDHE / ECDSA | 256-bit symmetric / 256-bit curves | Modern ephemeral key agreement suite. |

### Vulnerability Vector: Key Derivation & Management
Many smart meter firmware implementations suffer from:
1. **Hardcoded Security Keys**: The Master Key (System Title key) is burned directly in the raw binary.
2. **Weak Key Derivation Functions (KDF)**: Deriving keys from low-entropy inputs like the meter serial number or MAC address.
3. **Static Security Associations (LS/US)**: Low security (plain password) associations remaining active on telemetry ports, allowing unauthenticated firmware re-flashing.

---

## 3. Firmware Analysis Methodology for Smart Meters

Analyzing a smart meter firmware binary generally follows these chronological stages:

1.  **Entropy Analysis**: Scans for packed/encrypted code sections. Flat high-entropy suggests encryption (needs hardware keys), whereas local high-entropy suggests compressed assets (extractable).
2.  **Extraction**: Unpack the firmware container (`binwalk`, custom unpacking scripts).
3.  **Symbolic Execution & Decompilation**:
    *   Find the Association Request (AARQ) parser.
    *   Analyze the authentication state machine.
    *   Solve symbolic logic paths using `angr` to bypass checksum or signature checks.
4.  **Protocol Fuzzing**: Test the APDU (Application Protocol Data Unit) parsing engine for buffer overflows.
