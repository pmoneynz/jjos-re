#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import struct
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable


PRINTABLE_RE = re.compile(rb"[ -~]{4,}")

FEATURE_KEYWORDS = {
    "update_flash": [
        "flash rom",
        "os update",
        "os-xl update",
        "writes os",
        "not mpc2500 os file",
        "os file",
        "write error",
        "read  error",
        "erase error",
    ],
    "storage_filesystem": [
        "fat12",
        "fat16",
        "fat32",
        "msdos5.0",
        "compactflash",
        "hard disk",
        "memory card",
        "disk",
        "usb",
        "autoload",
    ],
    "sequencer_song": [
        "sequence",
        "song",
        "track",
        "bar",
        "tempo",
        "program change",
    ],
    "sampling_audio": [
        "sample",
        "sliced samples",
        "patched phrase",
        "record",
        "analog",
        "digital",
        "stereo",
        "mono",
    ],
    "midi_program": [
        "midi",
        "program",
        "receive channel",
        "note",
    ],
    "legacy_compatibility": [
        "mpc2000xl",
        "all(",
        "midi",
    ],
    "security_misc": [
        "password",
        "test",
        "version",
    ],
}

UPDATE_RANGES = {
    "boot_update_block": (0x7BE0, 0x8130),
    "progress_block": (0x94A0, 0x94D0),
    "late_ui_block": (0xC7D40, 0xC7EA0),
    "late_progress_block": (0xCB05C, 0xCB090),
    "late_error_block": (0xD30B0, 0xD3230),
}

EXACT_STRINGS = {
    "version_banner": 0x10000,
    "boot_update_title": 0x7C9C,
    "loading_os_file": 0x7CF8,
    "boot_flash_progress_erase": 0x94A0,
    "boot_flash_progress_write": 0x94B8,
    "late_not_os_file": 0xC7D58,
    "late_os_update": 0xC7D74,
    "late_osxl_update": 0xC7E74,
    "late_flash_progress_erase": 0xCB05C,
    "late_flash_progress_write": 0xCB074,
}

BASE_CANDIDATES = [0x09000000, 0x08000000, 0x0A000000, 0x01000000]


def entropy(data: bytes) -> float:
    counts = Counter(data)
    total = len(data)
    return -sum((count / total) * math.log2(count / total) for count in counts.values())


def extract_strings(data: bytes) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for match in PRINTABLE_RE.finditer(data):
        text = match.group().decode("latin1")
        rows.append(
            {
                "offset": match.start(),
                "length": len(text),
                "text": text,
            }
        )
    return rows


def classify_strings(strings: Iterable[dict[str, object]]) -> dict[str, list[dict[str, object]]]:
    out: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in strings:
        text = str(row["text"]).lower()
        for category, keywords in FEATURE_KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                out[category].append(row)
    return dict(out)


def base_mapping_counts(data: bytes) -> list[dict[str, object]]:
    size = len(data)
    rows: list[dict[str, object]] = []
    for base in BASE_CANDIDATES:
        count = 0
        samples = []
        for off in range(0, size - 4, 4):
            value = int.from_bytes(data[off : off + 4], "big")
            if base <= value < base + size:
                count += 1
                if len(samples) < 12:
                    samples.append(
                        {
                            "file_offset": off,
                            "value": value,
                            "mapped_file_offset": value - base,
                        }
                    )
        rows.append({"base": base, "mapped_word_count": count, "samples": samples})
    rows.sort(key=lambda row: int(row["mapped_word_count"]), reverse=True)
    return rows


def vector_words(data: bytes, count: int = 16) -> list[dict[str, object]]:
    rows = []
    for index in range(count):
        off = index * 4
        value = int.from_bytes(data[off : off + 4], "big")
        rows.append({"index": index, "offset": off, "value": value})
    return rows


def scan_standard_crc_tables(data: bytes) -> dict[str, int]:
    out: dict[str, int] = {}

    poly32 = 0xEDB88320
    table32 = []
    for i in range(256):
        crc = i
        for _ in range(8):
            crc = poly32 ^ (crc >> 1) if (crc & 1) else (crc >> 1)
        table32.append(crc)
    out["crc32_le"] = data.find(b"".join(struct.pack("<I", value) for value in table32))
    out["crc32_be"] = data.find(b"".join(struct.pack(">I", value) for value in table32))

    poly16 = 0x1021
    table16 = []
    for i in range(256):
        crc = i << 8
        for _ in range(8):
            crc = ((crc << 1) ^ poly16) & 0xFFFF if (crc & 0x8000) else (crc << 1) & 0xFFFF
        table16.append(crc)
    out["crc16_le"] = data.find(b"".join(struct.pack("<H", value) for value in table16))
    out["crc16_be"] = data.find(b"".join(struct.pack(">H", value) for value in table16))

    return out


