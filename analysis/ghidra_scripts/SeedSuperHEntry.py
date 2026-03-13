## ###
#  IP: GHIDRA
##
# Seed entry points for JJOS under SuperH little-endian analysis.
# @category: Analysis
# @runtime Jython

from ghidra.app.cmd.disassemble import DisassembleCommand


ENTRY_POINTS = [
    (0x0, "RESET_STUB"),
    (0x626, "ENTRY_INIT"),
]

ANCHOR_STRINGS = [
    (0x7c9c, "STR_BOOT_OS_UPDATE_TITLE"),
    (0x7cf8, "STR_BOOT_LOADING_OS_FILE"),
    (0x7d14, "STR_BOOT_OS_FILE_NOT_FOUND"),
    (0x7fa8, "STR_BOOT_FILE_WRITE_ERROR"),
    (0x80ca, "STR_BOOT_FLASH_ERASE_ERROR"),
    (0x80e7, "STR_BOOT_FLASH_WRITE_ERROR"),
    (0x8104, "STR_BOOT_FLASH_READ_ERROR"),
    (0x94a0, "STR_FLASH_PROGRESS_ERASE"),
    (0x94b8, "STR_FLASH_PROGRESS_WRITE"),
    (0xc7d58, "STR_LATE_NOT_MPC2500_OS_FILE"),
    (0xc7d74, "STR_LATE_OS_UPDATE"),
    (0xc7e74, "STR_LATE_OSXL_UPDATE"),
]


def safe_label(addr, name):
    try:
        if getSymbolAt(addr) is None:
            createLabel(addr, name, True)
    except:
        pass


def safe_ascii(addr):
    try:
        createAsciiString(addr)
    except:
        pass


def disassemble_from(addr):
    cmd = DisassembleCommand(addr, None, True)
    cmd.applyTo(currentProgram, monitor)


def seed_function(addr, name):
    disassemble_from(addr)
    func = getFunctionAt(addr)
    if func is None:
        try:
            func = createFunction(addr, name)
        except:
            func = getFunctionAt(addr)
    return func


def main():
    args = getScriptArgs()
    out_path = args[0] if len(args) else None

    report = []
    report.append("program\t{}".format(currentProgram.getName()))
    report.append("language\t{}".format(currentProgram.getLanguageID()))

    for off, label in ANCHOR_STRINGS:
        addr = toAddr(off)
        safe_ascii(addr)
        safe_label(addr, label)

    for off, name in ENTRY_POINTS:
        addr = toAddr(off)
        safe_label(addr, name)
        func = seed_function(addr, name)
        report.append("entry\t{}\t{}\t{}".format(name, hex(off), func is not None))

    if out_path:
        out_file = open(out_path, "w")
        for line in report:
            out_file.write(line + "\n")
        out_file.close()


main()
