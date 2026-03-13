# JJOS Reverse Engineering Workflow

This directory turns the one-off binary inspection into something repeatable.

## Files

- `scan_firmware.py`: extracts structural data from `mpc2500_jv313.bin`
- `output/report.md`: current human-readable summary
- `output/summary.json`: machine-readable scan output
- `output/strings.tsv`: all printable strings with file offsets
- `output/interesting_strings.tsv`: keyword-filtered strings grouped into RE-relevant categories

## Recommended Workflow

1. Start with the static scan:
   - `python3 analysis/scan_firmware.py mpc2500_jv313.bin`
2. Review the generated report and strings:
   - `analysis/output/report.md`
   - `analysis/output/interesting_strings.tsv`
   - `analysis/output/strings.tsv`
3. Use the strongest current import hypothesis in a disassembler:
   - architecture: `68000:BE:32:Coldfire`
   - base address: `0x09000000`
4. Pivot on the update strings first:
   - boot/update text around `0x7BE0-0x8130`
   - flash progress text at `0x94A0` and `0x94B8`
   - late UI/update text around `0xC7D40-0xD3230`
5. Do not start with behavior changes.
   - First prove you can make a same-length cosmetic patch.
   - Then identify the integrity check that accepts or rejects the image.

## Local Tooling

If you want lightweight M68k probing without full Ghidra setup, a workspace-local venv with `capstone` is enough:

```bash
python3 -m venv .venv
./.venv/bin/pip install capstone
```

Ghidra support for ColdFire is present locally, but Java still needs to be configured before headless analysis will work.