def string_density_by_block(data: bytes, block_size: int = 0x10000) -> list[dict[str, object]]:
    rows = []
    for off in range(0, len(data), block_size):
        block = data[off : off + block_size]
        rows.append(
            {
                "offset": off,
                "string_count": sum(1 for _ in PRINTABLE_RE.finditer(block)),
            }
        )
    return rows


def find_direct_refs(data: bytes, base: int, target_offset: int) -> list[int]:
    needle = (base + target_offset).to_bytes(4, "big")
    hits = []
    start = 0
    while True:
        idx = data.find(needle, start)
        if idx < 0:
            break
        hits.append(idx)
        start = idx + 1
    return hits


def range_refs(data: bytes, base: int, start_off: int, end_off: int) -> list[dict[str, int]]:
    hits = []
    for file_off in range(0, len(data) - 4, 2):
        value = int.from_bytes(data[file_off : file_off + 4], "big")
        target = value - base
        if start_off <= target < end_off:
            hits.append(
                {
                    "file_offset": file_off,
                    "pointer_value": value,
                    "target_offset": target,
                }
            )
    return hits


def dense_region_prefixed_ptrs(data: bytes, start_off: int, end_off: int) -> list[dict[str, int]]:
    hits = []
    for file_off in range(0, len(data) - 4, 2):
        value = int.from_bytes(data[file_off : file_off + 4], "big")
        prefix = value >> 24
        low = value & 0x00FFFFFF
        if prefix in (0x08, 0x09, 0x0A) and start_off <= low < end_off:
            hits.append(
                {
                    "file_offset": file_off,
                    "pointer_value": value,
                    "prefix": prefix,
                    "low_24_target": low,
                }
            )
    return hits


def capstone_probe(data: bytes) -> dict[str, object] | None:
    try:
        from capstone import CS_ARCH_M68K, CS_MODE_BIG_ENDIAN, Cs
    except Exception:
        return None

    md = Cs(CS_ARCH_M68K, CS_MODE_BIG_ENDIAN)
    windows = [0x2A0, 0x4F61C, 0x89290]
    probes = []
    for off in windows:
        instructions = []
        for insn in md.disasm(data[off : off + 32], 0x09000000 + off):
            instructions.append(
                {
                    "address": insn.address,
                    "mnemonic": insn.mnemonic,
                    "op_str": insn.op_str,
                }
            )
            if len(instructions) >= 8:
                break
        probes.append({"file_offset": off, "instructions": instructions})
    return {"arch": "m68k/coldfire probe", "windows": probes}


