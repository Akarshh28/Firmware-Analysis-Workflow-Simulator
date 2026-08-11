# Firmware Analysis Report

Generated: 2026-08-10T14:09:13.379009+00:00

Total files processed: 79

## Summary

| File | Status | Protocol Verdict | YARA High-Severity Hits |
|---|---|---|---|
| Firmware-Update Details.xlsx | skipped: recognized non-firmware document type (pdf/xlsx/png/etc.) - not analyzed | - | - |
| 363340 | ok: unrecognized/non-executable file type ('PC bitmap, Windows 3.x format, 493 x 58 x 8, 1 compression, image size 1668, resolution 3780 x 3780 px/m, 256 important colors, cbSize 2746, bits offset 1078') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected. | - | - |
| 366000 | ok: leaf binary ready for analysis | - | - |
| 37D660 | ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected. | - | - |
| 380000 | ok: unrecognized/non-executable file type ('PC bitmap, Windows 3.x format, 166 x 345 x 24, image size 172500, resolution 3780 x 3780 px/m, cbSize 172554, bits offset 54') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected. | - | - |
| 3B418D | ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected. | - | - |
| 3B4C66 | ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected. | - | - |
| 3B5B00 | ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected. | - | - |
| 3B81B6 | ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected. | - | - |
| 3B81D2 | ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected. | - | - |
| 3B81F0 | ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected. | - | - |
| 3B820A | ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected. | - | - |
| 3B8221 | ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected. | - | - |
| 3B9000 | ok: unrecognized/non-executable file type ('DER Encoded PKCS#7 Signed Data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected. | - | - |
| 3B9094 | ok: unrecognized/non-executable file type ('Certificate, Version=3') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected. | - | - |
| 3B9596 | ok: unrecognized/non-executable file type ('Certificate, Version=3') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected. | - | - |
| 3B9ACB | ok: unrecognized/non-executable file type ('Certificate, Version=3') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected. | - | - |
| 3BA17F | ok: unrecognized/non-executable file type ('Certificate, Version=3') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected. | - | - |
| 5000 | error: cab extraction failed: exit code 1: /tmp/fw_analysis_qhn9uciz/FST 2.3.13.0.msi_extracted/_FST 2.3.13.0.msi.extracted/5000: WARNING; possible 358553 extra bytes at end of file.
/tmp/fw_analysis_qhn9uciz/5000_extracted/_1MRG028040_Field_Service_Tool_Instruction.pdf: checksum error
/tmp/fw_analysis_qhn9uciz/5000_extracted/DelZip192.dll:  | - | - |
| Field_Service_Tool_instruction.pdf | skipped: recognized non-firmware document type (pdf/xlsx/png/etc.) - not analyzed | - | - |
| ShortProcedure.png | skipped: recognized non-firmware document type (pdf/xlsx/png/etc.) - not analyzed | - | - |
| 1A00 | ok: unrecognized/non-executable file type ('PC bitmap, Windows 3.x format, 158 x 323 x 32, image size 204138, resolution 2834 x 2834 px/m, cbSize 204192, bits offset 54') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected. | - | - |
| _1MRG031502_FST_670_1.1_update.pdf | skipped: recognized non-firmware document type (pdf/xlsx/png/etc.) - not analyzed | - | - |
| oneshot.txt | skipped: recognized non-firmware document type (pdf/xlsx/png/etc.) - not analyzed | - | - |
| package.ini | skipped: recognized non-firmware document type (pdf/xlsx/png/etc.) - not analyzed | - | - |
| ppc670.x | ok: leaf binary ready for analysis | - | - |
| ppc670.x1 | ok: leaf binary ready for analysis | - | - |
| prebase.txt | skipped: recognized non-firmware document type (pdf/xlsx/png/etc.) - not analyzed | - | - |
| productdef.xml | skipped: recognized non-firmware document type (pdf/xlsx/png/etc.) - not analyzed | - | - |
| update.cfg | skipped: recognized non-firmware document type (pdf/xlsx/png/etc.) - not analyzed | - | - |
| 90BD00 | ok: unrecognized/non-executable file type ('PC bitmap, Windows 3.x format, 35 x 35 x 4, image size 700, resolution 3780 x 3780 px/m, cbSize 818, bits offset 118') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected. | - | - |
| 90EB42 | ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected. | - | - |
| 90FC2F | ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected. | - | - |
| 90FC41 | ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected. | - | - |
| 910CD1 | ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected. | - | - |
| 910FF8 | ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected. | - | - |
| 912073 | ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected. | - | - |
| 912094 | ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected. | - | - |
| 91212D | ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected. | - | - |
| 9124DA | ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected. | - | - |
| 912586 | ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected. | - | - |
| 9125A3 | ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected. | - | - |
| 91826E | ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected. | - | - |
| 91828B | ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected. | - | - |
| 9182A7 | ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected. | - | - |
| 9182C2 | ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected. | - | - |
| 9182D6 | ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected. | - | - |
| 9188C8 | ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected. | - | - |
| 9188F2 | ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected. | - | - |
| 918918 | ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected. | - | - |
| 91D62A | ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected. | - | - |
| 924A00 | ok: unrecognized/non-executable file type ('PC bitmap, Windows 3.x format, 500 x 63 x 8, 1 compression, image size 3072, resolution 3779 x 3779 px/m, 255 important colors, cbSize 4132, bits offset 1074') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected. | - | - |
| 925C00 | ok: leaf binary ready for analysis | - | - |
| 927008 | ok: unrecognized/non-executable file type ('DER Encoded PKCS#7 Signed Data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected. | - | - |
| 92709D | ok: unrecognized/non-executable file type ('Certificate, Version=3') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected. | - | - |
| 927560 | ok: unrecognized/non-executable file type ('Certificate, Version=3') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected. | - | - |
| 9275F6 | ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected. | - | - |
| 928200 | ok: leaf binary ready for analysis | - | - |
| 931608 | ok: unrecognized/non-executable file type ('DER Encoded PKCS#7 Signed Data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected. | - | - |
| 93169D | skipped: duplicate content, identical to already-analyzed file '/tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/92709D' | - | - |
| 931B60 | skipped: duplicate content, identical to already-analyzed file '/tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/927560' | - | - |
| 931BF6 | ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected. | - | - |
| 932400 | ok: leaf binary ready for analysis | - | - |
| 938008 | ok: unrecognized/non-executable file type ('DER Encoded PKCS#7 Signed Data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected. | - | - |
| 93809D | skipped: duplicate content, identical to already-analyzed file '/tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/92709D' | - | - |
| 938560 | skipped: duplicate content, identical to already-analyzed file '/tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/927560' | - | - |
| 9385F6 | ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected. | - | - |
| 93A400 | ok: unrecognized/non-executable file type ('DER Encoded PKCS#7 Signed Data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected. | - | - |
| 93A494 | ok: unrecognized/non-executable file type ('Certificate, Version=3') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected. | - | - |
| 93A886 | ok: unrecognized/non-executable file type ('Certificate, Version=3') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected. | - | - |
| 93AD2D | ok: unrecognized/non-executable file type ('Certificate, Version=3') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected. | - | - |
| 93B261 | ok: unrecognized/non-executable file type ('Certificate, Version=3') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected. | - | - |
| _1MRG031502_FST_670_1.1_update.pdf | skipped: recognized non-firmware document type (pdf/xlsx/png/etc.) - not analyzed | - | - |
| oneshot.txt | skipped: recognized non-firmware document type (pdf/xlsx/png/etc.) - not analyzed | - | - |
| package.ini | skipped: recognized non-firmware document type (pdf/xlsx/png/etc.) - not analyzed | - | - |
| ppc670.x | skipped: duplicate content, identical to already-analyzed file '/tmp/fw_analysis_qhn9uciz/48E00.cab_extracted/ppc670.x' | - | - |
| ppc670.x1 | skipped: duplicate content, identical to already-analyzed file '/tmp/fw_analysis_qhn9uciz/48E00.cab_extracted/ppc670.x1' | - | - |
| prebase.txt | skipped: recognized non-firmware document type (pdf/xlsx/png/etc.) - not analyzed | - | - |
| update.cfg | skipped: recognized non-firmware document type (pdf/xlsx/png/etc.) - not analyzed | - | - |

## File Details

### /tmp/fw_analysis_qhn9uciz/34_Relion670_Firmware update 1p1r01 to 27.zip_extracted/Firmware-Update Details.xlsx

- **File type:** Microsoft Excel 2007+
- **Extraction status:** skipped: recognized non-firmware document type (pdf/xlsx/png/etc.) - not analyzed

### /tmp/fw_analysis_qhn9uciz/FST 2.3.13.0.msi_extracted/_FST 2.3.13.0.msi.extracted/363340

- **File type:** PC bitmap, Windows 3.x format, 493 x 58 x 8, 1 compression, image size 1668, resolution 3780 x 3780 px/m, 256 important colors, cbSize 2746, bits offset 1078
- **Extraction status:** ok: unrecognized/non-executable file type ('PC bitmap, Windows 3.x format, 493 x 58 x 8, 1 compression, image size 1668, resolution 3780 x 3780 px/m, 256 important colors, cbSize 2746, bits offset 1078') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected.
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** objdump -t failed: objdump: /tmp/fw_analysis_qhn9uciz/FST 2.3.13.0.msi_extracted/_FST 2.3.13.0.msi.extracted/363340: file format not recognized

### /tmp/fw_analysis_qhn9uciz/FST 2.3.13.0.msi_extracted/_FST 2.3.13.0.msi.extracted/366000

- **File type:** PE32 executable (DLL) (GUI) Intel 80386, for MS Windows, 5 sections
- **Extraction status:** ok: leaf binary ready for analysis
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** symbol table extraction ran but found no symbols - the binary may be stripped (no debug/function names available)

### /tmp/fw_analysis_qhn9uciz/FST 2.3.13.0.msi_extracted/_FST 2.3.13.0.msi.extracted/37D660

- **File type:** data
- **Extraction status:** ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected.
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** objdump -t failed: objdump: /tmp/fw_analysis_qhn9uciz/FST 2.3.13.0.msi_extracted/_FST 2.3.13.0.msi.extracted/37D660: file format not recognized

### /tmp/fw_analysis_qhn9uciz/FST 2.3.13.0.msi_extracted/_FST 2.3.13.0.msi.extracted/380000

- **File type:** PC bitmap, Windows 3.x format, 166 x 345 x 24, image size 172500, resolution 3780 x 3780 px/m, cbSize 172554, bits offset 54
- **Extraction status:** ok: unrecognized/non-executable file type ('PC bitmap, Windows 3.x format, 166 x 345 x 24, image size 172500, resolution 3780 x 3780 px/m, cbSize 172554, bits offset 54') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected.
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** objdump -t failed: objdump: /tmp/fw_analysis_qhn9uciz/FST 2.3.13.0.msi_extracted/_FST 2.3.13.0.msi.extracted/380000: file format not recognized

### /tmp/fw_analysis_qhn9uciz/FST 2.3.13.0.msi_extracted/_FST 2.3.13.0.msi.extracted/3B418D

- **File type:** data
- **Extraction status:** ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected.
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** objdump -t failed: objdump: /tmp/fw_analysis_qhn9uciz/FST 2.3.13.0.msi_extracted/_FST 2.3.13.0.msi.extracted/3B418D: file format not recognized

### /tmp/fw_analysis_qhn9uciz/FST 2.3.13.0.msi_extracted/_FST 2.3.13.0.msi.extracted/3B4C66

- **File type:** data
- **Extraction status:** ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected.
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** objdump -t failed: objdump: /tmp/fw_analysis_qhn9uciz/FST 2.3.13.0.msi_extracted/_FST 2.3.13.0.msi.extracted/3B4C66: file format not recognized

### /tmp/fw_analysis_qhn9uciz/FST 2.3.13.0.msi_extracted/_FST 2.3.13.0.msi.extracted/3B5B00

- **File type:** data
- **Extraction status:** ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected.
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** objdump -t failed: objdump: /tmp/fw_analysis_qhn9uciz/FST 2.3.13.0.msi_extracted/_FST 2.3.13.0.msi.extracted/3B5B00: file format not recognized

### /tmp/fw_analysis_qhn9uciz/FST 2.3.13.0.msi_extracted/_FST 2.3.13.0.msi.extracted/3B81B6

- **File type:** data
- **Extraction status:** ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected.
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** objdump -t failed: objdump: /tmp/fw_analysis_qhn9uciz/FST 2.3.13.0.msi_extracted/_FST 2.3.13.0.msi.extracted/3B81B6: file format not recognized

### /tmp/fw_analysis_qhn9uciz/FST 2.3.13.0.msi_extracted/_FST 2.3.13.0.msi.extracted/3B81D2

- **File type:** data
- **Extraction status:** ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected.
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** objdump -t failed: objdump: /tmp/fw_analysis_qhn9uciz/FST 2.3.13.0.msi_extracted/_FST 2.3.13.0.msi.extracted/3B81D2: file format not recognized

### /tmp/fw_analysis_qhn9uciz/FST 2.3.13.0.msi_extracted/_FST 2.3.13.0.msi.extracted/3B81F0

- **File type:** data
- **Extraction status:** ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected.
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** objdump -t failed: objdump: /tmp/fw_analysis_qhn9uciz/FST 2.3.13.0.msi_extracted/_FST 2.3.13.0.msi.extracted/3B81F0: file format not recognized

### /tmp/fw_analysis_qhn9uciz/FST 2.3.13.0.msi_extracted/_FST 2.3.13.0.msi.extracted/3B820A

- **File type:** data
- **Extraction status:** ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected.
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** objdump -t failed: objdump: /tmp/fw_analysis_qhn9uciz/FST 2.3.13.0.msi_extracted/_FST 2.3.13.0.msi.extracted/3B820A: file format not recognized

### /tmp/fw_analysis_qhn9uciz/FST 2.3.13.0.msi_extracted/_FST 2.3.13.0.msi.extracted/3B8221

- **File type:** data
- **Extraction status:** ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected.
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** objdump -t failed: objdump: /tmp/fw_analysis_qhn9uciz/FST 2.3.13.0.msi_extracted/_FST 2.3.13.0.msi.extracted/3B8221: file format not recognized

### /tmp/fw_analysis_qhn9uciz/FST 2.3.13.0.msi_extracted/_FST 2.3.13.0.msi.extracted/3B9000

- **File type:** DER Encoded PKCS#7 Signed Data
- **Extraction status:** ok: unrecognized/non-executable file type ('DER Encoded PKCS#7 Signed Data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected.
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** objdump -t failed: objdump: /tmp/fw_analysis_qhn9uciz/FST 2.3.13.0.msi_extracted/_FST 2.3.13.0.msi.extracted/3B9000: file format not recognized

### /tmp/fw_analysis_qhn9uciz/FST 2.3.13.0.msi_extracted/_FST 2.3.13.0.msi.extracted/3B9094

- **File type:** Certificate, Version=3
- **Extraction status:** ok: unrecognized/non-executable file type ('Certificate, Version=3') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected.
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** objdump -t failed: objdump: /tmp/fw_analysis_qhn9uciz/FST 2.3.13.0.msi_extracted/_FST 2.3.13.0.msi.extracted/3B9094: file format not recognized

### /tmp/fw_analysis_qhn9uciz/FST 2.3.13.0.msi_extracted/_FST 2.3.13.0.msi.extracted/3B9596

- **File type:** Certificate, Version=3
- **Extraction status:** ok: unrecognized/non-executable file type ('Certificate, Version=3') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected.
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** objdump -t failed: objdump: /tmp/fw_analysis_qhn9uciz/FST 2.3.13.0.msi_extracted/_FST 2.3.13.0.msi.extracted/3B9596: file format not recognized

### /tmp/fw_analysis_qhn9uciz/FST 2.3.13.0.msi_extracted/_FST 2.3.13.0.msi.extracted/3B9ACB

- **File type:** Certificate, Version=3
- **Extraction status:** ok: unrecognized/non-executable file type ('Certificate, Version=3') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected.
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** objdump -t failed: objdump: /tmp/fw_analysis_qhn9uciz/FST 2.3.13.0.msi_extracted/_FST 2.3.13.0.msi.extracted/3B9ACB: file format not recognized

### /tmp/fw_analysis_qhn9uciz/FST 2.3.13.0.msi_extracted/_FST 2.3.13.0.msi.extracted/3BA17F

- **File type:** Certificate, Version=3
- **Extraction status:** ok: unrecognized/non-executable file type ('Certificate, Version=3') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected.
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** objdump -t failed: objdump: /tmp/fw_analysis_qhn9uciz/FST 2.3.13.0.msi_extracted/_FST 2.3.13.0.msi.extracted/3BA17F: file format not recognized

### /tmp/fw_analysis_qhn9uciz/FST 2.3.13.0.msi_extracted/_FST 2.3.13.0.msi.extracted/5000

- **File type:** Microsoft Cabinet archive data, many, 3532647 bytes, 6 files, at 0x2c last modified Sun, Dec 22 2021 10:23:38 +A "_1MRG028040_Field_Service_Tool_Instruction.pdf" last modified Sun, Nov 08 2014 11:51:12 +A "DelZip192.dll", number 1, 222 datablocks, 0x1 compression
- **Extraction status:** error: cab extraction failed: exit code 1: /tmp/fw_analysis_qhn9uciz/FST 2.3.13.0.msi_extracted/_FST 2.3.13.0.msi.extracted/5000: WARNING; possible 358553 extra bytes at end of file.
/tmp/fw_analysis_qhn9uciz/5000_extracted/_1MRG028040_Field_Service_Tool_Instruction.pdf: checksum error
/tmp/fw_analysis_qhn9uciz/5000_extracted/DelZip192.dll: 

### /tmp/fw_analysis_qhn9uciz/34_Relion670_Firmware update 1p1r01 to 27.zip_extracted/Relion670/Field_Service_Tool_instruction.pdf

- **File type:** PDF document, version 1.4, 43 page(s)
- **Extraction status:** skipped: recognized non-firmware document type (pdf/xlsx/png/etc.) - not analyzed

### /tmp/fw_analysis_qhn9uciz/34_Relion670_Firmware update 1p1r01 to 27.zip_extracted/Relion670/ShortProcedure.png

- **File type:** PNG image data, 1814 x 1462, 8-bit/color RGBA, non-interlaced
- **Extraction status:** skipped: recognized non-firmware document type (pdf/xlsx/png/etc.) - not analyzed

### /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/1A00

- **File type:** PC bitmap, Windows 3.x format, 158 x 323 x 32, image size 204138, resolution 2834 x 2834 px/m, cbSize 204192, bits offset 54
- **Extraction status:** ok: unrecognized/non-executable file type ('PC bitmap, Windows 3.x format, 158 x 323 x 32, image size 204138, resolution 2834 x 2834 px/m, cbSize 204192, bits offset 54') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected.
- **Entropy verdict:** possible_compression_or_encryption (1 flagged region(s))
- **String scan categories matched:** iec61850, auth_credentials, network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** objdump -t failed: objdump: /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/1A00: file format not recognized

### /tmp/fw_analysis_qhn9uciz/48E00.cab_extracted/_1MRG031502_FST_670_1.1_update.pdf

- **File type:** PDF document, version 1.5, 8 page(s)
- **Extraction status:** skipped: recognized non-firmware document type (pdf/xlsx/png/etc.) - not analyzed

### /tmp/fw_analysis_qhn9uciz/48E00.cab_extracted/oneshot.txt

- **File type:** ASCII text, with CRLF line terminators
- **Extraction status:** skipped: recognized non-firmware document type (pdf/xlsx/png/etc.) - not analyzed

### /tmp/fw_analysis_qhn9uciz/48E00.cab_extracted/package.ini

- **File type:** Generic INItialization configuration [UPDATE]
- **Extraction status:** skipped: recognized non-firmware document type (pdf/xlsx/png/etc.) - not analyzed

### /tmp/fw_analysis_qhn9uciz/48E00.cab_extracted/ppc670.x

- **File type:** ELF 32-bit MSB executable, PowerPC or cisco 4500, version 1 (SYSV), statically linked, not stripped
- **Extraction status:** ok: leaf binary ready for analysis
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** iec61850, acse_association, weak_crypto, unsafe_functions, auth_credentials, network_services, rtos_platform
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** required disassembler 'powerpc-linux-gnu-objdump' is not installed on this system. Install the matching binutils cross-toolchain package (e.g. 'sudo apt-get install binutils-powerpc-linux-gnu') and re-run.

### /tmp/fw_analysis_qhn9uciz/48E00.cab_extracted/ppc670.x1

- **File type:** ELF 32-bit MSB executable, PowerPC or cisco 4500, version 1 (SYSV), statically linked, not stripped
- **Extraction status:** ok: leaf binary ready for analysis
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** iec61850, acse_association, weak_crypto, unsafe_functions, auth_credentials, network_services, rtos_platform
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** required disassembler 'powerpc-linux-gnu-objdump' is not installed on this system. Install the matching binutils cross-toolchain package (e.g. 'sudo apt-get install binutils-powerpc-linux-gnu') and re-run.

### /tmp/fw_analysis_qhn9uciz/48E00.cab_extracted/prebase.txt

- **File type:** ASCII text, with CRLF line terminators
- **Extraction status:** skipped: recognized non-firmware document type (pdf/xlsx/png/etc.) - not analyzed

### /tmp/fw_analysis_qhn9uciz/productdef_1p1r27.zip_extracted/productdef.xml

- **File type:** HTML document, ASCII text, with CRLF line terminators
- **Extraction status:** skipped: recognized non-firmware document type (pdf/xlsx/png/etc.) - not analyzed

### /tmp/fw_analysis_qhn9uciz/48E00.cab_extracted/update.cfg

- **File type:** Generic INItialization configuration [ID]
- **Extraction status:** skipped: recognized non-firmware document type (pdf/xlsx/png/etc.) - not analyzed

### /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/90BD00

- **File type:** PC bitmap, Windows 3.x format, 35 x 35 x 4, image size 700, resolution 3780 x 3780 px/m, cbSize 818, bits offset 118
- **Extraction status:** ok: unrecognized/non-executable file type ('PC bitmap, Windows 3.x format, 35 x 35 x 4, image size 700, resolution 3780 x 3780 px/m, cbSize 818, bits offset 118') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected.
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** auth_credentials, network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** objdump -t failed: objdump: /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/90BD00: file format not recognized

### /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/90EB42

- **File type:** data
- **Extraction status:** ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected.
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** auth_credentials, network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** objdump -t failed: objdump: /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/90EB42: file format not recognized

### /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/90FC2F

- **File type:** data
- **Extraction status:** ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected.
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** auth_credentials, network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** objdump -t failed: objdump: /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/90FC2F: file format not recognized

### /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/90FC41

- **File type:** data
- **Extraction status:** ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected.
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** auth_credentials, network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** objdump -t failed: objdump: /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/90FC41: file format not recognized

### /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/910CD1

- **File type:** data
- **Extraction status:** ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected.
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** auth_credentials, network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** objdump -t failed: objdump: /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/910CD1: file format not recognized

### /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/910FF8

- **File type:** data
- **Extraction status:** ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected.
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** auth_credentials, network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** objdump -t failed: objdump: /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/910FF8: file format not recognized

### /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/912073

- **File type:** data
- **Extraction status:** ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected.
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** auth_credentials, network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** objdump -t failed: objdump: /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/912073: file format not recognized

### /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/912094

- **File type:** data
- **Extraction status:** ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected.
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** auth_credentials, network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** objdump -t failed: objdump: /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/912094: file format not recognized

### /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/91212D

- **File type:** data
- **Extraction status:** ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected.
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** auth_credentials, network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** objdump -t failed: objdump: /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/91212D: file format not recognized

### /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/9124DA

- **File type:** data
- **Extraction status:** ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected.
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** auth_credentials, network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** objdump -t failed: objdump: /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/9124DA: file format not recognized

### /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/912586

- **File type:** data
- **Extraction status:** ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected.
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** auth_credentials, network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** objdump -t failed: objdump: /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/912586: file format not recognized

### /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/9125A3

- **File type:** data
- **Extraction status:** ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected.
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** auth_credentials, network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** objdump -t failed: objdump: /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/9125A3: file format not recognized

### /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/91826E

- **File type:** data
- **Extraction status:** ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected.
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** auth_credentials, network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** objdump -t failed: objdump: /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/91826E: file format not recognized

### /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/91828B

- **File type:** data
- **Extraction status:** ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected.
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** auth_credentials, network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** objdump -t failed: objdump: /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/91828B: file format not recognized

### /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/9182A7

- **File type:** data
- **Extraction status:** ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected.
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** auth_credentials, network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** objdump -t failed: objdump: /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/9182A7: file format not recognized

### /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/9182C2

- **File type:** data
- **Extraction status:** ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected.
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** auth_credentials, network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** objdump -t failed: objdump: /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/9182C2: file format not recognized

### /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/9182D6

- **File type:** data
- **Extraction status:** ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected.
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** auth_credentials, network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** objdump -t failed: objdump: /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/9182D6: file format not recognized

### /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/9188C8

- **File type:** data
- **Extraction status:** ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected.
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** auth_credentials, network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** objdump -t failed: objdump: /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/9188C8: file format not recognized

### /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/9188F2

- **File type:** data
- **Extraction status:** ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected.
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** auth_credentials, network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** objdump -t failed: objdump: /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/9188F2: file format not recognized

### /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/918918

- **File type:** data
- **Extraction status:** ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected.
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** auth_credentials, network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** objdump -t failed: objdump: /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/918918: file format not recognized

### /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/91D62A

- **File type:** data
- **Extraction status:** ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected.
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** auth_credentials, network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** objdump -t failed: objdump: /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/91D62A: file format not recognized

### /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/924A00

- **File type:** PC bitmap, Windows 3.x format, 500 x 63 x 8, 1 compression, image size 3072, resolution 3779 x 3779 px/m, 255 important colors, cbSize 4132, bits offset 1074
- **Extraction status:** ok: unrecognized/non-executable file type ('PC bitmap, Windows 3.x format, 500 x 63 x 8, 1 compression, image size 3072, resolution 3779 x 3779 px/m, 255 important colors, cbSize 4132, bits offset 1074') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected.
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** auth_credentials, network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** objdump -t failed: objdump: /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/924A00: file format not recognized

### /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/925C00

- **File type:** PE32 executable (DLL) (GUI) Intel 80386, for MS Windows, 4 sections
- **Extraction status:** ok: leaf binary ready for analysis
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** auth_credentials, network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** symbol table extraction ran but found no symbols - the binary may be stripped (no debug/function names available)

### /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/927008

- **File type:** DER Encoded PKCS#7 Signed Data
- **Extraction status:** ok: unrecognized/non-executable file type ('DER Encoded PKCS#7 Signed Data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected.
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** objdump -t failed: objdump: /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/927008: file format not recognized

### /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/92709D

- **File type:** Certificate, Version=3
- **Extraction status:** ok: unrecognized/non-executable file type ('Certificate, Version=3') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected.
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** objdump -t failed: objdump: /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/92709D: file format not recognized

### /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/927560

- **File type:** Certificate, Version=3
- **Extraction status:** ok: unrecognized/non-executable file type ('Certificate, Version=3') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected.
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** objdump -t failed: objdump: /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/927560: file format not recognized

### /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/9275F6

- **File type:** data
- **Extraction status:** ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected.
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** auth_credentials, network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** objdump -t failed: objdump: /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/9275F6: file format not recognized

### /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/928200

- **File type:** PE32+ executable (DLL) (GUI) x86-64, for MS Windows, 6 sections
- **Extraction status:** ok: leaf binary ready for analysis
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** auth_credentials, network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** symbol table extraction ran but found no symbols - the binary may be stripped (no debug/function names available)

### /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/931608

- **File type:** DER Encoded PKCS#7 Signed Data
- **Extraction status:** ok: unrecognized/non-executable file type ('DER Encoded PKCS#7 Signed Data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected.
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** objdump -t failed: objdump: /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/931608: file format not recognized

### /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/93169D

- **File type:** Certificate, Version=3
- **Extraction status:** skipped: duplicate content, identical to already-analyzed file '/tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/92709D'

### /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/931B60

- **File type:** Certificate, Version=3
- **Extraction status:** skipped: duplicate content, identical to already-analyzed file '/tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/927560'

### /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/931BF6

- **File type:** data
- **Extraction status:** ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected.
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** auth_credentials, network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** objdump -t failed: objdump: /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/931BF6: file format not recognized

### /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/932400

- **File type:** PE32 executable (DLL) (GUI) Intel 80386, for MS Windows, 5 sections
- **Extraction status:** ok: leaf binary ready for analysis
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** auth_credentials, network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** symbol table extraction ran but found no symbols - the binary may be stripped (no debug/function names available)

### /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/938008

- **File type:** DER Encoded PKCS#7 Signed Data
- **Extraction status:** ok: unrecognized/non-executable file type ('DER Encoded PKCS#7 Signed Data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected.
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** objdump -t failed: objdump: /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/938008: file format not recognized

### /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/93809D

- **File type:** Certificate, Version=3
- **Extraction status:** skipped: duplicate content, identical to already-analyzed file '/tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/92709D'

### /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/938560

- **File type:** Certificate, Version=3
- **Extraction status:** skipped: duplicate content, identical to already-analyzed file '/tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/927560'

### /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/9385F6

- **File type:** data
- **Extraction status:** ok: unrecognized/non-executable file type ('data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected.
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** objdump -t failed: objdump: /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/9385F6: file format not recognized

### /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/93A400

- **File type:** DER Encoded PKCS#7 Signed Data
- **Extraction status:** ok: unrecognized/non-executable file type ('DER Encoded PKCS#7 Signed Data') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected.
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** objdump -t failed: objdump: /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/93A400: file format not recognized

### /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/93A494

- **File type:** Certificate, Version=3
- **Extraction status:** ok: unrecognized/non-executable file type ('Certificate, Version=3') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected.
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** objdump -t failed: objdump: /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/93A494: file format not recognized

### /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/93A886

- **File type:** Certificate, Version=3
- **Extraction status:** ok: unrecognized/non-executable file type ('Certificate, Version=3') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected.
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** objdump -t failed: objdump: /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/93A886: file format not recognized

### /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/93AD2D

- **File type:** Certificate, Version=3
- **Extraction status:** ok: unrecognized/non-executable file type ('Certificate, Version=3') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected.
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** objdump -t failed: objdump: /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/93AD2D: file format not recognized

### /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/93B261

- **File type:** Certificate, Version=3
- **Extraction status:** ok: unrecognized/non-executable file type ('Certificate, Version=3') - not a known archive format, so treated as a raw leaf for entropy/string/YARA analysis. Symbol/disassembly stage will likely report 'no symbols' for this file, which is expected.
- **Entropy verdict:** clean (0 flagged region(s))
- **String scan categories matched:** network_services
- **YARA scan error:** yara-python is not installed (pip install yara-python --break-system-packages)
- **Symbol analysis error:** objdump -t failed: objdump: /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/93B261: file format not recognized

### /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/_1MRG031502_FST_670_1.1_update.pdf

- **File type:** PDF document, version 1.5, 8 page(s)
- **Extraction status:** skipped: recognized non-firmware document type (pdf/xlsx/png/etc.) - not analyzed

### /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/oneshot.txt

- **File type:** ASCII text, with CRLF line terminators
- **Extraction status:** skipped: recognized non-firmware document type (pdf/xlsx/png/etc.) - not analyzed

### /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/package.ini

- **File type:** Generic INItialization configuration [UPDATE]
- **Extraction status:** skipped: recognized non-firmware document type (pdf/xlsx/png/etc.) - not analyzed

### /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/ppc670.x

- **File type:** ELF 32-bit MSB executable, PowerPC or cisco 4500, version 1 (SYSV), statically linked, not stripped
- **Extraction status:** skipped: duplicate content, identical to already-analyzed file '/tmp/fw_analysis_qhn9uciz/48E00.cab_extracted/ppc670.x'

### /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/ppc670.x1

- **File type:** ELF 32-bit MSB executable, PowerPC or cisco 4500, version 1 (SYSV), statically linked, not stripped
- **Extraction status:** skipped: duplicate content, identical to already-analyzed file '/tmp/fw_analysis_qhn9uciz/48E00.cab_extracted/ppc670.x1'

### /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/prebase.txt

- **File type:** ASCII text, with CRLF line terminators
- **Extraction status:** skipped: recognized non-firmware document type (pdf/xlsx/png/etc.) - not analyzed

### /tmp/fw_analysis_qhn9uciz/update_670_1.1.27_MR.msi_extracted/_update_670_1.1.27_MR.msi.extracted/update.cfg

- **File type:** Generic INItialization configuration [ID]
- **Extraction status:** skipped: recognized non-firmware document type (pdf/xlsx/png/etc.) - not analyzed
