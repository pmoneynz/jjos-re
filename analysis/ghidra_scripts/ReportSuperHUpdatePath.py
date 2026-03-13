## ###
#  IP: GHIDRA
##
# Report update-path string references and containing functions for JJOS under SuperH analysis.
# @category: Analysis
# @runtime Jython


TARGETS = [
    ("update_filename_mpc2500_sos", 0x7c20),
    ("file_data_error", 0x7c50),
    ("os_data_error", 0x7c80),
    ("boot_update_title", 0x7c9c),
    ("boot_loading_os_file", 0x7cf8),
    ("boot_os_file_not_found", 0x7d14),
    ("wrong_file", 0x7df5),
    ("boot_file_write_error", 0x7fa8),
    ("boot_flash_erase_error", 0x80ca),
    ("boot_flash_write_error", 0x80e7),
    ("boot_flash_read_error", 0x8104),
    ("progress_erase", 0x94a0),
    ("progress_write", 0x94b8),
    ("late_not_os_file", 0xc7d58),
    ("late_os_update", 0xc7d74),
    ("late_osxl_update", 0xc7e74),
]


def join_addrs(addrs):
    if not addrs:
        return "-"
    return ", ".join([str(a) for a in addrs])


def get_function_calls(func):
    out = []
    seen = set()
    inst = getInstructionAt(func.getEntryPoint())
    while inst is not None and func.getBody().contains(inst.getAddress()):
        if inst.getFlowType().isCall():
            flows = inst.getFlows()
            if flows:
                for flow in flows:
                    callee = getFunctionAt(flow)
                    item = "{}@{}".format(callee.getName(), callee.getEntryPoint()) if callee else "SUB@{}".format(flow)
                    if item not in seen:
                        seen.add(item)
                        out.append(item)
        inst = inst.getNext()
    return out


def get_callers(func):
    out = []
    refs = currentProgram.getReferenceManager().getReferencesTo(func.getEntryPoint())
    while refs.hasNext():
        ref = refs.next()
        if ref.getReferenceType().isCall():
            out.append(ref.getFromAddress())
    out.sort(key=lambda x: x.getOffset())
    return out


def get_focus_function(addr_value):
    addr = toAddr(addr_value)
    func = getFunctionAt(addr)
    if func is None:
        func = currentProgram.getListing().getFunctionContaining(addr)
    return func


def main():
    args = getScriptArgs()
    out_path = args[0] if len(args) else None
    listing = currentProgram.getListing()

    target_refs = {}
    function_tags = {}
    function_sites = {}

    for name, off in TARGETS:
        addr = toAddr(off)
        refs = []
        it = currentProgram.getReferenceManager().getReferencesTo(addr)
        while it.hasNext():
            ref = it.next()
            refs.append(ref.getFromAddress())
        refs.sort(key=lambda x: x.getOffset())
        target_refs[name] = refs
        for ref_addr in refs:
            func = listing.getFunctionContaining(ref_addr)
            if func is None:
                continue
            function_tags.setdefault(func, set()).add(name)
            function_sites.setdefault(func, []).append(ref_addr)

    funcs = currentProgram.getFunctionManager().getFunctions(True)
    all_seeded = []
    while funcs.hasNext():
        func = funcs.next()
        if func.getName().startswith("ENTRY_") or func.getName().startswith("RESET_"):
            all_seeded.append(func)
    for func in all_seeded:
        function_tags.setdefault(func, set())
        function_sites.setdefault(func, [])

    functions = sorted(function_tags.keys(), key=lambda f: f.getEntryPoint().getOffset())

    lines = []
    lines.append("# SuperH Update Path Map")
    lines.append("")
    lines.append("- Program: `{}`".format(currentProgram.getName()))
    lines.append("- Language: `{}`".format(currentProgram.getLanguageID()))
    lines.append("- Image base: `0x00000000`")
    lines.append("")
    lines.append("## String Reference Summary")
    lines.append("")
    for name, off in TARGETS:
        lines.append("- `{}` at `{}` refs: `{}`".format(name, hex(off), len(target_refs[name])))
    lines.append("")
    lines.append("## Functions Touching Update Strings")
    lines.append("")

    for func in functions:
        refs = sorted(function_sites.get(func, []), key=lambda x: x.getOffset())
        tags = sorted(function_tags.get(func, set()))
        callers = get_callers(func)
        callees = get_function_calls(func)
        lines.append("### `{}`".format(func.getName()))
        lines.append("")
        lines.append("- Entry: `{}`".format(func.getEntryPoint()))
        lines.append("- Tags: `{}`".format(", ".join(tags) if tags else "-"))
        lines.append("- Ref sites: `{}`".format(join_addrs(refs)))
        lines.append("- Callers: `{}`".format(join_addrs(callers)))
        lines.append("- Callees: `{}`".format(", ".join(callees) if callees else "-"))
        lines.append("")

    lines.append("## Focus Helpers")
    lines.append("")
    for name, addr_value in [
        ("ENTRY_INIT", 0x626),
        ("scan_candidate_entries", 0x8a10),
        ("open_or_validate_stage_a", 0x8b8c),
        ("open_or_validate_stage_b", 0x8c44),
        ("commit_or_range_check", 0x8db4),
        ("device_write_stage", 0x8ed6),
    ]:
        func = get_focus_function(addr_value)
        lines.append("### `{}`".format(name))
        lines.append("")
        if func is None:
            lines.append("- Address: `{}`".format(hex(addr_value)))
            lines.append("- Function: `not recovered`")
            lines.append("")
            continue
        refs = sorted(function_sites.get(func, []), key=lambda x: x.getOffset())
        tags = sorted(function_tags.get(func, set()))
        lines.append("- Address: `{}`".format(hex(addr_value)))
        lines.append("- Function: `{}`".format(func.getName()))
        lines.append("- Entry: `{}`".format(func.getEntryPoint()))
        lines.append("- Tags: `{}`".format(", ".join(tags) if tags else "-"))
        lines.append("- Ref sites: `{}`".format(join_addrs(refs)))
        lines.append("- Callers: `{}`".format(join_addrs(get_callers(func))))
        lines.append("- Callees: `{}`".format(", ".join(get_function_calls(func)) if get_function_calls(func) else "-"))
        lines.append("")

    lines.append("## Raw Reference Lists")
    lines.append("")
    for name, off in TARGETS:
        lines.append("### `{}`".format(name))
        lines.append("")
        lines.append("- Address: `{}`".format(hex(off)))
        lines.append("- Refs: `{}`".format(join_addrs(target_refs[name])))
        lines.append("")

    if out_path:
        out_file = open(out_path, "w")
        for line in lines:
            out_file.write(line + "\n")
        out_file.close()


main()
