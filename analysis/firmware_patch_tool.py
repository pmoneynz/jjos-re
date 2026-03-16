#!/usr/bin/env python3

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


KNOWN_PATCH_TARGETS = [
    ("boot_update_title", 0x7C9C, 32),
    ("boot_loading_os_file", 0x7CF8, 27),
    ("boot_os_file_not_found", 0x7D14, 25),
    ("late_not_mpc2500_os_file", 0xC7D58, 25),
    ("late_os_update", 0xC7D74, 9),
    ("late_osxl_update", 0xC7E74, 12),
]


@dataclass(frozen=True)
class Patch:
    name: str
    offset: int
    expected: bytes
    replacement: bytes


def parse_offset(value: Any) -> int:
    if isinstance(value, int):
        if value < 0:
            raise ValueError("offset must be >= 0")
        return value
    if isinstance(value, str):
        text = value.strip().lower()
        base = 16 if text.startswith("0x") else 10
        out = int(text, base)
        if out < 0:
            raise ValueError("offset must be >= 0")
        return out
    raise ValueError("offset must be int or string")


def parse_patch_bytes(row: dict[str, Any], expected_key: str, replacement_key: str) -> tuple[bytes, bytes]:
    expected_value = row.get(expected_key)
    replacement_value = row.get(replacement_key)
    if expected_value is None or replacement_value is None:
        raise ValueError(f"patch row must contain both '{expected_key}' and '{replacement_key}'")

    if expected_key.endswith("_ascii"):
        if not isinstance(expected_value, str) or not isinstance(replacement_value, str):
            raise ValueError(f"{expected_key} and {replacement_key} must be strings")
        expected = expected_value.encode("ascii")
        replacement = replacement_value.encode("ascii")
    else:
        if not isinstance(expected_value, str) or not isinstance(replacement_value, str):
            raise ValueError(f"{expected_key} and {replacement_key} must be hex strings")
        expected = bytes.fromhex(expected_value)
        replacement = bytes.fromhex(replacement_value)

    if len(expected) != len(replacement):
        raise ValueError(
            f"replacement length mismatch for {row.get('name', '<unnamed>')}: "
            f"expected {len(expected)} bytes, got {len(replacement)} bytes"
        )
    return expected, replacement


def load_spec(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("spec root must be a JSON object")
    patches = data.get("patches")
    if not isinstance(patches, list) or not patches:
        raise ValueError("spec must contain a non-empty 'patches' array")
    return data


def to_patch(row: dict[str, Any]) -> Patch:
    if not isinstance(row, dict):
        raise ValueError("each patch entry must be an object")
    name = row.get("name", f"patch_at_{row.get('offset')}")
    if not isinstance(name, str):
        raise ValueError("patch name must be a string")
    offset = parse_offset(row.get("offset"))

    has_ascii = "expected_ascii" in row or "replacement_ascii" in row
    has_hex = "expected_hex" in row or "replacement_hex" in row
    if has_ascii and has_hex:
        raise ValueError(f"{name}: choose either *_ascii or *_hex fields, not both")
    if not has_ascii and not has_hex:
        raise ValueError(f"{name}: missing expected/replacement fields")

    if has_ascii:
        expected, replacement = parse_patch_bytes(row, "expected_ascii", "replacement_ascii")
    else:
        expected, replacement = parse_patch_bytes(row, "expected_hex", "replacement_hex")

    return Patch(name=name, offset=offset, expected=expected, replacement=replacement)


def ensure_non_overlapping(patches: list[Patch]) -> None:
    spans = sorted([(p.offset, p.offset + len(p.expected), p.name) for p in patches], key=lambda x: x[0])
    for i in range(len(spans) - 1):
        a_start, a_end, a_name = spans[i]
        b_start, _, b_name = spans[i + 1]
        if b_start < a_end:
            raise ValueError(f"overlapping patches: {a_name} overlaps {b_name}")


def apply_spec(firmware: Path, spec_path: Path, output: Path, manifest: Path | None) -> None:
    source = firmware.read_bytes()
    spec = load_spec(spec_path)
    patches = [to_patch(row) for row in spec["patches"]]
    ensure_non_overlapping(patches)

    mutable = bytearray(source)
    applied_rows: list[dict[str, Any]] = []

    for patch in sorted(patches, key=lambda p: p.offset):
        end = patch.offset + len(patch.expected)
        if end > len(source):
            raise ValueError(f"{patch.name}: patch range 0x{patch.offset:x}-0x{end:x} exceeds file size")

        actual = bytes(source[patch.offset:end])
        if actual != patch.expected:
            raise ValueError(
                f"{patch.name}: expected bytes at 0x{patch.offset:x} do not match.\n"
                f" expected={patch.expected.hex()}\n"
                f" actual  ={actual.hex()}"
            )

        mutable[patch.offset:end] = patch.replacement
        applied_rows.append(
            {
                "name": patch.name,
                "offset_hex": f"0x{patch.offset:x}",
                "length": len(patch.expected),
                "before_hex": patch.expected.hex(),
                "after_hex": patch.replacement.hex(),
                "before_ascii": patch.expected.decode("ascii", errors="replace"),
                "after_ascii": patch.replacement.decode("ascii", errors="replace"),
            }
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(bytes(mutable))

    src_sha = hashlib.sha256(source).hexdigest()
    out_sha = hashlib.sha256(bytes(mutable)).hexdigest()
    print(f"input_sha256={src_sha}")
    print(f"output_sha256={out_sha}")
    print(f"applied_patches={len(applied_rows)}")

    if manifest:
        manifest.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "firmware": firmware.name,
            "spec": str(spec_path),
            "spec_name": spec.get("name"),
            "spec_notes": spec.get("notes"),
            "input_size": len(source),
            "output_size": len(mutable),
            "input_sha256": src_sha,
            "output_sha256": out_sha,
            "patches": applied_rows,
        }
        manifest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"manifest={manifest}")


def inspect_targets(firmware: Path) -> None:
    data = firmware.read_bytes()
    print(f"firmware={firmware}")
    print(f"size={len(data)}")
    print(f"sha256={hashlib.sha256(data).hexdigest()}")
    print("")
    print("name\toffset_hex\tlength\tascii\tbytes_hex")
    for name, offset, length in KNOWN_PATCH_TARGETS:
        end = offset + length
        if end > len(data):
            print(f"{name}\t0x{offset:x}\t{length}\t<out_of_range>\t-")
            continue
        raw = data[offset:end]
        ascii_text = raw.decode("ascii", errors="replace")
        print(f"{name}\t0x{offset:x}\t{length}\t{ascii_text}\t{raw.hex()}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Deterministic patch helper for MPC2500 firmware experiments")
    subparsers = parser.add_subparsers(dest="command", required=True)

    inspect_parser = subparsers.add_parser("inspect", help="show bytes at known patch-safe string targets")
    inspect_parser.add_argument("--firmware", type=Path, required=True, help="input firmware binary")

    apply_parser = subparsers.add_parser("apply", help="apply same-length patches from a JSON spec")
    apply_parser.add_argument("--firmware", type=Path, required=True, help="input firmware binary")
    apply_parser.add_argument("--spec", type=Path, required=True, help="JSON patch spec")
    apply_parser.add_argument("--output", type=Path, required=True, help="output patched firmware path")
    apply_parser.add_argument("--manifest", type=Path, help="optional JSON manifest path")

    args = parser.parse_args()
    if args.command == "inspect":
        inspect_targets(args.firmware)
    elif args.command == "apply":
        apply_spec(args.firmware, args.spec, args.output, args.manifest)


if __name__ == "__main__":
    main()
