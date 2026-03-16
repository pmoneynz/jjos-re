# jjos-re

Reverse-engineering workspace for `JJOS` / `MPC2500` firmware, centered on the binary `mpc2500_jv313.bin`.

## Current State

- Firmware under analysis: `mpc2500_jv313.bin`
- Device CPU from service manual: `HD6417727F160C`
- Correct working RE import so far:
  - processor: `SuperH4:LE:32:default`
  - image base: `0x00000000`
  - reset flow: `0x00000000 -> 0x00000626`
- Best current findings are in:
  - `analysis/output/ghidra_sh_findings.md`
  - `analysis/output/ghidra_sh_update_map.md`

## Repo Contents

- `mpc2500_jv313.bin`
  - raw firmware image currently under analysis
- `analysis/scan_firmware.py`
  - static scanner for strings, pointer candidates, and coarse structure
- `analysis/ghidra_scripts/`
  - headless Ghidra scripts used to seed and report analysis
- `analysis/output/`
  - generated findings, maps, reports, and extracted string indexes
- `analysis/ghidra_project_sh/`
  - working Ghidra project using the SuperH import hypothesis

## Most Important Findings

- The earlier ColdFire hypothesis was wrong.
- The MPC2500 service manual identifies `IC1` as `HD6417727F160C`, a SuperH-family CPU.
- Under SuperH little-endian import, the binary produces coherent code and real update-path references.
- `ENTRY_INIT` at `0x00000626` owns the early update UI and file-loading flow.
- The earliest currently isolated valid/reject filename gate is `FUN_00008c44`.
- The strongest current low-level post-validation candidates are:
  - `FUN_00008ed6`
  - `FUN_00008db4`

## Resume Here

Read these first:

1. `analysis/output/ghidra_sh_findings.md`
2. `analysis/output/ghidra_sh_update_map.md`
3. `analysis/README.md`

Then continue from the current hypothesis:

1. Open `analysis/ghidra_project_sh/` in Ghidra.
2. Inspect `ENTRY_INIT` at `0x00000626`.
3. Follow these helper functions:
   - `FUN_00008c44`
   - `FUN_00008b8c`
   - `FUN_00008a10`
   - `FUN_00008ca6`
   - `FUN_00008ed6`
   - `FUN_00008db4`
4. Try to isolate:
   - the exact `valid OS file` / `reject` branch
   - the exact checksum / `OS data error` decision
   - the first true flash erase/write routine

## Reproduce Headless Analysis

The local machine used:

- Ghidra 12
- Java 21

Example headless import:

```bash
export JAVA_HOME="/Library/Java/JavaVirtualMachines/temurin-21.jdk/Contents/Home"
export PATH="$JAVA_HOME/bin:$PATH"
"/opt/homebrew/Cellar/ghidra/12.0/libexec/support/analyzeHeadless" \
  "/path/to/project_dir" JJOS_SH \
  -import "/path/to/mpc2500_jv313.bin" \
  -loader BinaryLoader \
  -loader-baseAddr 0x0 \
  -loader-blockName ROM \
  -processor SuperH4:LE:32:default \
  -scriptPath "/path/to/analysis/ghidra_scripts" \
  -preScript SeedSuperHEntry.py "/path/to/analysis/output/ghidra_sh_seed_report.tsv" \
  -postScript ReportSuperHUpdatePath.py "/path/to/analysis/output/ghidra_sh_update_map.md"
```

## Practical Patch Workflow (Current Best Path)

Use a strict, reproducible patch workflow before any hardware flash attempt:

1. Inspect known patch-safe string targets:
   - `python3 analysis/firmware_patch_tool.py inspect --firmware mpc2500_jv313.bin`
2. Build a same-length patch candidate from a JSON spec:
   - `python3 analysis/firmware_patch_tool.py apply --firmware mpc2500_jv313.bin --spec analysis/patch_specs/poc_late_os_update.json --output analysis/output/poc_late_os_update.bin --manifest analysis/output/poc_late_os_update_manifest.json`
3. Run staged hardware tests using:
   - `analysis/PRACTICAL_PATCH_PATH.md`

The patch helper refuses to patch unless expected bytes match exactly, which prevents drift and accidental corruption.

## Manual Knowledge Base

Manual-derived facts and constraints are tracked in:

- `analysis/knowledge_base/MANUAL_SOURCES.md`
- `analysis/knowledge_base/MANUAL_KNOWLEDGE_SUMMARY.md`
- `analysis/knowledge_base/manual_facts.json`

Use these before designing hardware trials so media, update-path, and USB assumptions stay consistent with documented behavior.

## Caution

This repo includes a proprietary firmware binary because that was explicitly requested for publication. That may have IP/legal implications depending on jurisdiction and intended use.
