# Flash Routine Characterization Notes (Run-10, strengthened)

Target firmware: `analysis/mpc2500.bin`  
SHA-256: `6a09b1801f4c38c2f710028126b70290e907980aea35b18c6e66459004d089b5`

## New hard evidence in this run

### 1) Program/write routine linkage (proven)

Call chain around `ENTRY_INIT`:

```
00000e28: mov.l 0xfa0,r2   ; literal -> 0x000087a6
00000e2a: jsr   @r2
...
00000e30: tst   r6,r6
00000e32: bt    0x00000e38
00000e34: bra   0x00001034
```

Failure branch at `0x1034` immediately dispatches message index `30` via `FUN_000016fc`:

```
00001034: mov   #45,r4
00001036: bsr   0x16fc
00001038: exts.w r10,r5   ; r10 = 30
```

Message table index `30` resolves to `0x80e7` (`Flash ROM write error`).

**Conclusion:** `FUN_000087a6` is directly tied to the write/program failure path.

---

### 2) Verify routine linkage (proven, file/OS integrity verify)

Validation block (`0x00000d3a` onward) compares multiple fields/checks and branches to `0x00000dd0` on mismatch:

- `0x00000d42 -> 0x00000dd0`
- `0x00000d76 -> 0x00000dd0`
- `0x00000d84 -> 0x00000dd0`

At `0x00000dd4`, string pointer `0x7c80` (`OS data error`) is displayed.

**Conclusion:** this is a proven verify/integrity-check stage in update flow.

---

### 3) Erase routine status (still not fully proven)

`FUN_0000853e` runs immediately before `FUN_000087a6`, uses the same low-level transaction helpers (`0x83b2`, `0x8398`, `0x83fe`, `0x844a`) and MMIO context, and returns status codes propagated through update error dispatch.

However, explicit command-sequence proof that uniquely labels it as *erase* (vs setup/probe/prepare) is still incomplete in current static evidence.

---

## Low-level access pattern evidence (supporting)

- MMIO/controller constants in this path include:
  - `a50072xx` region (`a5007230`, `a5007244`, `a500725c`, `a5007290`, etc.)
  - command/data staging around `ba000004` and read stream from `ba000000` style access
- `FUN_0000844a` builds transaction descriptors and uses helper waits/transfers (`0x8398`, `0x83fe`).

---

## Gate 7.2 implication (run-10)

- Program routine: **proven** (`FUN_000087a6`)
- Verify routine: **proven** (OS data integrity check block)
- Erase routine: **strong candidate but not yet command-proven**

Gate 7.2 remains blocked pending explicit erase-command proof.
