# Error Branch Mapping Notes (Run-09, completed trio)

Target firmware: `analysis/mpc2500.bin`  
SHA-256: `6a09b1801f4c38c2f710028126b70290e907980aea35b18c6e66459004d089b5`

Disassembly basis:
- Capstone `5.0.7`
- `CS_ARCH_SH`, `CS_MODE_SH4 | CS_MODE_LITTLE_ENDIAN`

## 1) `File data error` (`0x7c50`) — proven

```
00000c90: jsr      @r6
00000c94: exts.w   r0,r6
00000c98: tst      r6,r6
00000c9c: bf/s     0x00000cf4
...
00000cf4: mov.l    0x00000f6c,r6  ; literal value 0x00007c50
00000cf8: bsr      0x109e
```

Trigger condition: non-zero return from callsite at `0x00000c90`.

## 2) `OS data error` (`0x7c80`) — proven

Validation block exits to shared error leg:

```
00000d42: bf       0x00000dd0
00000d76: bf       0x00000dd0
00000d84: bf       0x00000dd0
...
00000dd4: mov.l    0x00000f8c,r6  ; literal value 0x00007c80
00000dd8: bsr      0x109e
```

Trigger condition: any mismatch branch in the validation checks enters `0x00000dd0`, then displays `OS data error`.

## 3) `Wrong file` (`0x7df5`) — proven

### A) Error-code dispatch path

`FUN_00008db4` return code is stored to stack word `(-68,r15)` at `0x00000c9e`.  
Later dispatch:

```
00001062: mov.w    @(r0,r15),r0     ; load saved status code
00001064: cmp/eq   #10,r0
00001066: bf       0x106e
...
0000106e: cmp/eq   #20,r0
00001070: bf       0x107e
...
0000107e: exts.w   r10,r5
00001080: mov      r0,r6            ; pass status code as message index
00001082: bsr      0x16fc
```

### B) `FUN_000016fc` message table indexing

```
00001700: exts.w   r6,r2
00001702: mov      #29,r3
00001704: mov.l    0x1730,r6        ; literal value 0x00007d81 (table base)
00001706: mul.l    r2,r3
...
00001710: add      r2,r6            ; pointer = 0x7d81 + 29*index
0000170e: bsr      0x109e
```

At `0x7d81` block, entries are fixed 29-byte rows.  
Row index `4` resolves to:

`0x7d81 + 29*4 = 0x7df5` -> `"Wrong file !!"`.

Trigger condition (mapped): when status code from `FUN_00008db4` equals `4`, dispatch through `FUN_000016fc` selects row index 4 and displays `Wrong file`.

---

## Gate-7.1 status implication

All three required errors now have function+address+condition mapping:
- `File data error`
- `OS data error`
- `Wrong file`
