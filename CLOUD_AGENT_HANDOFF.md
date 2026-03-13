# Cloud Agent Handoff

This repo is the active reverse-engineering workspace for the `JJOS` / `MPC2500` firmware binary `mpc2500_jv313.bin`.

Your job is to continue autonomously until the reverse engineering is as complete as practically possible.

Do not restart from scratch. Build directly on the current findings and artifacts in this repo.

## Mission

Reverse engineer the MPC2500 JJOS update binary deeply enough to answer, with evidence:

1. How the update file is discovered and accepted or rejected.
2. What exact filename patterns and file-layout rules are accepted.
3. What routine performs update-file validation and what checks it applies.
4. What routine performs flash erase/program/read-back.
5. What conditions trigger:
   - `File data error`
   - `OS data error`
   - `Wrong file`
   - `Flash ROM erase error`
   - `Flash ROM write error`
   - `Flash ROM read error`
6. Whether and how a modified firmware image could be accepted and flashed.

## Ground Truth

These points are already established and should be treated as proven unless you falsify them with stronger evidence.

### Hardware / CPU

- Target device: `Akai MPC2500`
- CPU from service manual: `HD6417727F160C`
- CPU family: `Renesas/Hitachi SH7727`
- Architecture family: `SuperH`

Relevant service-manual facts already identified:

- Flash ROM part on CPU board: `AM29LV641DL90REI`
- CPU board identifier includes:
  - `IC1 = HD6417727F160C`
  - `IC2 = AM29LV641DL90REI`

### Import Settings That Work

The earlier ColdFire hypothesis was wrong. Do not continue from the ColdFire Ghidra project except as a record of failed assumptions.

Current working import:

- Ghidra language: `SuperH4:LE:32:default`
- Raw binary base: `0x00000000`

This is not a claim that the CPU is literally SH-4. It is the best currently available Ghidra language that produces coherent code for this SH-family binary.

### Proven Entry Flow

- `RESET_STUB` at `0x00000000`
- `ENTRY_INIT` at `0x00000626`
- Reset stub jumps into `ENTRY_INIT`

### Proven Early Update/UI Ownership

`ENTRY_INIT` directly references or displays:

- `MPC2500.SOS`
- `File data error`
- `OS data error`
- `====== MPC2500 OS UPDATE =======`
- `Loading OS file`
- `OS file not found`
- `Flash ROM erasing %`

### Proven Validation/File-Selection Path

The following are now meaningfully classified:

- `FUN_00008a10`
  - directory scan / candidate-entry iterator
- `FUN_00008ca6`
  - VFAT long filename parsing / reconstruction
  - explicitly checks attribute `0x0f`, consistent with VFAT long filename entries
- `FUN_00008c44`
  - earliest currently isolated valid/reject filename gate
  - called from `ENTRY_INIT`
  - non-zero return leads to reject path
  - matches `MPC2500` and `SOS`
- `FUN_00008b8c`
  - alternate filename validator/scanner
  - literal pool includes:
    - `M25V`
    - `BIN`
    - `MPC25T`
    - `MPC2500`
    - `SOS`

That strongly suggests the updater accepts multiple naming conventions, not just `MPC2500.SOS`.

### Strongest Current Low-Level Commit Candidates

These are the strongest currently isolated post-validation low-level routines:

- `FUN_00008ed6`
- `FUN_00008db4`

They are not yet proven flash-programming functions, but they are the best current lead.

They call into:

- `FUN_000084e2`
- `FUN_0000844a`
- `FUN_000084f8`

Those lower functions operate on `0xa50072xx` state/controller addresses and busy-wait style logic.

## Files To Read First

Read these before making new claims:

1. `README.md`
2. `analysis/README.md`
3. `analysis/output/ghidra_sh_findings.md`
4. `analysis/output/ghidra_sh_update_map.md`
5. `analysis/output/report.md`
6. `analysis/output/summary.json`

Then inspect:

- `analysis/ghidra_scripts/`
- `analysis/ghidra_project_sh/`

## Existing Ghidra Artifacts

Important outputs already generated:

- `analysis/output/ghidra_sh_seed_report.tsv`
- `analysis/output/ghidra_sh_update_map.md`
- `analysis/output/ghidra_sh_findings.md`

Important scripts:

- `analysis/ghidra_scripts/SeedSuperHEntry.py`
- `analysis/ghidra_scripts/ReportSuperHUpdatePath.py`

## What Was Wrong Earlier

Do not waste time repeating these mistakes.

- ColdFire/68000 hypothesis: wrong
- ColdFire Ghidra import: misleading garbage
- Old `0x09000000` base assumption: wrong for the working SuperH analysis

The correct working hypothesis is:

- SuperH family
- little-endian
- image base `0x00000000`

## Known Evidence Snippets

### Current valid/reject gate

`FUN_00008c44` is the earliest concrete filename gate currently isolated.

It is called from `ENTRY_INIT` and compares entry names using `FUN_000016ba`:

- `MPC2500`
- `SOS`

`ENTRY_INIT` also compares full filename against `MPC2500.SOS`.

### Alternate update filenames

`FUN_00008b8c` uses literal pool values:

- `M25V`
- `BIN`
- `MPC25T`
- `MPC2500`
- `SOS`

Interpretation:

- likely supports factory or alternate update/test naming schemes
- likely relevant to service-manual update filename variants like `M25V100B.BIN`

## Current Unknowns

These are the main unresolved questions.

1. Exact file-format validation logic
2. Exact checksum / integrity check routine
3. Exact branching condition for:
   - `File data error`
   - `OS data error`
   - `Wrong file`
4. Exact flash-erase and flash-program routines
5. Exact use of the `AM29LV641` command set in code
6. Whether write-progress and flash-error strings are reached through:
   - direct refs
   - computed tables
   - indirect function pointers
   - alternate boot/test/update paths

## Recommended Work Plan

Proceed in this order.

### Phase 1: Lock Down The Validation Path

Goal: prove the full decision chain from directory entry to accepted update payload.

Tasks:

1. Fully annotate:
   - `FUN_00008a10`
   - `FUN_00008ca6`
   - `FUN_00008c44`
   - `FUN_00008b8c`
2. Name buffers and globals used for:
   - candidate filename
   - reconstructed long filename
   - extension comparison
   - selected file metadata
3. Determine exactly:
   - which filenames are accepted
   - whether directory entries are filtered by attributes
   - whether file size or cluster chain is checked at selection time
4. Identify the first routine after selection that reads the file body.

Deliverable:

- a written mini-map of update-file selection, with exact function names and branch meanings

### Phase 2: Isolate Payload Validation

Goal: find the first routine that decides “valid OS data” vs “reject”.

Tasks:

1. Trace from `ENTRY_INIT` call sites around:
   - `0x00000c38`
   - `0x00000c48`
   - `0x00000c90`
   - `0x00000e38`
   - `0x00000f4a`
2. Identify where `File data error` and `OS data error` are emitted.
3. Work backward from those string references to the branch conditions.
4. Determine whether validation is:
   - header signature check
   - size/range check
   - checksum/CRC
   - flash model/version compatibility check
   - all of the above

Deliverable:

- exact validation routine(s), expected inputs, and failure branches

### Phase 3: Isolate Flash Programming

Goal: identify the first routine that actually erases or programs the flash chip.

Tasks:

1. Pivot from:
   - `FUN_00008ed6`
   - `FUN_00008db4`
   - `FUN_000084f8`
   - `FUN_000084e2`
   - `FUN_0000844a`
2. Search for flash-command patterns consistent with `AM29LV641`.
3. Look for:
   - unlock sequences
   - erase command sequences
   - polling loops
   - status-bit checks
   - post-write verification
4. Determine which routines touch actual memory-mapped flash addresses versus controller/driver state buffers.

Deliverable:

- first proven erase routine
- first proven write routine
- first proven read-back or verify routine

### Phase 4: Patchability Assessment

Goal: determine how a modified firmware image could be accepted.

Tasks:

1. Find integrity enforcement point(s).
2. Determine whether update acceptance depends on:
   - filename only
   - internal header fields
   - checksum/signature
   - version/device identifiers
3. Propose the smallest safe proof-of-concept patch.
4. Prefer cosmetic same-length patches first.

Deliverable:

- realistic patch strategy with risks

## Naming Conventions For Continued Work

Please rename important functions as you prove them.

Suggested names:

- `scan_update_dir_entries`
- `parse_vfat_long_filename`
- `match_primary_update_filename`
- `match_alternate_update_filename`
- `load_selected_update_file`
- `validate_update_payload`
- `flash_commit_prepare`
- `flash_erase_block`
- `flash_program_page`
- `flash_verify_program`

Do not assign optimistic names without evidence.

## Standards For Claims

Be strict.

- If something is proven by disassembly and control flow, say it is proven.
- If something is likely but not proven, label it as hypothesis.
- Do not collapse “device I/O” into “flash write” unless you can show actual flash-targeted command behavior.

## Practical Tips

- The current Ghidra project already has the useful import.
- Reuse it rather than rebuilding unless you need a clean comparison.
- Keep producing markdown artifacts in `analysis/output/` so progress survives agent restarts.
- Prefer adding small targeted scripts over manually repeating Ghidra tasks.

## Completion Criteria

The task is not complete until you can provide:

1. A validated control-flow narrative from boot-update screen to accepted file.
2. Exact validation routine(s) and what they check.
3. Exact flash erase/program/verify routine(s).
4. Exact failure branches for update rejection and flash failure.
5. A realistic path to creating a modified accepted image.

## Final Note

Right now the most important proven pivot is:

- `ENTRY_INIT` -> `FUN_00008c44` / `FUN_00008b8c` -> `FUN_00008ed6` / `FUN_00008db4`

That is the spine of the remaining reverse engineering work.
