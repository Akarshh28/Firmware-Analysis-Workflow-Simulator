# Firmware Analyzer — Automated DLMS/COSEM Firmware Analysis CLI

Automates the exact pipeline that was run manually on the Relion670 firmware:
extraction → entropy scan → string/keyword scan → YARA pattern matching →
dynamic symbol-table lookup → targeted disassembly of flagged functions →
protocol verdict (DLMS/COSEM vs IEC 61850) → JSON + Markdown report.

## Install

```bash
pip install -r requirements.txt --break-system-packages
sudo apt-get install -y binwalk cabextract binutils-multiarch binutils-powerpc-linux-gnu
```

Install additional `binutils-<arch>-linux-gnu` packages as new architectures
are encountered (see `config.py` -> `ARCH_OBJDUMP_MAP`).

## Usage

```bash
# Analyze a whole folder (recurses through every file/archive found)
python3 main.py --input /path/to/Firmware_120626 --output ./report

# Analyze a single file
python3 main.py --input update_670_1.1.27_MR.msi --output ./report

# Skip the symbol/disassembly stage (faster; avoids objdump on very
# large or unusual binaries while you're still triaging a new device)
python3 main.py --input /path/to/firmware --output ./report --skip-symbols
```

Output: `report.json` (full machine-readable detail) and `report.md`
(human-readable summary table + per-file breakdown) in the `--output`
directory.

## How This Maps to the Project Roadmap

| Roadmap item | Module |
|---|---|
| Extraction (Binwalk-based carving) | `modules/extractor.py` |
| Entropy analysis (scipy) | `modules/entropy_analysis.py` |
| String extraction & filtering | `modules/string_scanner.py` |
| Pattern matching (YARA) | `modules/yara_scanner.py` (uses `yara_rules/`) |
| Static component analysis (unsafe functions, targeted disassembly) | `modules/symbol_analyzer.py` |
| Report generation | `modules/report_generator.py` |

Phase 3 (OBIS mapping, Security Suite verification, DLMS APDU fuzzing) and
Phase 2 Step C (Unicorn Engine fuzzing) are intentionally **not** part of
this CLI — they only apply once `protocol_verdict` in the report says
"DLMS/COSEM confirmed" for a given file. Running them against firmware
that doesn't implement DLMS/COSEM (like Relion670) would produce meaningless
results, so the pipeline stops at the verdict and leaves those phases as a
manual follow-up decision per file.

## How Symbol Targeting Works (no fixed keyword list per device)

The disassembly stage does **not** use a hardcoded list of function names.
For every file, it:

1. Runs the string scan and YARA scan first.
2. Pulls out whatever was actually found in the `unsafe_functions` and
   `auth_credentials` string categories for *that specific file*.
3. Cross-references those (plus a small generic list in
   `config.SUSPICIOUS_SYMBOL_KEYWORDS` — "backdoor", "bypass", "debug",
   etc.) against the binary's own symbol table (`objdump -t`).
4. Disassembles only the matching functions.

This is why the same script works unmodified on REB500, REX670, GE, or
Siemens firmware — the "what to look at" decision is made fresh from each
binary's own findings, not decided in advance.

## Error Handling Philosophy

No single file can crash the run. Every stage (`identify`, `extract`,
`entropy`, `strings`, `yara`, `symbols`) is wrapped so a failure produces a
specific, readable reason in the console output and the report instead of
a stack trace, for example:

```
[SKIP]  weird_file.bin: unrecognized/non-executable file type ('data') - ...
[ERROR] corrupt.zip: zip extraction failed: exit code 1: End-of-central-directory signature not found
[WARN]  Symbol analysis failed: required disassembler 'powerpc-linux-gnu-objdump' is not installed...
```

This was validated with a test corpus covering: a corrupt archive, a
random high-entropy blob, a stripped binary, a non-stripped binary with a
deliberately unsafe `strcpy` call inside a function named
`backdoor_debug_handler`, a nested zip-in-zip, and a plain document file —
every case produced the expected status and, for the vulnerable test
binary, the pipeline correctly found and disassembled the flagged function
without being told its name in advance.

## Known Limitations

- Ghidra is **not** integrated (its GUI/headless analysis proved unstable
  in the project VM — two crashes during manual use). The symbol/disassembly
  stage uses `objdump` instead, which is lighter-weight but gives raw
  assembly rather than Ghidra's decompiled pseudo-C, and won't build a full
  cross-reference/call graph. If VM stability improves, Ghidra headless
  mode (`analyzeHeadless`) would be a reasonable Phase 1 addition.
- Entropy/strings/YARA run on the whole file; on very large binaries
  (dozens of MB) this can take a noticeable amount of time. `--skip-symbols`
  helps when only a quick triage pass is needed.
- MSI extraction assumes the Cabinet-archive pattern observed in every ABB/
  Hitachi installer analyzed so far. A future installer packaged differently
  will report a clear extraction error rather than silently producing
  nothing, which is the "next-file bug fix" a maintainer needs to look at.
