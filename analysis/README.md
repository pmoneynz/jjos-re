# JJOS Reverse Engineering Workflow

This directory contains repeatable tooling and artifacts for MPC2500/JJOS firmware analysis and patch trials.

## Current Ground Truth

- Working architecture/import path: `SuperH4:LE:32:default` with image base `0x00000000`
- Proven early update owner: `ENTRY_INIT` at `0x00000626`
- Proven first filename gate: `FUN_00008c44`
- Strong alternate filename validator candidate: `FUN_00008b8c`

Primary evidence lives in:

- `analysis/output/ghidra_sh_findings.md`
- `analysis/output/ghidra_sh_update_map.md`

## Files

- `scan_firmware.py`
  - static extractor for strings and coarse structure
- `firmware_patch_tool.py`
  - deterministic patch helper with strict expected-byte checks
- `patch_specs/`
  - versioned JSON patch specs for reproducible experiments
- `PRACTICAL_PATCH_PATH.md`
  - stage-gated path from patch generation to controlled hardware trials
- `MPC2500_OS_RE_CHECKLIST.md`
  - pass/fail-gated execution checklist for autonomous RE agents
- `templates/`
  - structured JSON templates for gate status and hardware trial outcomes
- `output/`
  - generated reports, manifests, and scan artifacts

## Recommended Workflow

1. Reconfirm structural baseline (optional but useful):
   - `python3 analysis/scan_firmware.py mpc2500_jv313.bin`
2. Read current SuperH findings:
   - `analysis/output/ghidra_sh_findings.md`
   - `analysis/output/ghidra_sh_update_map.md`
3. Inspect patch-safe targets:
   - `python3 analysis/firmware_patch_tool.py inspect --firmware mpc2500_jv313.bin`
4. Build a deterministic same-length patch candidate:
   - `python3 analysis/firmware_patch_tool.py apply --firmware mpc2500_jv313.bin --spec analysis/patch_specs/poc_late_os_update.json --output hardware_candidates/poc_late_os_update.bin --manifest analysis/output/poc_late_os_update_manifest.json`
5. Execute hardware tests using the stage gates in:
   - `analysis/MPC2500_OS_RE_CHECKLIST.md`

## Discipline

- Do not make uncontrolled binary edits.
- Every hardware trial should have:
  - input hash
  - output hash
  - patch spec
  - manifest
  - observed device result
