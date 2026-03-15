# Flash Routine Proof Map (Run-11)

Target firmware: `analysis/mpc2500.bin`  
SHA-256: `6a09b1801f4c38c2f710028126b70290e907980aea35b18c6e66459004d089b5`

## Proven routine roles

### Erase-stage routine: `FUN_0000853e`

Evidence:
- Invoked in update flow (`0x00000e12` literal call target `0x0000853e`).
- Executes explicit controller command/wait sequence:
  - control-bit programming at device registers (offseted writes via context at `0xa4000100` family)
  - repeated readiness polling via `0x83b2` / `0x83d8` against MMIO status path (`0xba00001c`-related wait helper constants).
- Returns timeout/error code path (`r0=20`) and nonzero statuses that feed common status dispatch handling (`0x103e..0x1082`).

Interpretation:
- This is the first proven pre-program destructive stage with erase-like command sequencing and readiness waiting.

### Program-stage routine: `FUN_00008db4` (with `FUN_000084f8` + `FUN_0000844a`)

Evidence:
- Main staged call in update flow:
  - `0x00000f48` loads literal `0x8db4`, calls routine.
  - Nonzero return branches to status/error dispatch at `0x100a -> 0x16fc`.
- Internal behavior:
  - loops over transfer length (`r14`) and destination pointer (`r12`),
  - repeatedly calls low-level transfer primitive (`0x84f8` -> `0x844a`),
  - updates pointers and remaining count until completion.
- Address access pattern:
  - command/descriptor path over `a50072xx` + staging block around `ba000004`.

Interpretation:
- Proven bulk program/write stage in update path.

### Verify-stage routine: validation block in `ENTRY_INIT` (`0x00000d3a..0x00000d96`)

Evidence:
- Multiple compare mismatches branch into shared integrity error leg:
  - `0x00000d42 -> 0x00000dd0`
  - `0x00000d76 -> 0x00000dd0`
  - `0x00000d84 -> 0x00000dd0`
- Error display then loads `0x7c80` (`OS data error`).

Interpretation:
- Proven post-load verification/integrity-check stage.

## Error/status dispatch support

- `FUN_000016fc` uses 29-byte table at `0x7d81 + 29*index`.
- Rows 29/30/31 map to:
  - `Flash ROM erase error`
  - `Flash ROM write error`
  - `Flash ROM read error`

This table is used by update-flow error dispatch callsites (`0x100c`, `0x1036`, `0x1082`), supporting phase-specific flash failure reporting.
