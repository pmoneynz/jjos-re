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

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.RefType;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

public class ReportUpdatePath extends GhidraScript {

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
		Memory memory = currentProgram.getMemory();
		Listing listing = currentProgram.getListing();

		Map<String, List<Address>> hits = new LinkedHashMap<>();
		for (RefRange range : RANGES) {
			hits.put(range.name, scanForReferences(memory, range));
		}

		Map<Function, Set<String>> functionTags = new LinkedHashMap<>();
		Map<Function, Set<Address>> functionRefSites = new LinkedHashMap<>();

		for (Map.Entry<String, List<Address>> entry : hits.entrySet()) {
			for (Address refSite : entry.getValue()) {
				Function function = listing.getFunctionContaining(refSite);
				if (function == null) {
					continue;
				}
				functionTags.computeIfAbsent(function, key -> new LinkedHashSet<>()).add(entry.getKey());
				functionRefSites.computeIfAbsent(function, key -> new LinkedHashSet<>()).add(refSite);
			}
		}

		List<Function> functions = new ArrayList<>(functionTags.keySet());
		Collections.sort(functions, Comparator.comparingLong(f -> f.getEntryPoint().getOffset()));

		List<String> lines = new ArrayList<>();
		lines.add("# Ghidra Update Path Map");
		lines.add("");
		lines.add("- Program: `" + currentProgram.getName() + "`");
		lines.add("- Processor: `68000:BE:32:Coldfire`");
		lines.add("- Image base: `0x09000000`");
		lines.add("");
		lines.add("## Reference Summary");
		lines.add("");
		for (Map.Entry<String, List<Address>> entry : hits.entrySet()) {
			lines.add("- `" + entry.getKey() + "` refs: `" + entry.getValue().size() + "`");
		}
		lines.add("");
		lines.add("## Seeded Function Map");
		lines.add("");

		for (Function function : functions) {
			lines.add("### `" + function.getName() + "`");
			lines.add("");
			lines.add("- Entry: `" + function.getEntryPoint() + "`");
			lines.add("- Tags: `" + join(functionTags.get(function)) + "`");
			lines.add("- Ref sites: `" + joinAddresses(functionRefSites.get(function)) + "`");
			lines.add("- Callers: `" + joinAddresses(getCallers(function)) + "`");
			lines.add("- Callees: `" + joinFunctionCalls(function) + "`");
			lines.add("");
		}

		lines.add("## Observations");
		lines.add("");
		lines.add("- Functions tagged with `progress_block` are the strongest current flash/write routine candidates.");
		lines.add("- Functions tagged only with `boot_update_block` are more likely to belong to verification, load/update UI, or error handling.");
		lines.add("- Missing `progress_write_exact` refs means the write-progress string may be reached through a nearby pointer or table, not a direct immediate.");
		lines.add("");

		if (outPath != null) {
			writeLines(outPath, lines);
		}
	}

	private List<Address> scanForReferences(Memory memory, RefRange range) throws Exception {
		List<Address> results = new ArrayList<>();
		for (MemoryBlock block : memory.getBlocks()) {
			if (!block.isInitialized()) {
				continue;
			}
			long endOffset = block.getEnd().getOffset() - 3;
			for (long off = block.getStart().getOffset(); off <= endOffset && !monitor.isCancelled(); off += 2) {
				Address addr = toAddr(off);
				long value = readUnsignedInt(memory, addr);
				boolean match = range.exactOnly ? value == range.start
						: (value >= range.start && value < range.end);
				if (match) {
					results.add(addr);
				}
			}
		}
		Collections.sort(results, Comparator.comparingLong(Address::getOffset));
		return results;
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

	private List<Address> getCallers(Function function) {
		List<Address> callers = new ArrayList<>();
		ReferenceIterator iterator =
			currentProgram.getReferenceManager().getReferencesTo(function.getEntryPoint());
		while (iterator.hasNext()) {
			Reference reference = iterator.next();
			if (reference.getReferenceType().isCall()) {
				callers.add(reference.getFromAddress());
			}
		}
		Collections.sort(callers, Comparator.comparingLong(Address::getOffset));
		return callers;
	}

	private String joinFunctionCalls(Function function) {
		Set<String> calls = new LinkedHashSet<>();
		Instruction instruction = getInstructionAt(function.getEntryPoint());
		while (instruction != null && function.getBody().contains(instruction.getAddress())) {
			if (instruction.getFlowType().isCall()) {
				Address[] flows = instruction.getFlows();
				for (Address flow : flows) {
					Function callee = getFunctionAt(flow);
					if (callee != null) {
						calls.add(callee.getName() + "@" + callee.getEntryPoint());
					}
					else {
						calls.add("SUB@" + flow);
					}
				}
			}
			instruction = instruction.getNext();
		}
		return calls.isEmpty() ? "-" : join(calls);
	}

	private String joinAddresses(Set<Address> values) {
		if (values == null || values.isEmpty()) {
			return "-";
		}
		List<Address> rows = new ArrayList<>(values);
		Collections.sort(rows, Comparator.comparingLong(Address::getOffset));
		List<String> rendered = new ArrayList<>();
		for (Address addr : rows) {
			rendered.add(addr.toString());
		}
		return String.join(", ", rendered);
	}

	private String join(List<Address> values) {
		if (values == null || values.isEmpty()) {
			return "-";
		}
		List<String> rendered = new ArrayList<>();
		for (Address addr : values) {
			rendered.add(addr.toString());
		}
		return String.join(", ", rendered);
	}

	private String join(Set<String> values) {
		if (values == null || values.isEmpty()) {
			return "-";
		}
		return String.join(", ", values);
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
