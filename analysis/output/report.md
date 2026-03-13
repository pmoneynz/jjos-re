# JJOS Firmware Structural Report

- File: `mpc2500_jv313.bin`
- Size: `894040` bytes
- SHA-256: `7a64b6c82bf47bff3f0091fa90a0c7162fc563352f1c779a2c59f9da449e66b9`
- Entropy: `6.8694` bits/byte

## Mapping Heuristics and Current Architecture Baseline

- Static pointer-density scan still reports a legacy high-score base candidate at `0x09000000`.
- Legacy evidence count: `6281` aligned big-endian words map inside-file under that base arithmetic.
- This scanner is ISA-agnostic and does **not** prove CPU architecture by itself.
- Current repository baseline for disassembly remains:
  - SuperH-family import in Ghidra (`SuperH4:LE:32:default`)
  - raw image base `0x00000000`
  - seed flow `0x00000000 -> 0x00000626`
- `0x08xxxxxx` / `0x09xxxxxx` / `0x0Axxxxxx` pointer-like prefixes still suggest multiple mapped regions or table domains worth tracking.

## Candidate Validation / Checksum Areas

- Boot/update string block at `0x7BE0-0x8130`: dense cluster of status and error strings tied to loading and writing the OS image.
- Direct/immediate references into that boot/update block under the legacy `0x09000000` arithmetic scan: `207` hits.
- Flash progress strings at `0x94A0` and `0x94B8` are directly referenced from file offsets `0x4F61C` and `0x89290`.
- Later JJOS/OS-XL UI blocks around `0xC7D40-0xD3230` do not expose clean direct references under that same arithmetic model, suggesting table-driven/indirect lookup.
- No standard table-driven `CRC32` or `CRC16-CCITT` lookup tables were found in the image.
- Practical implication: update validation is likely custom, bitwise, additive, or embedded inside hand-written routines rather than a stock table-based CRC implementation.

## String / Feature Map

- The densest UI/resource area is `0xC0000-0xDFFFF`.
- Feature families recovered from strings include storage/filesystem, USB transfer, sequencing, sampling, MIDI/program handling, MPC2000XL compatibility, password handling, and flash update flows.

## First Safe POC Patch

1. Duplicate the original image and never patch the only copy.
2. Patch a fixed-length UI string in a late resource block, not boot-critical code and not the main version banner.
3. Best initial target: the late update-label string at `0xC7D74` (`OS update`) or another same-length late UI string, because it is cosmetic and isolated.
4. Keep the replacement exactly the same byte length. Do not insert or delete bytes.
5. Before any hardware flash attempt, identify and bypass or reproduce the update integrity check so the device accepts the modified image.
6. First hardware validation should stop before flash commit if possible: confirm the device loads the file and reaches the update screen with the modified label.

## Regeneration

- Run: `python3 analysis/scan_firmware.py mpc2500_jv313.bin`
- Output directory: `analysis/output`
