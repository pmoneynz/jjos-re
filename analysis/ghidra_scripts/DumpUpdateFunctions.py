## ###
#  IP: GHIDRA
##
# Dump the first instructions of key update-path seed functions.
# @category: Analysis
# @runtime Jython

TARGETS = [
    0x09047c9a,
    0x0904f61c,
    0x0908925e,
    0x09000482,
    0x090004ea,
    0x09010412,
    0x09010432,
    0x0904644e,
]


def main():
    out_path = None
    args = getScriptArgs()
    if len(args) > 0:
        out_path = args[0]

    lines = []
    lines.append("# Update Function Instruction Dumps")
    lines.append("")

    for entry in TARGETS:
        addr = toAddr(entry)
        func = getFunctionAt(addr)
        lines.append("## `{}`".format(addr))
        lines.append("")
        if func is None:
            lines.append("- No function at this address.")
            lines.append("")
            continue

        lines.append("- Name: `{}`".format(func.getName()))
        lines.append("- Entry: `{}`".format(func.getEntryPoint()))
        lines.append("")
        lines.append("```text")
        inst = getInstructionAt(func.getEntryPoint())
        count = 0
        while inst is not None and func.getBody().contains(inst.getAddress()) and count < 16:
            lines.append("{}: {}".format(inst.getAddress(), str(inst)))
            inst = inst.getNext()
            count += 1
        lines.append("```")
        lines.append("")

    if out_path is not None:
        out_file = open(out_path, "w")
        for line in lines:
            out_file.write(line + "\n")
        out_file.close()


main()
