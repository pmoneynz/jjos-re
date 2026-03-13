//@category Analysis

import java.io.File;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.app.script.GhidraScript;
import ghidra.app.util.PseudoDisassembler;
import ghidra.app.util.PseudoInstruction;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.SourceType;

public class SeedUpdatePath extends GhidraScript {

	private static class RefRange {
		String name;
		long start;
		long end;
		boolean exactOnly;

		RefRange(String name, long start, long end, boolean exactOnly) {
			this.name = name;
			this.start = start;
			this.end = end;
			this.exactOnly = exactOnly;
		}
	}

	private static final long BASE = 0x09000000L;

	private static final RefRange[] RANGES = new RefRange[] {
		new RefRange("boot_update_block", BASE + 0x7be0, BASE + 0x8130, false),
		new RefRange("progress_block", BASE + 0x94a0, BASE + 0x94d0, false),
		new RefRange("progress_erase_exact", BASE + 0x94a0, BASE + 0x94a1, true),
		new RefRange("progress_write_exact", BASE + 0x94b8, BASE + 0x94b9, true),
	};

	@Override
	public void run() throws Exception {
		String outPath = getScriptArgs().length > 0 ? getScriptArgs()[0] : null;
		Listing listing = currentProgram.getListing();
		Memory memory = currentProgram.getMemory();

		createAnchorLabels();

		Map<String, List<Address>> rawHits = new LinkedHashMap<>();
		for (RefRange range : RANGES) {
			rawHits.put(range.name, scanForReferences(memory, range));
		}

		List<Address> seedSites = new ArrayList<>();
		seedSites.addAll(rawHits.get("progress_block"));

		Map<Long, Integer> bootBins = new LinkedHashMap<>();
		for (Address hit : rawHits.get("boot_update_block")) {
			long bin = ((hit.getOffset() - BASE) / 0x100L);
			Integer count = bootBins.get(bin);
			bootBins.put(bin, count == null ? 1 : count + 1);
		}

		for (Address hit : rawHits.get("boot_update_block")) {
			long bin = ((hit.getOffset() - BASE) / 0x100L);
			if (bootBins.get(bin) != null && bootBins.get(bin) >= 2) {
				seedSites.add(hit);
			}
		}

		Set<Long> uniqueSeeds = new LinkedHashSet<>();
		List<String> reportLines = new ArrayList<>();
		reportLines.add("program\t" + currentProgram.getName());
		reportLines.add("image_base\t0x09000000");
		reportLines.add("boot_update_hits\t" + rawHits.get("boot_update_block").size());
		reportLines.add("progress_hits\t" + rawHits.get("progress_block").size());

		for (Map.Entry<String, List<Address>> entry : rawHits.entrySet()) {
			int index = 0;
			for (Address hit : entry.getValue()) {
				String label = "ref_" + entry.getKey() + "_" + index;
				safeCreateLabel(hit, label);
				index++;
			}
		}

		for (Address site : seedSites) {
			Address start = chooseSeedStart(site);
			if (start == null) {
				start = site;
			}
			if (!uniqueSeeds.add(start.getOffset())) {
				continue;
			}
			disassembleFrom(start);
			Function function = listing.getFunctionContaining(start);
			if (function == null) {
				String name = String.format("UPD_%08x", start.getOffset());
				function = createFunction(start, name);
			}
			if (function != null) {
				reportLines.add(String.format("seed_function\t%s\t%s", function.getName(),
					function.getEntryPoint()));
			}
			else {
				reportLines.add(String.format("seed_failed\t%s", start));
			}
		}

		if (outPath != null) {
			writeLines(outPath, reportLines);
		}
	}

