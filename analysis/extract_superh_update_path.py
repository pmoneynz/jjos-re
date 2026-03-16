#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
import string
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass
class DecodedInstruction:
    address: int
    word: int
    kind: str
    mnemonic: str
    register: int | None = None
    target: int | None = None
    literal_address: int | None = None
    literal_value: int | None = None
    immediate_value: int | None = None


SEED_WINDOWS: dict[str, dict[str, int]] = {
    "ENTRY_INIT": {"entry": 0x00000626, "start": 0x00000626, "end": 0x00001060},
    "FUN_00008a10": {"entry": 0x00008A10, "start": 0x00008A10, "end": 0x00008B4C},
    "FUN_00008b8c": {"entry": 0x00008B8C, "start": 0x00008B8C, "end": 0x00008C42},
    "FUN_00008c44": {"entry": 0x00008C44, "start": 0x00008C44, "end": 0x00008CA4},
    "FUN_00008db4": {"entry": 0x00008DB4, "start": 0x00008DB4, "end": 0x00008ED4},
    "FUN_00008ed6": {"entry": 0x00008ED6, "start": 0x00008ED6, "end": 0x00008F00},
    "FUN_0000844a": {"entry": 0x0000844A, "start": 0x0000844A, "end": 0x000084E0},
    "FUN_000084e2": {"entry": 0x000084E2, "start": 0x000084E2, "end": 0x000084F4},
    "FUN_000084f8": {"entry": 0x000084F8, "start": 0x000084F8, "end": 0x0000853C},
    "FUN_0000914c": {"entry": 0x0000914C, "start": 0x0000914C, "end": 0x000091A6},
}

TARGET_STRINGS = {
    "File data error": 0x00007C50,
    "OS data error": 0x00007C80,
    "Loading OS file": 0x00007CF8,
    "OS file not found": 0x00007D14,
    "Flash ROM erasing %": 0x000094A0,
}

ENTRY_REQUIRED_CALLS = [0x00008C44, 0x00008ED6, 0x00008DB4, 0x00008B8C]
ALT_FILENAME_EXPECTED = {"M25V", "BIN", "MPC25T", "MPC2500", "SOS"}


def read_u16_le(data: bytes, address: int) -> int:
    return int.from_bytes(data[address : address + 2], "little")


def read_u32_le(data: bytes, address: int) -> int:
    return int.from_bytes(data[address : address + 4], "little")


def sign_extend_8(value: int) -> int:
    return value - 0x100 if (value & 0x80) else value


def sign_extend_12(value: int) -> int:
    return value - 0x1000 if (value & 0x800) else value


def decode_instruction(data: bytes, address: int) -> DecodedInstruction:
    word = read_u16_le(data, address)
    op_hi = (word >> 12) & 0xF

    if op_hi == 0xA:
        disp = sign_extend_12(word & 0x0FFF)
        target = address + 4 + (disp * 2)
        return DecodedInstruction(address=address, word=word, kind="branch_uncond", mnemonic="bra", target=target)

    if op_hi == 0xB:
        disp = sign_extend_12(word & 0x0FFF)
        target = address + 4 + (disp * 2)
        return DecodedInstruction(address=address, word=word, kind="call_rel", mnemonic="bsr", target=target)

    upper = word & 0xFF00
    if upper == 0x8900:
        disp = sign_extend_8(word & 0x00FF)
        target = address + 4 + (disp * 2)
        return DecodedInstruction(address=address, word=word, kind="branch_cond", mnemonic="bt", target=target)
    if upper == 0x8B00:
        disp = sign_extend_8(word & 0x00FF)
        target = address + 4 + (disp * 2)
        return DecodedInstruction(address=address, word=word, kind="branch_cond", mnemonic="bf", target=target)
    if upper == 0x8D00:
        disp = sign_extend_8(word & 0x00FF)
        target = address + 4 + (disp * 2)
        return DecodedInstruction(address=address, word=word, kind="branch_cond", mnemonic="bt/s", target=target)
    if upper == 0x8F00:
        disp = sign_extend_8(word & 0x00FF)
        target = address + 4 + (disp * 2)
        return DecodedInstruction(address=address, word=word, kind="branch_cond", mnemonic="bf/s", target=target)

    if (word & 0xF0FF) == 0x400B:
        register = (word >> 8) & 0xF
        return DecodedInstruction(address=address, word=word, kind="call_reg", mnemonic="jsr", register=register)

    if word == 0x000B:
        return DecodedInstruction(address=address, word=word, kind="return", mnemonic="rts")

    if op_hi == 0xD:
        register = (word >> 8) & 0xF
        disp = word & 0xFF
        literal_address = ((address + 4) & ~0x3) + (disp * 4)
        literal_value = read_u32_le(data, literal_address) if literal_address + 4 <= len(data) else None
        return DecodedInstruction(
            address=address,
            word=word,
            kind="load_literal_long",
            mnemonic="mov.l",
            register=register,
            literal_address=literal_address,
            literal_value=literal_value,
        )

    if op_hi == 0x9:
        register = (word >> 8) & 0xF
        disp = word & 0xFF
        literal_address = address + 4 + (disp * 2)
        literal_value = None
        if literal_address + 2 <= len(data):
            literal_value = int.from_bytes(data[literal_address : literal_address + 2], "little", signed=True)
        return DecodedInstruction(
            address=address,
            word=word,
            kind="load_literal_word",
            mnemonic="mov.w",
            register=register,
            literal_address=literal_address,
            literal_value=literal_value,
        )

    if op_hi == 0xE:
        register = (word >> 8) & 0xF
        imm = sign_extend_8(word & 0xFF)
        return DecodedInstruction(
            address=address,
            word=word,
            kind="mov_imm",
            mnemonic="mov",
            register=register,
            immediate_value=imm,
        )

    return DecodedInstruction(address=address, word=word, kind="other", mnemonic="other")


