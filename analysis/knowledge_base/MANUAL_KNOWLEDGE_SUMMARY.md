# MPC2500 Manual-Derived Knowledge Summary

This file distills manual-backed facts that are directly useful for firmware reverse engineering and patch deployment planning.

## 1) Update Path Constraints (Manual-backed)

### Proven enough to operationalize

- Update media path is Compact Flash-centric; USB is used as a transport to storage media, not as direct live flashing from host PC.
  - Evidence: service notes L174-L196, operator manual L2671-L2707.
- Service workflow references entering update while holding **Window** on power-up.
  - Evidence: service notes L193-L196.
- Service update screen references file token `M25V100B.BIN` and action key `F6 (DO IT)`.
  - Evidence: service notes L187-L193, L196.

### Operational implication

For hardware trials, default to CF-based update media and treat direct USB-to-flash assumptions as invalid until proven otherwise.

## 2) Storage and USB Behavior

- CF supported size: **32MB to 2GB**.
  - Evidence: operator manual L2390, L2776.
- USB mode is explicitly mass-storage behavior around removable media/internal HDD visibility.
  - Evidence: operator manual L2671-L2699.
- In USB mode, device workflow is constrained until clean removal/disconnect.
  - Evidence: operator manual L2697-L2707.

### Operational implication

When preparing test media, enforce:
1. compatible CF size,
2. clean USB eject/removal process,
3. explicit logging of storage mode and filename used.

## 3) Hardware Components Relevant to RE

- Service parts list includes CPU-board flash component `AM29LV641DL90REI` (IC2).
  - Evidence: service notes L248-L249.
- Service text references JIG PC Flash ROM via socket `J110` on CPU board.
  - Evidence: service notes L208, L249.

### Operational implication

Flash command-sequence reverse engineering should prioritize patterns compatible with AMD AM29LV64x family behavior.

## 4) Test / Hidden Modes (Use Caution)

- Service notes include text for Test OS and hidden mode entry combos (Owner Name, parameter init, demo mode), but OCR quality is fragmented.
  - Evidence: service notes L201-L212.

### Operational implication

Treat hidden-mode claims as **medium confidence** until validated on hardware or cleaner source scans.

## 5) Confidence and Risk Notes

- This knowledge base is OCR-derived. Some lines are partially merged or fragmented.
- Facts with confidence `high` in `manual_facts.json` are suitable for immediate workflow use.
- Facts with confidence `medium` should be used as hypotheses unless corroborated by:
  - hardware observation, or
  - cleaner manual extraction.

See: `analysis/knowledge_base/manual_facts.json` and `analysis/knowledge_base/MANUAL_SOURCES.md`.

