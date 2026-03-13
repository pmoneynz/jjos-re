## ###
#  IP: GHIDRA
##
# Report update-path functions and references for a raw JJOS firmware image.
# @category: Analysis
# @runtime Jython

BASE = 0x09000000
from jarray import zeros

RANGES = [
    ("boot_update_block", BASE + 0x7be0, BASE + 0x8130, False),
    ("progress_block", BASE + 0x94a0, BASE + 0x94d0, False),
    ("progress_erase_exact", BASE + 0x94a0, BASE + 0x94a1, True),
    ("progress_write_exact", BASE + 0x94b8, BASE + 0x94b9, True),
]


def read_u32(memory, addr):
    data = zeros(4, 'b')
    read = memory.getBytes(addr, data)
    if read != 4:
        return -1
    return ((data[0] & 0xff) << 24) | ((data[1] & 0xff) << 16) | ((data[2] & 0xff) << 8) | (data[3] & 0xff)


def scan_for_refs(memory, start_value, end_value, exact_only):
    hits = []
    for block in memory.getBlocks():
        if not block.isInitialized():
            continue
        cur = block.getStart()
        end = block.getEnd().subtract(3)
        while cur.compareTo(end) <= 0 and not monitor.isCancelled():
            value = read_u32(memory, cur)
            if exact_only:
                match = value == start_value
            else:
                match = value >= start_value and value < end_value
            if match:
                hits.append(cur)
            cur = cur.add(2)
    return hits


def get_callers(func):
    out = []
    refs = currentProgram.getReferenceManager().getReferencesTo(func.getEntryPoint())
    while refs.hasNext():
        ref = refs.next()
        if ref.getReferenceType().isCall():
            out.append(ref.getFromAddress())
    out.sort(key=lambda x: x.getOffset())
    return out


def find_nearby_seed_function(ref_site):
    func = getFunctionContaining(ref_site)
    if func is not None:
        return func

    best = None
    best_delta = None
    funcs = currentProgram.getFunctionManager().getFunctions(True)
    while funcs.hasNext():
        candidate = funcs.next()
        if not candidate.getName().startswith("UPD_"):
            continue
        delta = ref_site.getOffset() - candidate.getEntryPoint().getOffset()
        if delta < 0 or delta > 0x40:
            continue
        if best is None or delta < best_delta:
            best = candidate
            best_delta = delta
    return best


def get_callees(func):
    out = []
    seen = set()
    inst = getInstructionAt(func.getEntryPoint())
    while inst is not None and func.getBody().contains(inst.getAddress()):
        if inst.getFlowType().isCall():
            for flow in inst.getFlows():
                callee = getFunctionAt(flow)
                if callee is not None:
                    item = "{}@{}".format(callee.getName(), callee.getEntryPoint())
                else:
                    item = "SUB@{}".format(flow)
                if item not in seen:
                    seen.add(item)
                    out.append(item)
        inst = inst.getNext()
    return out


def join_addresses(addrs):
    if addrs is None or len(addrs) == 0:
        return "-"
    return ", ".join([str(x) for x in addrs])


def main():
    out_path = None
    args = getScriptArgs()
    if len(args) > 0:
        out_path = args[0]

    memory = currentProgram.getMemory()
    listing = currentProgram.getListing()

    hits = {}
    for name, start_value, end_value, exact_only in RANGES:
        hits[name] = scan_for_refs(memory, start_value, end_value, exact_only)

    function_tags = {}
    function_sites = {}
    for tag in hits:
        for ref_site in hits[tag]:
            func = find_nearby_seed_function(ref_site)
            if func is None:
                continue
            function_tags.setdefault(func, set()).add(tag)
            function_sites.setdefault(func, []).append(ref_site)

    funcs = currentProgram.getFunctionManager().getFunctions(True)
    while funcs.hasNext():
        func = funcs.next()
        if func.getName().startswith("UPD_"):
            function_tags.setdefault(func, set())
            function_sites.setdefault(func, [])

    functions = sorted(function_tags.keys(), key=lambda f: f.getEntryPoint().getOffset())

    lines = []
    lines.append("# Ghidra Update Path Map")
    lines.append("")
    lines.append("- Program: `{}`".format(currentProgram.getName()))
    lines.append("- Processor: `68000:BE:32:Coldfire`")
    lines.append("- Image base: `0x09000000`")
    lines.append("")
    lines.append("## Reference Summary")
    lines.append("")
    for tag in hits:
        lines.append("- `{}` refs: `{}`".format(tag, len(hits[tag])))
    lines.append("")
    lines.append("## Seeded Function Map")
    lines.append("")

    for func in functions:
        sites = sorted(function_sites.get(func, []), key=lambda x: x.getOffset())
        callers = get_callers(func)
        callees = get_callees(func)
        lines.append("### `{}`".format(func.getName()))
        lines.append("")
        lines.append("- Entry: `{}`".format(func.getEntryPoint()))
        lines.append("- Tags: `{}`".format(", ".join(sorted(function_tags.get(func, [])))))
        lines.append("- Ref sites: `{}`".format(join_addresses(sites)))
        lines.append("- Callers: `{}`".format(join_addresses(callers)))
        lines.append("- Callees: `{}`".format(", ".join(callees) if len(callees) else "-"))
        lines.append("")

    lines.append("## Observations")
    lines.append("")
    lines.append("- Functions tagged with `progress_block` are the strongest current flash/write routine candidates.")
    lines.append("- Functions tagged only with `boot_update_block` are more likely verification, load/update UI, or error handling paths.")
    lines.append("- Zero exact refs to `progress_write_exact` means the write-progress string is probably reached indirectly or via a nearby literal pool entry.")
    lines.append("")

    if out_path is not None:
        out_file = open(out_path, "w")
        for line in lines:
            out_file.write(line + "\n")
        out_file.close()


main()