def successors(ins: DecodedInstruction) -> list[int]:
    next_addr = ins.address + 2
    if ins.kind == "return":
        return []
    if ins.kind == "branch_uncond":
        return [ins.target] if ins.target is not None else []
    if ins.kind == "branch_cond":
        out: list[int] = [next_addr]
        if ins.target is not None:
            out.append(ins.target)
        return out
    return [next_addr]


def explore_window(data: bytes, entry: int, start: int, end: int) -> list[DecodedInstruction]:
    visited: set[int] = set()
    decoded: dict[int, DecodedInstruction] = {}
    queue: list[int] = [entry]

    while queue:
        pc = queue.pop()
        while start <= pc < end and pc + 2 <= len(data):
            if pc in visited:
                break
            visited.add(pc)
            ins = decode_instruction(data, pc)
            decoded[pc] = ins

            next_nodes = successors(ins)
            if ins.kind == "branch_uncond":
                if next_nodes:
                    target = next_nodes[0]
                    if start <= target < end and target not in visited:
                        queue.append(target)
                break
            if ins.kind == "branch_cond":
                linear = next_nodes[0]
                if len(next_nodes) > 1:
                    target = next_nodes[1]
                    if start <= target < end and target not in visited:
                        queue.append(target)
                pc = linear
                continue
            if ins.kind == "return":
                break
            if next_nodes:
                pc = next_nodes[0]
                continue
            break

    return [decoded[address] for address in sorted(decoded)]


def read_ascii_at(data: bytes, address: int, max_len: int = 64) -> str | None:
    if not (0 <= address < len(data)):
        return None
    out: list[str] = []
    for idx in range(address, min(address + max_len, len(data))):
        value = data[idx]
        if value == 0:
            break
        ch = chr(value)
        if ch not in string.printable or ch in "\r\n\t\x0b\x0c":
            break
        out.append(ch)
    if len(out) < 3:
        return None
    return "".join(out).strip()


def resolve_register_call_target(
    instructions: list[DecodedInstruction], call_index: int, register: int, lookback: int = 16
) -> tuple[int | None, int | None]:
    lower = max(0, call_index - lookback)
    for idx in range(call_index - 1, lower - 1, -1):
        ins = instructions[idx]
        if ins.register != register:
            continue
        if ins.kind == "load_literal_long" and ins.literal_value is not None:
            return ins.literal_value, ins.address
        if ins.kind == "mov_imm" and ins.immediate_value is not None:
            return ins.immediate_value, ins.address
    return None, None


