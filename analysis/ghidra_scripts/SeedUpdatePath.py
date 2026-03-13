## ###
#  IP: GHIDRA
##
# Seed likely update-path routines in a raw JJOS firmware image.
# @category: Analysis
# @runtime Jython

from ghidra.app.cmd.disassemble import DisassembleCommand
from ghidra.app.util import PseudoDisassembler
from jarray import zeros

BASE = 0x09000000

RANGES = [
    ("boot_update_block", BASE + 0x7be0, BASE + 0x8130, False),
    ("progress_block", BASE + 0x94a0, BASE + 0x94d0, False),
    ("progress_erase_exact", BASE + 0x94a0, BASE + 0x94a1, True),
    ("progress_write_exact", BASE + 0x94b8, BASE + 0x94b9, True),
]


def safe_create_label(addr, name):
    try:
        if getSymbolAt(addr) is None:
            createLabel(addr, name, True)
    except:
        pass


def create_anchor_labels():
    safe_create_label(toAddr(BASE + 0x7c9c), "STR_BOOT_OS_UPDATE_TITLE")
    safe_create_label(toAddr(BASE + 0x7cf8), "STR_BOOT_LOADING_OS_FILE")
    safe_create_label(toAddr(BASE + 0x7d14), "STR_BOOT_OS_FILE_NOT_FOUND")
    safe_create_label(toAddr(BASE + 0x7fa8), "STR_BOOT_FILE_WRITE_ERROR")
    safe_create_label(toAddr(BASE + 0x80ca), "STR_BOOT_FLASH_ERASE_ERROR")
    safe_create_label(toAddr(BASE + 0x80e7), "STR_BOOT_FLASH_WRITE_ERROR")
    safe_create_label(toAddr(BASE + 0x8104), "STR_BOOT_FLASH_READ_ERROR")
    safe_create_label(toAddr(BASE + 0x94a0), "STR_FLASH_PROGRESS_ERASE")
    safe_create_label(toAddr(BASE + 0x94b8), "STR_FLASH_PROGRESS_WRITE")


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


def score_candidate(pdis, start, site):
    try:
        cur = start
        count = 0
        covers_site = False
        limit = site.add(8)
        while count < 24 and cur.compareTo(limit) <= 0:
            ins = pdis.disassemble(cur)
            if ins is None:
                return -1
            count += 1
            if ins.getMinAddress().compareTo(site) <= 0 and ins.getMaxAddress().compareTo(site) >= 0:
                covers_site = True
            nxt = ins.getMaxAddress().next()
            if nxt is None or nxt.compareTo(cur) <= 0:
                return -1
            cur = nxt
        if not covers_site:
            return -1
        return (count * 100) + int(site.getOffset() - start.getOffset())
    except:
        return -1


def choose_seed_start(site):
    pdis = PseudoDisassembler(currentProgram)
    best = None
    best_score = -1
    for delta in range(0x40, -2, -2):
        cand = site.subtract(delta)
        score = score_candidate(pdis, cand, site)
        if score > best_score:
            best = cand
            best_score = score
    return best


def disassemble_from(addr):
    if getInstructionAt(addr) is not None:
        return
    cmd = DisassembleCommand(addr, None, True)
    cmd.applyTo(currentProgram, monitor)


def main():
    out_path = None
    args = getScriptArgs()
    if len(args) > 0:
        out_path = args[0]

    memory = currentProgram.getMemory()
    listing = currentProgram.getListing()
    create_anchor_labels()

    raw_hits = {}
    for name, start_value, end_value, exact_only in RANGES:
        raw_hits[name] = scan_for_refs(memory, start_value, end_value, exact_only)

    seed_sites = []
    for addr in raw_hits["progress_block"]:
        seed_sites.append(addr)

    boot_bins = {}
    for addr in raw_hits["boot_update_block"]:
        bin_id = (addr.getOffset() - BASE) // 0x100
        boot_bins[bin_id] = boot_bins.get(bin_id, 0) + 1

    for addr in raw_hits["boot_update_block"]:
        bin_id = (addr.getOffset() - BASE) // 0x100
        if boot_bins.get(bin_id, 0) >= 2:
            seed_sites.append(addr)

    report_lines = []
    report_lines.append("program\t{}".format(currentProgram.getName()))
    report_lines.append("image_base\t0x09000000")
    report_lines.append("boot_update_hits\t{}".format(len(raw_hits["boot_update_block"])))
    report_lines.append("progress_hits\t{}".format(len(raw_hits["progress_block"])))

    for name in raw_hits:
        idx = 0
        for addr in raw_hits[name]:
            safe_create_label(addr, "ref_{}_{}".format(name, idx))
            idx += 1

    unique_starts = set()
    for site in seed_sites:
        start = choose_seed_start(site)
        if start is None:
            start = site
        if start.getOffset() in unique_starts:
            continue
        unique_starts.add(start.getOffset())
        disassemble_from(start)
        func = listing.getFunctionContaining(start)
        if func is None:
            func = createFunction(start, "UPD_{:08x}".format(int(start.getOffset())))
        if func is not None:
            report_lines.append("seed_function\t{}\t{}".format(func.getName(), func.getEntryPoint()))
        else:
            report_lines.append("seed_failed\t{}".format(start))

    if out_path is not None:
        out_file = open(out_path, "w")
        for line in report_lines:
            out_file.write(line + "\n")
        out_file.close()


main()
