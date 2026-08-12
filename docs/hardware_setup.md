# Hardware-Assisted Testbed (Stage 5)

As part of the C3iHub FAWS project, this guide covers the setup for a **Hybrid Validation** testing bed using physical microcontroller boards (ESP32 / STM32). This bridges the gap between simulated function-level fuzzing and real-world network packet fuzzing.

## Prerequisites
1. **Hardware**: 
   - ESP32 Development Board (e.g., ESP-WROOM-32) OR
   - STM32 Nucleo Board (e.g., Nucleo-F429ZI) with Ethernet/Wi-Fi capability.
2. **Software**:
   - Arduino IDE or PlatformIO
   - [Gurux DLMS/COSEM Open Source Stack for C/C++](https://github.com/Gurux/GuruxDLMS.c)

## Setup Instructions

### 1. Flashing the DLMS Server
1. Clone the Gurux DLMS repository:
   ```bash
   git clone https://github.com/Gurux/GuruxDLMS.c.git
   ```
2. Open the `Arduino_IDE` example from the repository in the Arduino IDE.
3. Configure the network settings in the sketch (SSID and Password if using ESP32 Wi-Fi).
4. Select your target board and flash the firmware.
5. Note the assigned IP Address from the serial monitor (e.g., `192.168.1.100`).

### 2. Physical Port Configuration
The default DLMS/COSEM server listens on **TCP Port 4059**. Ensure your testing machine running FAWS is on the same local subnet as the board.

## Running the FAWS Network Fuzzer

Once the board is running the dummy DLMS meter firmware, you can use the FAWS CLI wrapper to execute the **Boofuzz State Machine Fuzzer** against it over the network.

```bash
# Execute Stage 5 Hybrid Validation
python faws.py network-fuzz --target 192.168.1.100
```

### What Happens During the Test?
1. `boofuzz_fuzzer.py` initializes a `Session` with the target IP address.
2. It sends mutated `AARQ` (Application Association Request) packets targeting the DLMS connection sequence.
3. It monitors the connection for crashes (connection resets, timeouts, or lack of response).
4. If a crash is detected, the fuzzing payload is logged to help identify buffer overflows in the physical firmware.

## Expanding the Testbed
To test other architectures (e.g., ARM Cortex-M0 vs ESP32's Xtensa), you can compile the same Gurux DLMS server for different boards and repeat the `network-fuzz` command. This ensures your static and dynamic findings from Stages 1-3 align with physical hardware limitations.