def extract_calls(instructions: list[DecodedInstruction]) -> list[dict[str, Any]]:
    calls: list[dict[str, Any]] = []
    for idx, ins in enumerate(instructions):
        if ins.kind == "call_rel":
            calls.append(
                {
                    "call_site": ins.address,
                    "mnemonic": ins.mnemonic,
                    "resolved_target": ins.target,
                    "resolution_source": "relative",
                    "status": "proven",
                }
            )
        elif ins.kind == "call_reg" and ins.register is not None:
            target, source = resolve_register_call_target(instructions, idx, ins.register)
            calls.append(
                {
                    "call_site": ins.address,
                    "mnemonic": ins.mnemonic,
                    "register": ins.register,
                    "resolved_target": target,
                    "resolution_source": source,
                    "status": "proven" if target is not None else "hypothesis",
                }
            )
    return calls


def extract_literal_strings(instructions: list[DecodedInstruction], data: bytes) -> list[dict[str, Any]]:
    rows: dict[int, dict[str, Any]] = {}
    for ins in instructions:
        if ins.kind != "load_literal_long" or ins.literal_value is None:
            continue
        text = read_ascii_at(data, ins.literal_value)
        if not text:
            continue
        rows[ins.literal_value] = {"address": ins.literal_value, "text": text, "loaded_at": ins.address}
    return [rows[address] for address in sorted(rows)]


def extract_literal_refs(instructions: list[DecodedInstruction], target_value: int) -> list[int]:
    refs: list[int] = []
    for ins in instructions:
        if ins.kind == "load_literal_long" and ins.literal_value == target_value:
            refs.append(ins.address)
    return refs


def extract_mmio_literals(instructions: list[DecodedInstruction]) -> list[int]:
    values: set[int] = set()
    for ins in instructions:
        if ins.kind != "load_literal_long" or ins.literal_value is None:
            continue
        if 0xA5007200 <= ins.literal_value <= 0xA50072FF:
            values.add(ins.literal_value)
    return sorted(values)


def to_hex(value: int | None) -> str | None:
    if value is None:
        return None
    return f"0x{value:08x}"


