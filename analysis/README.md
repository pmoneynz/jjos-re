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
   - `python3 analysis/extract_superh_update_path.py mpc2500_jv313.bin --output-dir analysis/output`
2. Review the generated report and strings:
   - `analysis/output/report.md`
   - `analysis/output/superh_update_evidence.md`
   - `analysis/output/interesting_strings.tsv`
   - `analysis/output/strings.tsv`
3. Use the current proven import baseline in Ghidra:
   - language: `SuperH4:LE:32:default`
   - raw binary base address: `0x00000000`
   - seed flow: `RESET_STUB (0x00000000) -> ENTRY_INIT (0x00000626)`
4. Pivot on the update strings first:
   - boot/update text around `0x7BE0-0x8130`
   - flash progress text at `0x94A0` and `0x94B8`
   - late UI/update text around `0xC7D40-0xD3230`
5. Do not start with behavior changes.
   - First prove you can make a same-length cosmetic patch.
   - Then identify the integrity check that accepts or rejects the image.

## Notes on superseded assumptions

- The older ColdFire/`0x09000000` workflow is retained in some legacy artifacts for historical context only.
- Treat it as a disproven path unless new stronger evidence appears.

## Local Tooling

If you want lightweight byte-level corroboration without launching Ghidra, the repository-local extractor is enough:

```bash
python3 analysis/extract_superh_update_path.py mpc2500_jv313.bin --output-dir analysis/output
```

If you still want optional historical M68k probing for comparison experiments, create a workspace-local venv with `capstone`:

```bash
python3 -m venv .venv
./.venv/bin/pip install capstone
```

Use the Capstone output only as secondary context; do not treat it as the active architecture baseline.
