# T0004 Media Preparation Notes (Gate 5.1 Evidence)

## Objective

Prepare a controlled CF-style update media artifact with expected updater filename `MPC2500.SOS` for dry-run validation workflow.

## Method (reproducible)

1. Create 16 MiB image file:
   - `truncate -s 16M hardware_candidates/t0004_cf_fat16.img`
2. Format as FAT16:
   - `mkfs.fat -F 16 -n MPCCF004 hardware_candidates/t0004_cf_fat16.img`
3. Copy candidate firmware to root with controlled updater name:
   - `mcopy -i hardware_candidates/t0004_cf_fat16.img hardware_candidates/mpc2500_t0004_late_os_update.bin ::MPC2500.SOS`
4. Verify root directory contents:
   - `mdir -i hardware_candidates/t0004_cf_fat16.img ::`

## Verification output

- Directory listing confirms file:
  - `MPC2500.SOS` size `784916`
- Payload integrity check:
  - Candidate SHA-256: `e54040ef75cb5da75a0d4a7be2bcac96d6e163804b21b7d10865b70285d20099`
  - Extracted `MPC2500.SOS` SHA-256: `e54040ef75cb5da75a0d4a7be2bcac96d6e163804b21b7d10865b70285d20099`
  - FAT16 image SHA-256: `5be262f219261cc4c7211aee0ff413d31d4d1022452b713a057cb18199fb473f`

## Scope limitation

This is host-side media-preparation evidence only. No physical MPC2500 load attempt, photo, or video capture was executed in this environment.
