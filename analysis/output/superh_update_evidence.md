# SuperH Update Evidence (Raw-Binary Extractor)

## Method

- Source: `mpc2500_jv313.bin`
- Technique: focused SuperH pattern extraction from known seed windows
- Classification policy:
  - **proven**: directly observed by decoded control-flow/literal evidence
  - **hypothesis**: plausible but not directly proven by current extraction

## Proven Calls from ENTRY_INIT

- `0x00000808` `bsr` -> `0x00000210` (resolution source: `relative`, status: `proven`)
- `0x00000818` `bsr` -> `0x00000210` (resolution source: `relative`, status: `proven`)
- `0x0000081e` `bsr` -> `0x00000210` (resolution source: `relative`, status: `proven`)
- `0x00000830` `bsr` -> `0x00000210` (resolution source: `relative`, status: `proven`)
- `0x00000866` `bsr` -> `0x0000041c` (resolution source: `relative`, status: `proven`)
- `0x000008f4` `bsr` -> `0x0000037c` (resolution source: `relative`, status: `proven`)
- `0x00000900` `bsr` -> `0x0000037c` (resolution source: `relative`, status: `proven`)
- `0x0000090a` `bsr` -> `0x0000037c` (resolution source: `relative`, status: `proven`)
- `0x00000910` `bsr` -> `0x000005ae` (resolution source: `relative`, status: `proven`)
- `0x00000914` `bsr` -> `0x000005b6` (resolution source: `relative`, status: `proven`)
- `0x00000918` `bsr` -> `0x000005ae` (resolution source: `relative`, status: `proven`)
- `0x0000091c` `bsr` -> `0x000005b6` (resolution source: `relative`, status: `proven`)
- `0x00000920` `bsr` -> `0x000005ae` (resolution source: `relative`, status: `proven`)
- `0x00000924` `bsr` -> `0x000005b6` (resolution source: `relative`, status: `proven`)
- `0x00000928` `bsr` -> `0x000005ae` (resolution source: `relative`, status: `proven`)
- `0x0000092c` `bsr` -> `0x000005b6` (resolution source: `relative`, status: `proven`)
- `0x00000930` `bsr` -> `0x000005ae` (resolution source: `relative`, status: `proven`)
- `0x00000936` `bsr` -> `0x000005ae` (resolution source: `relative`, status: `proven`)
- `0x0000093c` `bsr` -> `0x000005ae` (resolution source: `relative`, status: `proven`)
- `0x00000940` `bsr` -> `0x000005b6` (resolution source: `relative`, status: `proven`)
- `0x00000944` `bsr` -> `0x000005ae` (resolution source: `relative`, status: `proven`)
- `0x00000948` `bsr` -> `0x000005ae` (resolution source: `relative`, status: `proven`)
- `0x0000094c` `bsr` -> `0x000005de` (resolution source: `relative`, status: `proven`)
- `0x00000958` `bsr` -> `0x000005ae` (resolution source: `relative`, status: `proven`)
- `0x0000099c` `bsr` -> `0x000016ba` (resolution source: `relative`, status: `proven`)
- `0x00000a60` `bsr` -> `0x0000165e` (resolution source: `relative`, status: `proven`)
- `0x00000aa0` `bsr` -> `0x0000165e` (resolution source: `relative`, status: `proven`)
- `0x00000ab0` `bsr` -> `0x0000165e` (resolution source: `relative`, status: `proven`)
- `0x00000aba` `bsr` -> `0x00001358` (resolution source: `relative`, status: `proven`)
- `0x00000ac2` `bsr` -> `0x00001358` (resolution source: `relative`, status: `proven`)
- `0x00000acc` `bsr` -> `0x00001438` (resolution source: `relative`, status: `proven`)
- `0x00000ad6` `bsr` -> `0x00001438` (resolution source: `relative`, status: `proven`)
- `0x00000ae2` `bsr` -> `0x0000160c` (resolution source: `relative`, status: `proven`)
- `0x00000aea` `bsr` -> `0x000014a2` (resolution source: `relative`, status: `proven`)
- `0x00000af4` `bsr` -> `0x000015a0` (resolution source: `relative`, status: `proven`)
- `0x00000afe` `bsr` -> `0x000014a2` (resolution source: `relative`, status: `proven`)
- `0x00000b06` `bsr` -> `0x000015a0` (resolution source: `relative`, status: `proven`)
- `0x00000b10` `bsr` -> `0x00001438` (resolution source: `relative`, status: `proven`)
- `0x00000b18` `bsr` -> `0x00001438` (resolution source: `relative`, status: `proven`)
- `0x00000b20` `bsr` -> `0x00001438` (resolution source: `relative`, status: `proven`)
- `0x00000b28` `bsr` -> `0x00001438` (resolution source: `relative`, status: `proven`)
- `0x00000b48` `bsr` -> `0x0000115a` (resolution source: `relative`, status: `proven`)
- `0x00000b56` `bsr` -> `0x0000109e` (resolution source: `relative`, status: `proven`)
- `0x00000b6e` `bsr` -> `0x00001228` (resolution source: `relative`, status: `proven`)
- `0x00000b74` `bsr` -> `0x00001676` (resolution source: `relative`, status: `proven`)
- `0x00000bbc` `bsr` -> `0x0000109e` (resolution source: `relative`, status: `proven`)
- `0x00000bc0` `bsr` -> `0x00001676` (resolution source: `relative`, status: `proven`)
- `0x00000be8` `bsr` -> `0x00000606` (resolution source: `relative`, status: `proven`)
- `0x00000c18` `bsr` -> `0x000005f2` (resolution source: `relative`, status: `proven`)
- `0x00000c1e` `jsr` -> `0x0000853e` (resolution source: `0x00000c1c`, status: `proven`)
- `0x00000c28` `jsr` -> `0x000087a6` (resolution source: `0x00000c26`, status: `proven`)
- `0x00000c38` `jsr` -> `0x00008c44` (resolution source: `0x00000c34`, status: `proven`)
- `0x00000c48` `jsr` -> `0x00008ed6` (resolution source: `0x00000c42`, status: `proven`)
- `0x00000c54` `bsr` -> `0x000016ba` (resolution source: `relative`, status: `proven`)
- `0x00000c62` `bsr` -> `0x0000109e` (resolution source: `relative`, status: `proven`)
- `0x00000c66` `bsr` -> `0x00001676` (resolution source: `relative`, status: `proven`)
- `0x00000c86` `jsr` -> `0x00008c44` (resolution source: `0x00000c70`, status: `proven`)
- `0x00000c90` `jsr` -> `0x00008db4` (resolution source: `0x00000c8c`, status: `proven`)
- `0x00000ca6` `jsr` -> `None` (resolution source: `None`, status: `hypothesis`)
- `0x00000cf8` `bsr` -> `0x0000109e` (resolution source: `relative`, status: `proven`)
- `0x00000cfc` `bsr` -> `0x00001676` (resolution source: `relative`, status: `proven`)
- `0x00000d02` `bsr` -> `0x00000606` (resolution source: `relative`, status: `proven`)
- `0x00000d24` `bsr` -> `0x000016ba` (resolution source: `relative`, status: `proven`)
- `0x00000d2e` `bsr` -> `0x000005f2` (resolution source: `relative`, status: `proven`)
- `0x00000d3a` `bsr` -> `0x000016ba` (resolution source: `relative`, status: `proven`)
- `0x00000d8e` `bsr` -> `0x000016ba` (resolution source: `relative`, status: `proven`)
- `0x00000d98` `bsr` -> `0x000005f2` (resolution source: `relative`, status: `proven`)
- `0x00000dc6` `jsr` -> `None` (resolution source: `None`, status: `hypothesis`)
- `0x00000dd0` `bsr` -> `0x0000165e` (resolution source: `relative`, status: `proven`)
- `0x00000dd8` `bsr` -> `0x0000109e` (resolution source: `relative`, status: `proven`)
- `0x00000ddc` `bsr` -> `0x00001676` (resolution source: `relative`, status: `proven`)
- `0x00000de2` `bsr` -> `0x00000606` (resolution source: `relative`, status: `proven`)
- `0x00000e06` `bsr` -> `0x0000165e` (resolution source: `relative`, status: `proven`)
- `0x00000e0e` `bsr` -> `0x0000109e` (resolution source: `relative`, status: `proven`)
- `0x00000e14` `jsr` -> `0x0000853e` (resolution source: `0x00000e12`, status: `proven`)
- `0x00000e2a` `jsr` -> `0x000087a6` (resolution source: `0x00000e28`, status: `proven`)
- `0x00000e3a` `jsr` -> `0x00008b8c` (resolution source: `0x00000e38`, status: `proven`)
- `0x00000e50` `bsr` -> `0x0000109e` (resolution source: `relative`, status: `proven`)
- `0x00000e58` `bsr` -> `0x0000109e` (resolution source: `relative`, status: `proven`)
- `0x00000e62` `bsr` -> `0x0000109e` (resolution source: `relative`, status: `proven`)
- `0x00000e6a` `jsr` -> `0x0000914c` (resolution source: `0x00000e68`, status: `proven`)
- `0x00000e86` `bsr` -> `0x0000109e` (resolution source: `relative`, status: `proven`)
- `0x00000e94` `bsr` -> `0x0000109e` (resolution source: `relative`, status: `proven`)
- `0x00000eac` `bsr` -> `0x00001358` (resolution source: `relative`, status: `proven`)
- `0x00000eb8` `bsr` -> `0x0000160c` (resolution source: `relative`, status: `proven`)
- `0x00000ec2` `bsr` -> `0x0000109e` (resolution source: `relative`, status: `proven`)
- `0x00000ec6` `bsr` -> `0x00001676` (resolution source: `relative`, status: `proven`)
- `0x00000edc` `bsr` -> `0x00000606` (resolution source: `relative`, status: `proven`)
- `0x00000f0a` `bsr` -> `0x0000165e` (resolution source: `relative`, status: `proven`)
- `0x00000f14` `bsr` -> `0x0000109e` (resolution source: `relative`, status: `proven`)
- `0x00000f18` `bsr` -> `0x00001676` (resolution source: `relative`, status: `proven`)
- `0x00000f38` `bsr` -> `0x000016ba` (resolution source: `relative`, status: `proven`)
- `0x00000f4a` `jsr` -> `0x00008db4` (resolution source: `0x00000f48`, status: `proven`)
- `0x00000f56` `jsr` -> `0xa50070ac` (resolution source: `0x00000f54`, status: `proven`)
- `0x00000f62` `bsr` -> `0x000016ba` (resolution source: `relative`, status: `proven`)
- `0x00000ff6` `jsr` -> `None` (resolution source: `None`, status: `hypothesis`)
- `0x00001002` `bsr` -> `0x000005f2` (resolution source: `relative`, status: `proven`)
- `0x0000100c` `bsr` -> `0x000016fc` (resolution source: `relative`, status: `proven`)
- `0x00001010` `bsr` -> `0x00001676` (resolution source: `relative`, status: `proven`)
- `0x00001016` `bsr` -> `0x00000606` (resolution source: `relative`, status: `proven`)
- `0x00001022` `bsr` -> `0x0000109e` (resolution source: `relative`, status: `proven`)
- `0x00001026` `bsr` -> `0x00001676` (resolution source: `relative`, status: `proven`)
- `0x0000102c` `bsr` -> `0x00000606` (resolution source: `relative`, status: `proven`)
- `0x00001036` `bsr` -> `0x000016fc` (resolution source: `relative`, status: `proven`)
- `0x00001046` `bsr` -> `0x0000109e` (resolution source: `relative`, status: `proven`)
- `0x00001050` `bsr` -> `0x0000115a` (resolution source: `relative`, status: `proven`)
- `0x0000105a` `bsr` -> `0x0000115a` (resolution source: `relative`, status: `proven`)

