# Error Branch Mapping Notes (Run-08)

Target firmware: `analysis/mpc2500.bin`  
SHA-256: `6a09b1801f4c38c2f710028126b70290e907980aea35b18c6e66459004d089b5`

## Method

- Disassembly engine: Capstone `5.0.7`, `CS_ARCH_SH`, `CS_MODE_SH4 | CS_MODE_LITTLE_ENDIAN`
- Objective: map triggering branch/function conditions for:
  - `File data error`
  - `OS data error`
  - `Wrong file`

## 1) `File data error` mapping (proven)

### Key branch

```
00000c90: jsr      @r6
00000c94: exts.w   r0,r6
00000c98: tst      r6,r6
00000c9c: bf/s     0xcf4
```

Interpretation:
- `r0` from `jsr @r6` is converted to signed and tested.
- If non-zero (`bf`), branch goes to `0x00000cf4`.

### Error display load

```
00000cf4: mov.l    0xf6c,r6   ; pool 0x00000f6c = 0x00007c50
00000cf8: bsr      0x109e
```

`0x7c50` is `File data error`.

**Trigger condition (proven):** non-zero return from the pre-check routine at `0x00000c90` path causes `File data error` display.

---

## 2) `OS data error` mapping (proven)

### Validation mismatch branches

```
00000d3a: bsr      0x16ba
00000d40: tst      r2,r2
00000d42: bf       0xdd0

00000d74: cmp/eq   r2,r6
00000d76: bf       0xdd0

00000d82: cmp/eq   r2,r6
00000d84: bf       0xdd0
```

These are three mismatch exits into a shared error leg at `0x00000dd0`.

### Error display load

```
00000dd0: bsr      0x165e
00000dd4: mov.l    0xf8c,r6   ; pool 0x00000f8c = 0x00007c80
00000dd8: bsr      0x109e
```

`0x7c80` is `OS data error`.

**Trigger condition (proven):** any of the compared fields/checks failing in this validation block branches to `0x00000dd0`, then displays `OS data error`.

---

## 3) `Wrong file` mapping (not yet proven)

Known string addresses:
- `0x7df5` (early block)
- `0xb97a4` (late UI block duplicate)

Observed:
- Existing map artifact shows `wrong_file` refs: `0`.
- Full scan of SH PC-relative literal loads found direct loads for `0x7c50` and `0x7c80`, but **no direct literal load** for `0x7df5` or `0xb97a4`.

**Status:** unresolved. Likely table-driven/indirect text selection or alternate code path not captured by current static extraction.

---

## Gate-7.1 implication

- `File data error`: mapped with branch/function proof.
- `OS data error`: mapped with branch/function proof.
- `Wrong file`: **not yet mapped with branch/function proof**.

Therefore Gate 7.1 remains blocked.
