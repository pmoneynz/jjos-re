# Patch Experiment Log

## Trial 0001 - Late UI Label Cosmetic Patch

- Date (UTC): 2026-03-13
- Goal: produce a deterministic same-length firmware patch candidate for Stage 1 dry-run testing.
- Input firmware: `mpc2500_jv313.bin`
- Input SHA-256: `7a64b6c82bf47bff3f0091fa90a0c7162fc563352f1c779a2c59f9da449e66b9`
- Patch spec: `analysis/patch_specs/poc_late_os_update.json`
- Output SHA-256: `51f719ce90592f97443bafef771bea622caa731685654ba70fb7003dd758f751`
- Manifest: `analysis/output/poc_late_os_update_manifest.json`

### Byte-level change

- Offset: `0xC7D74`
- Before: `OS update` (`4f5320757064617465`)
- After: `OS MOD V1` (`4f53204d4f44205631`)
- Length preserved: yes (`9` bytes)

### Current status

- Firmware candidate generated successfully.
- No hardware execution yet in this workspace.
- Next required evidence: on-device behavior trace using the stage gates in `analysis/PRACTICAL_PATCH_PATH.md`.