### Required-call checks

- target `0x00008c44`: FOUND (**proven**)
- target `0x00008ed6`: FOUND (**proven**)
- target `0x00008db4`: FOUND (**proven**)
- target `0x00008b8c`: FOUND (**proven**)

## Proven Alternate Filename Literal Set (FUN_00008b8c)

- `0x00009294` -> `M25V` (loaded at `0x00008bb0`)
- `0x0000929c` -> `BIN` (loaded at `0x00008bfe`)
- `0x000092a0` -> `MPC25T` (loaded at `0x00008bd0`)
- `0x000092a8` -> `MPC2500` (loaded at `0x00008c0c`)
- `0x000092b0` -> `SOS` (loaded at `0x00008c1c`)

### Expected-set checks

- `BIN`: FOUND (**proven**)
- `M25V`: FOUND (**proven**)
- `MPC2500`: FOUND (**proven**)
- `MPC25T`: FOUND (**proven**)
- `SOS`: FOUND (**proven**)

## Proven Direct Error-String Literal References (ENTRY_INIT window)

- `File data error` at `0x00007c50` refs: `0x00000cf4` (**proven**)
- `OS data error` at `0x00007c80` refs: `0x00000dd4` (**proven**)
- `Loading OS file` at `0x00007cf8` refs: `0x00000f0e` (**proven**)
- `OS file not found` at `0x00007d14` refs: `0x0000101e` (**proven**)
- `Flash ROM erasing %` at `0x000094a0` refs: `0x000008fa, 0x00000904` (**proven**)

## Proven MMIO/Controller Literal Touchpoints (`0xa50072xx`)

- `FUN_00008db4`: 0xa5007230, 0xa5007244, 0xa500725c, 0xa5007288, 0xa5007290
- `FUN_00008ed6`: 0xa5007230, 0xa5007290
- `FUN_0000844a`: 0xa5007250
- `FUN_000084e2`: 0xa5007284, 0xa500728c, 0xa5007290
- `FUN_000084f8`: 0xa5007234, 0xa5007238, 0xa5007248, 0xa5007260, 0xa5007290

## Current Hypotheses / Unresolved

- No direct long-literal references were extracted for `Wrong file` / flash erase-write-read error strings in the boot block; these are likely reached indirectly through table/index flow.
- The `0xa50072xx` touchpoints in `FUN_00008db4`/`FUN_00008ed6`/`FUN_000084x` strongly indicate low-level transaction control, but this extractor does not yet prove exact AM29LV641 erase/program command semantics.