	private void createAnchorLabels() throws Exception {
		safeCreateLabel(toAddr(BASE + 0x7c9c), "STR_BOOT_OS_UPDATE_TITLE");
		safeCreateLabel(toAddr(BASE + 0x7cf8), "STR_BOOT_LOADING_OS_FILE");
		safeCreateLabel(toAddr(BASE + 0x7d14), "STR_BOOT_OS_FILE_NOT_FOUND");
		safeCreateLabel(toAddr(BASE + 0x7fa8), "STR_BOOT_FILE_WRITE_ERROR");
		safeCreateLabel(toAddr(BASE + 0x80ca), "STR_BOOT_FLASH_ERASE_ERROR");
		safeCreateLabel(toAddr(BASE + 0x80e7), "STR_BOOT_FLASH_WRITE_ERROR");
		safeCreateLabel(toAddr(BASE + 0x8104), "STR_BOOT_FLASH_READ_ERROR");
		safeCreateLabel(toAddr(BASE + 0x94a0), "STR_FLASH_PROGRESS_ERASE");
		safeCreateLabel(toAddr(BASE + 0x94b8), "STR_FLASH_PROGRESS_WRITE");
	}

	private void safeCreateLabel(Address address, String name) {
		try {
			if (getSymbolAt(address) == null) {
				createLabel(address, name, true, SourceType.ANALYSIS);
			}
		}
		catch (Exception ignored) {
			// Ghidra will throw on duplicate/invalid labels. Ignore and continue.
		}
	}

	private List<Address> scanForReferences(Memory memory, RefRange range) throws Exception {
		List<Address> hits = new ArrayList<>();
		for (MemoryBlock block : memory.getBlocks()) {
			if (!block.isInitialized()) {
				continue;
			}
			Address start = block.getStart();
			long endOffset = block.getEnd().getOffset() - 3;
			for (long off = start.getOffset(); off <= endOffset && !monitor.isCancelled(); off += 2) {
				Address addr = toAddr(off);
				long value = readUnsignedInt(memory, addr);
				boolean match = range.exactOnly ? value == range.start
						: (value >= range.start && value < range.end);
				if (match) {
					hits.add(addr);
				}
			}
		}
		Collections.sort(hits, Comparator.comparingLong(Address::getOffset));
		return hits;
	}

	private long readUnsignedInt(Memory memory, Address address) throws Exception {
		byte[] bytes = new byte[4];
		int read = memory.getBytes(address, bytes);
		if (read != 4) {
			return -1;
		}
		return ((bytes[0] & 0xffL) << 24) | ((bytes[1] & 0xffL) << 16) | ((bytes[2] & 0xffL) << 8) |
			(bytes[3] & 0xffL);
	}

	private Address chooseSeedStart(Address site) throws Exception {
		PseudoDisassembler pdis = new PseudoDisassembler(currentProgram);
		Address best = null;
		int bestScore = -1;
		for (int delta = 0x40; delta >= 0; delta -= 2) {
			Address cand = site.subtract(delta);
			int score = scoreCandidate(pdis, cand, site);
			if (score > bestScore) {
				bestScore = score;
				best = cand;
			}
		}
		return best;
	}

	private int scoreCandidate(PseudoDisassembler pdis, Address start, Address site) {
		try {
			Address cur = start;
			int count = 0;
			boolean coversSite = false;
			while (count < 24 && cur.compareTo(site.add(8)) <= 0) {
				PseudoInstruction ins = pdis.disassemble(cur);
				if (ins == null) {
					return -1;
				}
				count++;
				Address next = ins.getMaxAddress().next();
				if (next == null || next.compareTo(cur) <= 0) {
					return -1;
				}
				if (ins.getMinAddress().compareTo(site) <= 0 &&
					ins.getMaxAddress().compareTo(site) >= 0) {
					coversSite = true;
				}
				cur = next;
			}
			if (!coversSite) {
				return -1;
			}
			return (count * 100) + (int) (site.getOffset() - start.getOffset());
		}
		catch (Exception e) {
			return -1;
		}
	}

	private void disassembleFrom(Address start) throws Exception {
		Instruction existing = getInstructionAt(start);
		if (existing != null) {
			return;
		}
		DisassembleCommand cmd = new DisassembleCommand(start, null, true);
		cmd.applyTo(currentProgram, monitor);
	}

	private void writeLines(String outPath, List<String> lines) throws Exception {
		File outFile = new File(outPath);
		outFile.getParentFile().mkdirs();
		PrintWriter writer = new PrintWriter(outFile);
		try {
			for (String line : lines) {
				writer.println(line);
			}
		}
		finally {
			writer.close();
		}
	}
}
