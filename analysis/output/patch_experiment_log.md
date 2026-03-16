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

## Trial 0004 - Hardware Dry-Run Media Preparation (T0004)

- Date (UTC): 2026-03-15
- Goal: execute Gate 5.1 with reproducible media/filename discipline for dry-run update loading.
- Risk classification: cosmetic (safe) candidate; no additional firmware logic/code edits beyond Trial 0003 patch semantics.
- Input firmware: `analysis/mpc2500.bin`
- Input SHA-256: `6a09b1801f4c38c2f710028126b70290e907980aea35b18c6e66459004d089b5`
- Patch spec: `analysis/patch_specs/t0004_mpc2500_late_os_update.json`
- Candidate binary: `hardware_candidates/mpc2500_t0004_late_os_update.bin`
- Output SHA-256: `e54040ef75cb5da75a0d4a7be2bcac96d6e163804b21b7d10865b70285d20099`
- Manifest: `analysis/output/t0004_mpc2500_late_os_update_manifest.json`
- Media image: `hardware_candidates/t0004_cf_fat16.img` (FAT16, volume label `MPCCF004`)
- Controlled updater filename on prepared media root: `MPC2500.SOS`
- Media image SHA-256: `5be262f219261cc4c7211aee0ff413d31d4d1022452b713a057cb18199fb473f`

### Byte-level change

- Offset: `0xB1B28`
- Before: `OS update` (`4f5320757064617465`)
- After: `OS MOD V3` (`4f53204d4f44205633`)
- Length preserved: yes (`9` bytes)

### Current status

- Gate 5.1 evidence completed via host-side FAT16 media preparation and filename verification.
- Operator-reported hardware outcome: `mpc2500_t0004_late_os_update.bin` loads and runs successfully on MPC2500.
- User-provided screenshot evidence references are now documented in `analysis/output/t0004_hardware_capture_notes.md`.
- Hardware screenshots show file selection/confirmation path using `mpc2500.update`.
- Additional proof screenshot now shows patched label `OS MOD V3` with `Flash ROM Writing 11%`.

## Trial 0005 - Matrix B Startup Banner Patch

- Date (UTC): 2026-03-15
- Goal: create startup-banner matrix candidate for integrity characterization.
- Risk classification: cosmetic (safe) — same-length text edit in startup banner string block.
- Input firmware: `analysis/mpc2500.bin`
- Input SHA-256: `6a09b1801f4c38c2f710028126b70290e907980aea35b18c6e66459004d089b5`
- Patch spec: `analysis/patch_specs/t0005_mpc2500_startup_banner_matrix.json`
- Candidate binary: `hardware_candidates/mpc2500_t0005_startup_banner_matrix.bin`
- Output SHA-256: `1dafc6e8285faa3c532f2e54df286175cbcb136dc9558b5c905a70fc0aeb0040`
- Manifest: `analysis/output/t0005_mpc2500_startup_banner_manifest.json`

### Byte-level change

- Offset: `0x10000`
- Before: `MPC2500         Version=1.24   30-July-2008     `
- After: `MPC2500         Version=1.24   MATRIX-B-05      `
- Length preserved: yes (`48` bytes)
- Byte-level verification: 11 bytes changed (`0x1001F..0x1002A`).

### Current status

- Candidate generated and manifested.
- Hardware proof captured: runtime UI shows `Version=1.24   MATRIX-B-05` on MPC2500.
- Trial result recorded as accepted in `analysis/output/t0005_hardware_trial_result.json`.

## Trial 0006 - Matrix C Neutral-Region Single-Byte Patch

- Date (UTC): 2026-03-15
- Goal: create non-UI single-byte matrix candidate to test broad integrity behavior.
- Risk classification: moderate/high (neutral-region hypothesis) — one-byte edit in long zero-filled region, functional impact unknown until hardware run.
- Input firmware: `analysis/mpc2500.bin`
- Input SHA-256: `6a09b1801f4c38c2f710028126b70290e907980aea35b18c6e66459004d089b5`
- Patch spec: `analysis/patch_specs/t0006_mpc2500_neutral_byte_matrix.json`
- Candidate binary: `hardware_candidates/mpc2500_t0006_neutral_byte_matrix.bin`
- Output SHA-256: `14bf5aa37b7aef59fba0d828d2f5e1fce1cc9fb8afe128a7ef1a1370ef786219`
- Manifest: `analysis/output/t0006_mpc2500_neutral_byte_manifest.json`

### Byte-level change

- Offset: `0x9500`
- Before: `00`
- After: `01`
- Length preserved: yes (`1` byte)
- Byte-level verification: exactly one byte changed.

### Current status

- Candidate generated and manifested.
- Operator-reported hardware outcome: T0006 succeeds on MPC2500.
- Evidence currently note-only (no screenshot/video yet recorded) in `analysis/output/t0006_hardware_trial_result.json`.

## Trial 0007 - Matrix Control / Original

