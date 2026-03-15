# JJOS Firmware Structural Report

- File: `mpc2500.bin`
- Size: `784916` bytes
- SHA-256: `6a09b1801f4c38c2f710028126b70290e907980aea35b18c6e66459004d089b5`
- Entropy: `6.8587` bits/byte

## Likely Architecture / Mapping

- Authoritative working RE path is currently SuperH (`SuperH4:LE:32:default`, base `0x00000000`) from the Ghidra artifacts.
- This script's pointer-density/base heuristics are coarse and should be treated as supporting context only, not architecture proof.
- Top legacy big-endian base candidate in this static scan: `0x9000000` with `5485` mapped words.
- Practical rule: rely on `analysis/output/ghidra_sh_findings.md` for architecture and control-flow claims.

## Candidate Validation / Checksum Areas

- Boot/update string block at `0x7BE0-0x8130`: dense cluster of status and error strings tied to loading and writing the OS image.
- Direct/immediate references into that boot/update block under base `0x09000000`: `216` hits.
- Flash progress strings at `0x94A0` and `0x94B8` are directly referenced from file offsets `0x4F61C` and `0x89290`.
- Later JJOS/OS-XL UI blocks around `0xC7D40-0xD3230` do not expose clean `0x09000000 + offset` references, which suggests a different addressing scheme or table-driven lookup.
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
