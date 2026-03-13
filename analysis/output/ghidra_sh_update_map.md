# SuperH Update Path Map

- Program: `mpc2500_jv313.bin`
- Language: `SuperH4:LE:32:default`
- Image base: `0x00000000`

## String Reference Summary

- `update_filename_mpc2500_sos` at `0x7c20` refs: `2`
- `file_data_error` at `0x7c50` refs: `2`
- `os_data_error` at `0x7c80` refs: `2`
- `boot_update_title` at `0x7c9c` refs: `2`
- `boot_loading_os_file` at `0x7cf8` refs: `2`
- `boot_os_file_not_found` at `0x7d14` refs: `2`
- `wrong_file` at `0x7df5` refs: `0`
- `boot_file_write_error` at `0x7fa8` refs: `0`
- `boot_flash_erase_error` at `0x80ca` refs: `0`
- `boot_flash_write_error` at `0x80e7` refs: `0`
- `boot_flash_read_error` at `0x8104` refs: `0`
- `progress_erase` at `0x94a0` refs: `4`
- `progress_write` at `0x94b8` refs: `0`
- `late_not_os_file` at `0xc7d58` refs: `0`
- `late_os_update` at `0xc7d74` refs: `0`
- `late_osxl_update` at `0xc7e74` refs: `0`

## Functions Touching Update Strings

### `RESET_STUB`

- Entry: `00000000`
- Tags: `-`
- Ref sites: `-`
- Callers: `-`
- Callees: `ENTRY_INIT@00000626`

### `ENTRY_INIT`

- Entry: `00000626`
- Tags: `boot_loading_os_file, boot_os_file_not_found, boot_update_title, file_data_error, os_data_error, progress_erase, update_filename_mpc2500_sos`
- Ref sites: `000008fa, 00000904, 00000c4e, 00000cf4, 00000dd4, 00000e0a, 00000f0e, 0000101e`
- Callers: `00000002`
- Callees: `FUN_00000210@00000210, FUN_0000041c@0000041c, thunk_FUN_0000038a@0000037c, FUN_000005ae@000005ae, FUN_000005b6@000005b6, FUN_000005de@000005de, FUN_000016ba@000016ba, FUN_0000165e@0000165e, FUN_00001358@00001358, FUN_00001438@00001438, FUN_0000160c@0000160c, FUN_000014a2@000014a2, FUN_000015a0@000015a0, FUN_0000115a@0000115a, FUN_0000109e@0000109e, FUN_00001228@00001228, FUN_00001676@00001676, FUN_00000606@00000606, FUN_000005f2@000005f2, FUN_0000853e@0000853e, FUN_000087a6@000087a6, FUN_00008c44@00008c44, FUN_00008ed6@00008ed6, FUN_00008db4@00008db4, FUN_00008b8c@00008b8c, FUN_0000914c@0000914c, SUB@a50070ac, FUN_000016fc@000016fc`

## Focus Helpers

### `ENTRY_INIT`

- Address: `0x626`
- Function: `ENTRY_INIT`
- Entry: `00000626`
- Tags: `boot_loading_os_file, boot_os_file_not_found, boot_update_title, file_data_error, os_data_error, progress_erase, update_filename_mpc2500_sos`
- Ref sites: `000008fa, 00000904, 00000c4e, 00000cf4, 00000dd4, 00000e0a, 00000f0e, 0000101e`
- Callers: `00000002`
- Callees: `FUN_00000210@00000210, FUN_0000041c@0000041c, thunk_FUN_0000038a@0000037c, FUN_000005ae@000005ae, FUN_000005b6@000005b6, FUN_000005de@000005de, FUN_000016ba@000016ba, FUN_0000165e@0000165e, FUN_00001358@00001358, FUN_00001438@00001438, FUN_0000160c@0000160c, FUN_000014a2@000014a2, FUN_000015a0@000015a0, FUN_0000115a@0000115a, FUN_0000109e@0000109e, FUN_00001228@00001228, FUN_00001676@00001676, FUN_00000606@00000606, FUN_000005f2@000005f2, FUN_0000853e@0000853e, FUN_000087a6@000087a6, FUN_00008c44@00008c44, FUN_00008ed6@00008ed6, FUN_00008db4@00008db4, FUN_00008b8c@00008b8c, FUN_0000914c@0000914c, SUB@a50070ac, FUN_000016fc@000016fc`

### `scan_candidate_entries`

- Address: `0x8a10`
- Function: `FUN_00008a10`
- Entry: `00008a10`
- Tags: `-`
- Ref sites: `-`
- Callers: `00008ba0, 00008c2c, 00008c58, 00008c8e`
- Callees: `FUN_000091a8@000091a8, FUN_00009140@00009140, FUN_000082ec@000082ec, FUN_000082c8@000082c8, FUN_00008ca6@00008ca6`

### `open_or_validate_stage_a`

- Address: `0x8b8c`
- Function: `FUN_00008b8c`
- Entry: `00008b8c`
- Tags: `-`
- Ref sites: `-`
- Callers: `00000e3a`
- Callees: `FUN_00008a10@00008a10, FUN_000016ba@000016ba`

### `open_or_validate_stage_b`

- Address: `0x8c44`
- Function: `FUN_00008c44`
- Entry: `00008c44`
- Tags: `-`
- Ref sites: `-`
- Callers: `00000c38, 00000c86`
- Callees: `FUN_00008a10@00008a10, FUN_000016ba@000016ba`

### `commit_or_range_check`

- Address: `0x8db4`
- Function: `FUN_00008db4`
- Entry: `00008db4`
- Tags: `-`
- Ref sites: `-`
- Callers: `00000c90, 00000f4a`
- Callees: `FUN_000084f8@000084f8, FUN_000084e2@000084e2, FUN_0000844a@0000844a`

### `device_write_stage`

- Address: `0x8ed6`
- Function: `FUN_00008ed6`
- Entry: `00008ed6`
- Tags: `-`
- Ref sites: `-`
- Callers: `00000c48`
- Callees: `FUN_000084e2@000084e2, FUN_0000844a@0000844a`

## Raw Reference Lists

### `update_filename_mpc2500_sos`

- Address: `0x7c20`
- Refs: `00000c4e, 00000ce4`

### `file_data_error`

- Address: `0x7c50`
- Refs: `00000cf4, 00000f6c`

### `os_data_error`

- Address: `0x7c80`
- Refs: `00000dd4, 00000f8c`

### `boot_update_title`

- Address: `0x7c9c`
- Refs: `00000e0a, 00000f98`

### `boot_loading_os_file`

- Address: `0x7cf8`
- Refs: `00000f0e, 00000fc0`

### `boot_os_file_not_found`

- Address: `0x7d14`
- Refs: `0000101e, 00001260`

### `wrong_file`

- Address: `0x7df5`
- Refs: `-`

### `boot_file_write_error`

- Address: `0x7fa8`
- Refs: `-`

### `boot_flash_erase_error`

- Address: `0x80ca`
- Refs: `-`

### `boot_flash_write_error`

- Address: `0x80e7`
- Refs: `-`

### `boot_flash_read_error`

- Address: `0x8104`
- Refs: `-`

### `progress_erase`

- Address: `0x94a0`
- Refs: `000008fa, 00000904, 00000a2c, 00000a34`

### `progress_write`

- Address: `0x94b8`
- Refs: `-`

### `late_not_os_file`

- Address: `0xc7d58`
- Refs: `-`

### `late_os_update`

- Address: `0xc7d74`
- Refs: `-`

### `late_osxl_update`

- Address: `0xc7e74`
- Refs: `-`

