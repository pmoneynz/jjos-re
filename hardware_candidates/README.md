# Hardware Test Candidates

## Candidate: `mpc2500_jv313_startup_banner_cand01.bin`

- Purpose: startup/version banner identification patch for real-hardware dry-run.
- Input firmware: `mpc2500_jv313.bin`
- Input SHA-256: `7a64b6c82bf47bff3f0091fa90a0c7162fc563352f1c779a2c59f9da449e66b9`
- Output SHA-256: `c887e4fc263c09d8e62e561689babe3c1832ea7748a3a7261e806d00b6c36dcd`
- Patch spec: `analysis/patch_specs/poc_startup_banner_cand01.json`
- Manifest: `analysis/output/startup_banner_cand01_manifest.json`

### Byte change

- Offset: `0x10000`
- Before: `MPC2500         Version=3.13   16-FEB-2015     `
- After:  `MPC2500         Version=3.13   CANDIDATE-01    `
- Length preserved: `47` bytes

### Testing intent

This is a **same-length cosmetic patch** intended to confirm whether modified firmware reaches expected startup/update behavior on real MPC2500 hardware.

