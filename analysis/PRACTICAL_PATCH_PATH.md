# Practical MPC2500 OS Patch Path (Evidence-Backed)

This is the current best path to move from reverse engineering to a controlled hardware patch test.

The goal is not to "guess and flash". The goal is to collect hard evidence at each stage and only escalate when the previous stage is proven.

## Proven Facts (from this repo)

1. **CPU family and working analysis mode**
   - Proven: SuperH-family target (`HD6417727F160C` / SH7727 line), coherent disassembly under `SuperH4:LE:32:default`, image base `0x00000000`.
   - Evidence:
     - `README.md`
     - `analysis/output/ghidra_sh_findings.md`

2. **Boot/update entry flow**
   - Proven: reset flow reaches `ENTRY_INIT` at `0x00000626`.
   - Evidence:
     - `analysis/output/ghidra_sh_findings.md`
     - `analysis/output/ghidra_sh_update_map.md`

3. **Early update filename gate exists**
   - Proven: `FUN_00008c44` is a concrete early validator and is called from `ENTRY_INIT`.
   - Evidence:
     - `analysis/output/ghidra_sh_findings.md`

4. **Expected update naming includes `MPC2500` + `SOS`**
   - Proven: direct matching behavior exists in early path.
   - Evidence:
     - `analysis/output/ghidra_sh_findings.md`

5. **Alternate naming patterns likely exist**
   - Hypothesis (strong): additional tokens `M25V`, `BIN`, `MPC25T`, `MPC2500`, `SOS` in `FUN_00008b8c`.
   - Evidence:
     - `analysis/output/ghidra_sh_findings.md`

6. **Post-selection low-level device transaction path**
   - Proven (path position), not yet fully proven as flash erase/program:
     - `FUN_00008ed6`, `FUN_00008db4`, and lower routines around `0xa50072xx`.
   - Evidence:
     - `analysis/output/ghidra_sh_findings.md`
     - `analysis/output/ghidra_sh_update_map.md`

## What Is Still Unknown (must be proven)

1. Exact payload integrity check routine and algorithm.
2. Exact branch condition for `File data error` and `OS data error`.
3. First routine that provably emits AMD flash erase/program command sequences.
4. Whether a modified payload must be re-signed/checksummed, and if so, how.

Do not claim these are solved until the proof is in control flow and data flow.

## Stage-Gated Execution Plan

### Stage 0: Reproducible Baseline

Generate stable hashes and track all patch attempts with manifests.

```bash
python3 analysis/firmware_patch_tool.py inspect --firmware mpc2500_jv313.bin
```

Expected: exact bytes at known string targets are shown, with baseline SHA-256.

### Stage 1: Same-Length Cosmetic Patch (No Logic Change)

Apply a safe, late-UI string patch to prove your patch pipeline and media handling before trying behavior changes.

```bash
python3 analysis/firmware_patch_tool.py apply \
  --firmware mpc2500_jv313.bin \
  --spec analysis/patch_specs/poc_late_os_update.json \
  --output analysis/output/poc_late_os_update.bin \
  --manifest analysis/output/poc_late_os_update_manifest.json
```

This patch changes only one known late UI label at `0xC7D74`:
- `OS update` -> `OS MOD V1`

Both strings are 9 bytes. No file length or layout changes.

### Stage 2: Hardware Dry-Run (No Flash Commit Yet)

Goal: prove the unit loads the candidate file and reaches update UI with modified text, without committing flash.

Required evidence:
1. Storage medium prep method and filesystem type.
2. Filename used on media (start with `MPC2500.SOS`).
3. Device behavior sequence (photo/video):
   - boot/update entry
   - file detection/loading state
   - appearance of modified late label (if path reaches that UI)
4. Result classification:
   - accepted to update flow
   - rejected (`Wrong file`, `OS data error`, etc.)

If rejected, keep the manifest and firmware hash, and treat it as evidence for integrity enforcement.

### Stage 3: Integrity-Check Characterization

Design controlled A/B tests:
1. Patch one byte in late UI string region.
2. Patch one byte in unrelated region.
3. Patch one byte in very early region.

Each trial should differ by exactly one patch and one manifest. Compare acceptance/rejection behavior.

Decision rule:
- If every modified image is rejected, integrity check is global or header-coupled.
- If only certain regions fail, validation scope is constrained and can be mapped.

### Stage 4: Logic Feature Patch Candidates

Only after Stages 1-3 are reproducible:
1. Target small branch edits in already-mapped update control flow.
2. Keep patches minimal and individually attributable.
3. Collect manifests + hardware outcomes for every trial.

## Evidence Standards (strict)

Every claim should include:
1. Exact binary hash.
2. Exact patch spec and manifest.
3. Exact function/address references when making RE claims.
4. Hardware observation artifact (photo/video/log) for behavioral claims.

No evidence = no claim.