def write_strings_tsv(path: Path, strings: Iterable[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        handle.write("offset_hex\tlength\ttext\n")
        for row in strings:
            text = str(row["text"]).replace("\t", " ").replace("\n", " ")
            handle.write(f"0x{int(row['offset']):x}\t{row['length']}\t{text}\n")


def write_interesting_strings_tsv(path: Path, categories: dict[str, list[dict[str, object]]]) -> None:
    seen: set[tuple[int, str]] = set()
    rows: list[tuple[str, int, int, str]] = []
    for category, items in categories.items():
        for row in items:
            key = (int(row["offset"]), str(row["text"]))
            if key in seen:
                continue
            seen.add(key)
            rows.append((category, int(row["offset"]), int(row["length"]), str(row["text"])))

    rows.sort(key=lambda row: row[1])
    with path.open("w", encoding="utf-8") as handle:
        handle.write("category\toffset_hex\tlength\ttext\n")
        for category, offset, length, text in rows:
            clean = text.replace("\t", " ").replace("\n", " ")
            handle.write(f"{category}\t0x{offset:x}\t{length}\t{clean}\n")


def write_report(path: Path, summary: dict[str, object]) -> None:
    best_base = summary["base_candidates"][0]
    lines = [
        "# JJOS Firmware Structural Report",
        "",
        f"- File: `{summary['file_name']}`",
        f"- Size: `{summary['size_bytes']}` bytes",
        f"- SHA-256: `{summary['sha256']}`",
        f"- Entropy: `{summary['entropy_bits_per_byte']}` bits/byte",
        "",
        "## Likely Architecture / Mapping",
        "",
        "- Authoritative working RE path is currently SuperH (`SuperH4:LE:32:default`, base `0x00000000`) from the Ghidra artifacts.",
        "- This script's pointer-density/base heuristics are coarse and should be treated as supporting context only, not architecture proof.",
        f"- Top legacy big-endian base candidate in this static scan: `{hex(best_base['base'])}` with `{best_base['mapped_word_count']}` mapped words.",
        "- Practical rule: rely on `analysis/output/ghidra_sh_findings.md` for architecture and control-flow claims.",
        "",
        "## Candidate Validation / Checksum Areas",
        "",
        "- Boot/update string block at `0x7BE0-0x8130`: dense cluster of status and error strings tied to loading and writing the OS image.",
        f"- Direct/immediate references into that boot/update block under base `0x09000000`: `{summary['update_range_refs']['boot_update_block_count']}` hits.",
        "- Flash progress strings at `0x94A0` and `0x94B8` are directly referenced from file offsets `0x4F61C` and `0x89290`.",
        "- Later JJOS/OS-XL UI blocks around `0xC7D40-0xD3230` do not expose clean `0x09000000 + offset` references, which suggests a different addressing scheme or table-driven lookup.",
        "- No standard table-driven `CRC32` or `CRC16-CCITT` lookup tables were found in the image.",
        "- Practical implication: update validation is likely custom, bitwise, additive, or embedded inside hand-written routines rather than a stock table-based CRC implementation.",
        "",
        "## String / Feature Map",
        "",
        "- The densest UI/resource area is `0xC0000-0xDFFFF`.",
        "- Feature families recovered from strings include storage/filesystem, USB transfer, sequencing, sampling, MIDI/program handling, MPC2000XL compatibility, password handling, and flash update flows.",
        "",
        "## First Safe POC Patch",
        "",
        "1. Duplicate the original image and never patch the only copy.",
        "2. Patch a fixed-length UI string in a late resource block, not boot-critical code and not the main version banner.",
        "3. Best initial target: the late update-label string at `0xC7D74` (`OS update`) or another same-length late UI string, because it is cosmetic and isolated.",
        "4. Keep the replacement exactly the same byte length. Do not insert or delete bytes.",
        "5. Before any hardware flash attempt, identify and bypass or reproduce the update integrity check so the device accepts the modified image.",
        "6. First hardware validation should stop before flash commit if possible: confirm the device loads the file and reaches the update screen with the modified label.",
        "",
        "## Regeneration",
        "",
        "- Run: `python3 analysis/scan_firmware.py mpc2500_jv313.bin`",
        "- Output directory: `analysis/output`",
    ]

    capstone_info = summary.get("capstone_probe")
    if capstone_info:
        lines.extend(
            [
                "",
                "## Optional Legacy Probe",
                "",
                "- Optional Capstone M68k probing is kept only as a legacy heuristic and is not architecture evidence.",
            ]
        )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract structure from a raw JJOS firmware image.")
    parser.add_argument("firmware", type=Path, help="Path to firmware binary")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("analysis/output"),
        help="Directory for generated artifacts",
    )
    args = parser.parse_args()

    data = args.firmware.read_bytes()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    strings = extract_strings(data)
    categories = classify_strings(strings)

    summary = {
        "file_name": args.firmware.name,
        "size_bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "entropy_bits_per_byte": round(entropy(data), 4),
        "vector_words": vector_words(data, count=16),
        "base_candidates": base_mapping_counts(data),
        "crc_tables": scan_standard_crc_tables(data),
        "string_density_by_64k": string_density_by_block(data),
        "exact_string_refs_base_0x09000000": {
            name: find_direct_refs(data, 0x09000000, target_off)
            for name, target_off in EXACT_STRINGS.items()
        },
        "update_range_refs": {
            f"{name}_count": len(range_refs(data, 0x09000000, start, end))
            for name, (start, end) in UPDATE_RANGES.items()
        },
        "late_region_prefixed_pointers": dense_region_prefixed_ptrs(data, 0x0C7000, 0x0D4000),
        "feature_categories": {
            name: rows[:80]
            for name, rows in sorted(categories.items(), key=lambda item: len(item[1]), reverse=True)
        },
        "capstone_probe": capstone_probe(data),
    }

    (args.output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )
    write_strings_tsv(args.output_dir / "strings.tsv", strings)
    write_interesting_strings_tsv(args.output_dir / "interesting_strings.tsv", categories)
    write_report(args.output_dir / "report.md", summary)


if __name__ == "__main__":
    main()