def build_markdown(summary: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# SuperH Update Evidence (Raw-Binary Extractor)")
    lines.append("")
    lines.append("## Method")
    lines.append("")
    lines.append("- Source: `mpc2500_jv313.bin`")
    lines.append("- Technique: focused SuperH pattern extraction from known seed windows")
    lines.append("- Classification policy:")
    lines.append("  - **proven**: directly observed by decoded control-flow/literal evidence")
    lines.append("  - **hypothesis**: plausible but not directly proven by current extraction")
    lines.append("")
    lines.append("## Proven Calls from ENTRY_INIT")
    lines.append("")
    for row in summary["entry_init"]["calls"]:
        target = to_hex(row.get("resolved_target"))
        source = to_hex(row.get("resolution_source")) if isinstance(row.get("resolution_source"), int) else row.get("resolution_source")
        lines.append(
            f"- `{to_hex(row['call_site'])}` `{row['mnemonic']}` -> `{target}` "
            f"(resolution source: `{source}`, status: `{row['status']}`)"
        )
    lines.append("")
    lines.append("### Required-call checks")
    lines.append("")
    for row in summary["entry_init"]["required_call_checks"]:
        lines.append(
            f"- target `{to_hex(row['target'])}`: "
            f"{'FOUND' if row['found'] else 'MISSING'} (**{row['status']}**)"
        )
    lines.append("")
    lines.append("## Proven Alternate Filename Literal Set (FUN_00008b8c)")
    lines.append("")
    for row in summary["fun_8b8c"]["literal_strings"]:
        lines.append(f"- `{to_hex(row['address'])}` -> `{row['text']}` (loaded at `{to_hex(row['loaded_at'])}`)")
    lines.append("")
    lines.append("### Expected-set checks")
    lines.append("")
    for name in sorted(ALT_FILENAME_EXPECTED):
        found = name in summary["fun_8b8c"]["literal_texts"]
        lines.append(f"- `{name}`: {'FOUND' if found else 'MISSING'} (**{'proven' if found else 'hypothesis'}**)")
    lines.append("")
    lines.append("## Proven Direct Error-String Literal References (ENTRY_INIT window)")
    lines.append("")
    for label, row in summary["entry_init"]["string_literal_refs"].items():
        refs = ", ".join(to_hex(addr) for addr in row["refs"]) if row["refs"] else "-"
        lines.append(f"- `{label}` at `{to_hex(row['target'])}` refs: `{refs}` (**{row['status']}**)")
    lines.append("")
    lines.append("## Proven MMIO/Controller Literal Touchpoints (`0xa50072xx`)")
    lines.append("")
    for function_name, values in summary["mmio_touchpoints"].items():
        rendered = ", ".join(to_hex(value) for value in values) if values else "-"
        lines.append(f"- `{function_name}`: {rendered}")
    lines.append("")
    lines.append("## Current Hypotheses / Unresolved")
    lines.append("")
    for row in summary["hypotheses"]:
        lines.append(f"- {row}")
    lines.append("")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract SuperH update-path evidence from raw JJOS binary.")
    parser.add_argument("firmware", type=Path, help="Path to firmware binary")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("analysis/output"),
        help="Directory for generated evidence outputs",
    )
    args = parser.parse_args()

    data = args.firmware.read_bytes()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    decoded_by_name: dict[str, list[DecodedInstruction]] = {}
    for name, window in SEED_WINDOWS.items():
        decoded_by_name[name] = explore_window(
            data=data,
            entry=window["entry"],
            start=window["start"],
            end=window["end"],
        )

    entry_calls = extract_calls(decoded_by_name["ENTRY_INIT"])
    required_checks = []
    resolved_targets = {row["resolved_target"] for row in entry_calls if row.get("resolved_target") is not None}
    for target in ENTRY_REQUIRED_CALLS:
        found = target in resolved_targets
        required_checks.append({"target": target, "found": found, "status": "proven" if found else "hypothesis"})

    literal_strings_8b8c = extract_literal_strings(decoded_by_name["FUN_00008b8c"], data)
    literal_texts_8b8c = {row["text"] for row in literal_strings_8b8c}

    string_literal_refs: dict[str, Any] = {}
    for label, target in TARGET_STRINGS.items():
        refs = extract_literal_refs(decoded_by_name["ENTRY_INIT"], target)
        string_literal_refs[label] = {
            "target": target,
            "refs": refs,
            "status": "proven" if refs else "hypothesis",
        }

    mmio_touchpoints = {
        "FUN_00008db4": extract_mmio_literals(decoded_by_name["FUN_00008db4"]),
        "FUN_00008ed6": extract_mmio_literals(decoded_by_name["FUN_00008ed6"]),
        "FUN_0000844a": extract_mmio_literals(decoded_by_name["FUN_0000844a"]),
        "FUN_000084e2": extract_mmio_literals(decoded_by_name["FUN_000084e2"]),
        "FUN_000084f8": extract_mmio_literals(decoded_by_name["FUN_000084f8"]),
    }

    hypotheses = [
        "No direct long-literal references were extracted for `Wrong file` / flash erase-write-read error strings in the boot block; these are likely reached indirectly through table/index flow.",
        "The `0xa50072xx` touchpoints in `FUN_00008db4`/`FUN_00008ed6`/`FUN_000084x` strongly indicate low-level transaction control, but this extractor does not yet prove exact AM29LV641 erase/program command semantics.",
    ]

    summary: dict[str, Any] = {
        "file_name": args.firmware.name,
        "sha256": hashlib.sha256(data).hexdigest(),
        "seed_windows": SEED_WINDOWS,
        "decoded_instruction_counts": {name: len(rows) for name, rows in decoded_by_name.items()},
        "entry_init": {
            "calls": entry_calls,
            "required_call_checks": required_checks,
            "string_literal_refs": string_literal_refs,
        },
        "fun_8b8c": {
            "literal_strings": literal_strings_8b8c,
            "literal_texts": sorted(literal_texts_8b8c),
            "expected_set_all_found": ALT_FILENAME_EXPECTED.issubset(literal_texts_8b8c),
        },
        "mmio_touchpoints": mmio_touchpoints,
        "hypotheses": hypotheses,
    }

    # Convert dataclass rows in call list if any nested dataclasses are added later.
    summary_json = json.loads(json.dumps(summary, default=lambda obj: asdict(obj) if hasattr(obj, "__dataclass_fields__") else str(obj)))

    json_path = args.output_dir / "superh_update_evidence.json"
    md_path = args.output_dir / "superh_update_evidence.md"
    json_path.write_text(json.dumps(summary_json, indent=2), encoding="utf-8")
    md_path.write_text(build_markdown(summary_json), encoding="utf-8")


if __name__ == "__main__":
    main()
