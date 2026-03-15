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

## Trial 0002 - Startup Banner Candidate (Real Hardware)

- Date (UTC): 2026-03-13
- Goal: generate a startup banner candidate for real hardware validation.
- Input firmware: `mpc2500_jv313.bin`
- Input SHA-256: `7a64b6c82bf47bff3f0091fa90a0c7162fc563352f1c779a2c59f9da449e66b9`
- Patch spec: `analysis/patch_specs/poc_startup_banner_cand01.json`
- Candidate binary: `hardware_candidates/mpc2500_jv313_startup_banner_cand01.bin`
- Output SHA-256: `c887e4fc263c09d8e62e561689babe3c1832ea7748a3a7261e806d00b6c36dcd`
- Manifest: `analysis/output/startup_banner_cand01_manifest.json`

### Byte-level change

- Offset: `0x10000`
- Before: `MPC2500         Version=3.13   16-FEB-2015     ` (`4d50433235303020202020202020202056657273696f6e3d332e313320202031362d4645422d323031352020202020`)
- After: `MPC2500         Version=3.13   CANDIDATE-01    ` (`4d50433235303020202020202020202056657273696f6e3d332e313320202043414e4449444154452d303120202020`)
- Length preserved: yes (`47` bytes)

### Current status

- Candidate produced and byte-verified in this workspace.
- Awaiting real MPC2500 hardware outcome evidence.

## Trial 0003 - mpc2500.bin Late OS Update Label Patch

- Date (UTC): 2026-03-15
- Goal: generate a deterministic single-variable cosmetic candidate for `analysis/mpc2500.bin`.
- Risk classification: cosmetic (safe) — modifies a late UI label string (`OS update`) with same-length bytes only.
- Input firmware: `analysis/mpc2500.bin`
- Input SHA-256: `6a09b1801f4c38c2f710028126b70290e907980aea35b18c6e66459004d089b5`
- Patch spec: `analysis/patch_specs/t0003_mpc2500_late_os_update.json`
- Candidate binary: `hardware_candidates/mpc2500_t0003_late_os_update.bin`
- Output SHA-256: `e54040ef75cb5da75a0d4a7be2bcac96d6e163804b21b7d10865b70285d20099`
- Manifest: `analysis/output/t0003_mpc2500_late_os_update_manifest.json`

### Byte-level change

- Offset: `0xB1B28`
- Before: `OS update` (`4f5320757064617465`)
- After: `OS MOD V3` (`4f53204d4f44205633`)
- Length preserved: yes (`9` bytes)
- Byte-level verification: only 6 byte values changed (contiguous range `0xB1B2B`..`0xB1B30`), consistent with replacing `update` -> `MOD V3` while keeping `OS ` unchanged.

### Current status

- Candidate generated and manifested in this workspace.
- No hardware media preparation or on-device dry-run evidence captured yet.

