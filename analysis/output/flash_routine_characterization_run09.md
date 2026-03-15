# Flash Routine Characterization Notes (Run-09)

Target firmware: `analysis/mpc2500.bin`  
SHA-256: `6a09b1801f4c38c2f710028126b70290e907980aea35b18c6e66459004d089b5`

## Summary

Current evidence strongly supports:
- erase/program dispatch through `FUN_00008ed6` / `FUN_00008db4`
- low-level transaction engine in `FUN_0000844a` (with helpers `FUN_000084e2`, `FUN_000084f8`)

But full **erase/program/verify** proof at command-sequence level is still incomplete.

## Literal evidence for controller/MMIO context

From low-level literal pool:

- `0x85d8 -> 0xa5007250`
- `0x85dc -> 0xba000004`
- `0x85e0 -> 0xa5007290`
- `0x85e4 -> 0xa500728c`
- `0x85e8 -> 0xa5007284`
- `0x85ec -> 0xa5007260`
- `0x85f0 -> 0xa5007248`
- `0x85f4 -> 0xa5007238`
- `0x85f8 -> 0xa5007234`

These are consistent with a memory-mapped storage/flash controller transaction path.

## Candidate routine roles (with evidence)

### 1) `FUN_00008ed6` (likely erase/setup stage)

- Called before main loop in update path.
- If context length is zero, returns `4`.
- Otherwise:
  - updates context register/state (`a5007290` path),
  - computes mapped offset via `FUN_000084e2`,
  - calls `FUN_0000844a` with `r6=1` (single unit transaction).

Interpretation: single-unit pre-write operation consistent with erase/setup semantics.

### 2) `FUN_00008db4` (likely program loop + status return)

- Main loop calls `FUN_000084f8`, which computes offset and then calls `FUN_0000844a` with chunk-size from controller context.
- Loop updates source/destination pointers and remaining bytes.
- Returns status codes consumed by higher-level error dispatch (`0x1062..0x1082` path).

Interpretation: primary programming/transfer loop.

### 3) `FUN_0000844a` (low-level transaction engine)

- Builds structured command block at MMIO window (`0xba000004`).
- Encodes source/destination/length fields.
- Calls helper routines (`0x8398`, `0x83fe`) and loops until transfer complete.

Interpretation: device transaction primitive used by both pre-write and main-loop stages.

## Why Gate 7.2 is still blocked

Checklist requires explicit proof of **erase + program + verify** routines by command-sequence behavior and access pattern.

What is still missing:
- explicit command-value mapping that uniquely labels one routine as erase, one as program, one as verify,
- or hardware-correlated traces showing verify call path distinct from program path.

Therefore this note supports strong candidates but does not close 7.2 yet.
