# SuperH Update Path Findings

## Proven architecture/import

- CPU family: `Renesas/Hitachi SH7727` (`HD6417727F160C`)
- Ghidra language that produced coherent analysis: `SuperH4:LE:32:default`
- Working raw-image base: `0x00000000`
- Reset flow: `RESET_STUB` at `0x00000000` jumps to `ENTRY_INIT` at `0x00000626`

## Proven string ownership

`ENTRY_INIT` directly references and/or displays:

- `MPC2500.SOS`
- `File data error`
- `OS data error`
- `====== MPC2500 OS UPDATE =======`
- `Loading OS file`
- `OS file not found`
- `Flash ROM erasing %`

## First valid/reject decision

The earliest concrete "is this an update file?" gate currently isolated is `FUN_00008c44`.

Evidence:

- `ENTRY_INIT` calls `FUN_00008c44` at `0x00000c38`
- On non-zero return it branches to the reject path at `0x00000d06`
- `FUN_00008c44` repeatedly calls `FUN_00008a10` to scan directory entries
- It then uses `FUN_000016ba` (case-insensitive string compare) to match:
  - `MPC2500`
  - `SOS`

In the same path, `ENTRY_INIT` also compares the full filename against `MPC2500.SOS` at `0x00000c4e` via `FUN_000016ba`.

## Alternate accepted filename patterns

`FUN_00008b8c` is a second-stage filename validator/scanner that also calls `FUN_00008a10` and `FUN_000016ba`.

Its literal pool contains:

- `M25V`
- `BIN`
- `MPC25T`
- `MPC2500`
- `SOS`

This strongly suggests the updater accepts multiple filename schemes, not just `MPC2500.SOS`.

## FAT/LFN parsing path

`FUN_00008a10` and `FUN_00008ca6` are not flash routines.

They are part of the FAT directory parsing path:

- `FUN_00008ca6` explicitly checks attribute `0x0f`, which matches VFAT long filename entries
- It reconstructs a filename into a working buffer
- `FUN_00008a10` scans candidate entries and calls `FUN_00008ca6`

## First low-level commit/programming candidate

The first low-level routine after filename acceptance is not yet proven to be flash programming, but the strongest current candidates are:

- `FUN_00008ed6`
- `FUN_00008db4`

Why:

- `ENTRY_INIT` calls `FUN_00008ed6` immediately after the first `MPC2500`/`SOS` validation stage
- `ENTRY_INIT` then calls `FUN_00008db4`
- `FUN_00008db4` calls `FUN_000084f8`, `FUN_000084e2`, and `FUN_0000844a`
- `FUN_00008ed6` calls `FUN_000084e2` and `FUN_0000844a`
- Those lower routines operate on `0xa50072xx` controller/state addresses and busy-wait helpers

Current confidence:

- High confidence: these are low-level device transaction routines
- Medium confidence: they are involved in update-file loading/commit flow
- Low confidence: they are the actual flash erase/write routines

## Additional proven literal/call evidence (raw-binary extractor)

A local raw-binary SuperH extractor (`analysis/extract_superh_update_path.py`) reproduces these points without depending on Ghidra runtime availability.

Proven from extracted call/literal traces:

- `ENTRY_INIT` includes resolved calls to:
  - `FUN_00008c44` (`0x00000c38`)
  - `FUN_00008ed6` (`0x00000c48`)
  - `FUN_00008db4` (`0x00000c90`, and again at `0x00000f4a`)
  - `FUN_00008b8c` (`0x00000e3a`)
- `FUN_00008b8c` loads literal strings:
  - `M25V` (`0x00009294`)
  - `BIN` (`0x0000929c`)
  - `MPC25T` (`0x000092a0`)
  - `MPC2500` (`0x000092a8`)
  - `SOS` (`0x000092b0`)
- `ENTRY_INIT` directly loads boot-error/status strings via long literals:
  - `File data error` (`0x00000cf4 -> 0x00007c50`)
  - `OS data error` (`0x00000dd4 -> 0x00007c80`)
  - `Loading OS file` (`0x00000f0e -> 0x00007cf8`)
  - `OS file not found` (`0x0000101e -> 0x00007d14`)
  - `Flash ROM erasing %` (`0x000008fa` and `0x00000904` -> `0x000094a0`)
- `FUN_00008db4`, `FUN_00008ed6`, `FUN_0000844a`, `FUN_000084e2`, and `FUN_000084f8` all load literals in the `0xa50072xx` region.

## Not yet proven

- Direct code references to:
  - `Flash ROM write error`
  - `Flash ROM erase error`
  - `Flash ROM read error`
  - `Flash ROM Writing %`
- The exact function that sends AMD flash command sequences to the `AM29LV641`
- The exact checksum / OS-data validation routine

## Error-string branch mapping status (run-08)

For target firmware `analysis/mpc2500.bin`, Capstone SH4 disassembly now proves:

- `File data error` (`0x7c50`) branch leg at `0x00000cf4`, reached when the pre-check return at `0x00000c90` is non-zero (`tst r6,r6` + `bf/s 0x00000cf4`).
- `OS data error` (`0x7c80`) branch leg at `0x00000dd4`, reached via mismatch branches to `0x00000dd0` from checks at `0x00000d42`, `0x00000d76`, and `0x00000d84`.

Still unresolved:

- `Wrong file` branch/function proof. Current static artifacts still show no direct xref for `0x7df5`, and no direct literal-load proof for the late duplicate string.

Detailed evidence notes: `analysis/output/error_branch_mapping_run08.md`.

## Error-string branch mapping status (run-09 update)

`Wrong file` is now branch-mapped for `analysis/mpc2500.bin`:

- status code from `FUN_00008db4` is dispatched at `0x1062..0x1082`
- non-10/non-20 codes route to `FUN_000016fc` with `r6 = status_code`
- `FUN_000016fc` indexes fixed-width table at `0x7d81` using `29 * index`
- index `4` resolves to `0x7df5` (`Wrong file !!`)

Detailed proof: `analysis/output/error_branch_mapping_run09.md`.

## Flash routine characterization status (run-10 update)

Strengthened evidence now proves:

- `FUN_000087a6` failure maps directly to message index `30` -> `Flash ROM write error` (`0x80e7`) via `0x1034 -> 0x16fc`.
- OS verify/integrity checks are proven in `0x00000d3a..0x00000dd8` (mismatch branches to `OS data error`).

Still pending for full gate closure:

- unique command-sequence proof that `FUN_0000853e` is erase (vs setup/probe) rather than a generic pre-write stage.

Detailed evidence notes: `analysis/output/flash_routine_characterization_run10.md`.

## Flash routine proof status (run-11)

Routine-role mapping is now formalized in `analysis/output/flash_routine_proof_run11.md`:

- Erase-stage: `FUN_0000853e` (controller command+wait sequencing in update flow)
- Program-stage: `FUN_00008db4` (bulk transfer loop through `FUN_000084f8`/`FUN_0000844a`)
- Verify-stage: validation block `0x00000d3a..0x00000d96` (`OS data error` mismatch leg)

Supporting dispatch table mapping for flash-specific error rows (29/30/31) is included in the same proof note.