- Date (UTC): 2026-03-15
- Goal: create reproducible control candidate artifact with no effective binary change.
- Risk classification: control (safe) — explicit no-op patch keeps binary byte-identical.
- Input firmware: `analysis/mpc2500.bin`
- Input SHA-256: `6a09b1801f4c38c2f710028126b70290e907980aea35b18c6e66459004d089b5`
- Patch spec: `analysis/patch_specs/t0007_mpc2500_control_original.json`
- Candidate binary: `hardware_candidates/mpc2500_t0007_control_original.bin`
- Output SHA-256: `6a09b1801f4c38c2f710028126b70290e907980aea35b18c6e66459004d089b5`
- Manifest: `analysis/output/t0007_mpc2500_control_manifest.json`

### Byte-level change

- Offset: `0x7C9C`
- Before: `3d`
- After: `3d`
- Length preserved: yes (`1` byte)
- Byte-level verification: zero byte differences between input and output candidate.

### Current status

- Control candidate generated and manifested.
- Hardware screenshot shows update dialog loading T0007 candidate; operator reports success.
- Trial recorded as accepted in `analysis/output/t0007_hardware_trial_result.json`.

## Trial 0008 - First Logic Patch (Error Dispatch Compare Shift)

- Date (UTC): 2026-03-15
- Goal: create first minimal reversible logic patch candidate for Gate 8.x readiness.
- Risk classification: logic (moderate) — modifies one compare immediate in error-dispatch control flow.
- Input firmware: `analysis/mpc2500.bin`
- Input SHA-256: `6a09b1801f4c38c2f710028126b70290e907980aea35b18c6e66459004d089b5`
- Patch spec: `analysis/patch_specs/t0008_mpc2500_logic_error_dispatch_shift.json`
- Candidate binary: `hardware_candidates/mpc2500_t0008_logic_error_dispatch_shift.bin`
- Output SHA-256: `2e103331c2dc18a86b47982f8f7aecb4192cbb4dc7cb6b251109196b34d5316a`
- Manifest: `analysis/output/t0008_mpc2500_logic_error_dispatch_shift_manifest.json`

### Byte-level change

- Offset: `0x1064`
- Before: `0a88` (`cmp/eq #10,r0`)
- After: `0b88` (`cmp/eq #11,r0`)
- Length preserved: yes (`2` bytes)
- Byte-level verification: exactly one byte changed (`0x1064`).

### Current status

- Candidate generated and manifested with deterministic single-byte control-flow change.
- Hardware acceptance is proven (load + completed flash write).
- No-media validation case showed same message as control (`Insert Memory Card !!`), so behavior-change effect is not yet demonstrated for this patch.

## Trial 0009 - Diagnostic Control (Forced Status=10)

- Date (UTC): 2026-03-15
- Goal: force error-dispatch input to status 10 on control baseline for deterministic A/B with T0010.
- Risk classification: diagnostic logic (temporary).
- Input firmware: `analysis/mpc2500.bin`
- Input SHA-256: `6a09b1801f4c38c2f710028126b70290e907980aea35b18c6e66459004d089b5`
- Patch spec: `analysis/patch_specs/t0009_diag_control_force_status10.json`
- Candidate binary: `hardware_candidates/mpc2500_t0009_diag_control_force_status10.bin`
- Output SHA-256: `4b08e3c19040af8c356c844dd924ddcfd14d1aa0796601f02d4acb679f28cdab`
- Manifest: `analysis/output/t0009_diag_control_force_status10_manifest.json`

### Byte-level change

- Offset: `0x1062`
- Before: `fd00` (`mov.w @(r0,r15),r0`)
- After: `0ae0` (`mov #10,r0`)
- Length preserved: yes (`2` bytes)

### Current status

- Diagnostic build generated; awaiting hardware A/B capture.
- Hardware run outcome reported: `Wrong card !!`.

## Trial 0010 - Diagnostic T0008 (Forced Status=10 + cmp#11)

- Date (UTC): 2026-03-15
- Goal: force same dispatch input as T0009 while retaining T0008 compare shift to expose deterministic branch divergence.
- Risk classification: diagnostic logic (temporary).
- Input firmware: `analysis/mpc2500.bin`
- Input SHA-256: `6a09b1801f4c38c2f710028126b70290e907980aea35b18c6e66459004d089b5`
- Patch spec: `analysis/patch_specs/t0010_diag_t0008_force_status10.json`
- Candidate binary: `hardware_candidates/mpc2500_t0010_diag_t0008_force_status10.bin`
- Output SHA-256: `ffe648dd2528a3facf1404098c22f5b27a8af4557ddaa0bd4dc7ee3a7a6508c1`
- Manifest: `analysis/output/t0010_diag_t0008_force_status10_manifest.json`

### Byte-level change

- Offset `0x1062`: `fd00` -> `0ae0` (force status 10)
- Offset `0x1064`: `0a88` -> `0b88` (T0008 compare shift 10->11)

### Current status

- Diagnostic build generated; awaiting hardware A/B capture.
- Hardware run outcome reported: `Wrong card !!` (same as T0009).
- No differential behavior observed in this A/B run.

