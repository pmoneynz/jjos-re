# MPC2500 OS Reverse Engineering Checklist (Pass/Fail Gated)

This checklist is designed for autonomous agent execution.  
Every step has a hard gate: **PASS** to continue, **FAIL** to stop/escalate/fix.

---

## Operating Rules (Do Not Skip)

1. **Evidence-first**: no claims without artifacts.
2. **One change per trial**: each test isolates one variable.
3. **Hash everything**: input/output SHA-256 for every binary.
4. **No destructive hardware write tests** until dry-run gates are passed.
5. **Label confidence**:
   - **Proven** = control/data flow and reproducible evidence
   - **Hypothesis** = plausible, not yet proven

---

## Required Artifact Set Per Trial

For each trial `TXXXX`, produce:

- patch spec JSON (`analysis/patch_specs/*.json`)
- manifest JSON (`analysis/output/*manifest.json`)
- trial log entry (`analysis/output/patch_experiment_log.md`)
- candidate binary (if hardware run intended)
- hardware outcome record (photo/video + structured notes)

If any artifact is missing: **FAIL** the trial.

---

## Phase 0 - Workspace Integrity Gate

### Step 0.1 - Repository and branch sanity
- Action:
  - confirm correct branch
  - confirm clean working tree or document dirty files
- PASS:
  - branch is expected task branch
  - no unknown unintended modifications
- FAIL:
  - wrong branch, untracked mystery files, or accidental edits
- Evidence:
  - `git status --short --branch` output captured in notes

### Step 0.2 - Baseline firmware fingerprint
- Action:
  - compute SHA-256 of baseline firmware
- PASS:
  - hash matches expected baseline for this project run
- FAIL:
  - hash mismatch (wrong file/version)
- Evidence:
  - baseline hash recorded in trial notes/log

---

## Phase 1 - Toolchain Validation Gate

### Step 1.1 - Patch tooling smoke test
- Action:
  - run:
    - `python3 analysis/firmware_patch_tool.py inspect --firmware mpc2500_jv313.bin`
- PASS:
  - command succeeds
  - known string targets render correctly
- FAIL:
  - command error or unreadable/shifted target bytes
- Evidence:
  - command output with firmware hash and target strings

### Step 1.2 - Static scan regeneration sanity
- Action:
  - run: `python3 analysis/scan_firmware.py mpc2500_jv313.bin`
- PASS:
  - `analysis/output/report.md` and `summary.json` regenerate without error
- FAIL:
  - script errors or malformed output
- Evidence:
  - regenerated timestamp + clean script exit

---

## Phase 2 - Architecture and Flow Ground Truth Gate

### Step 2.1 - Architecture consistency check
- Action:
  - verify current findings still support SuperH import path
  - read:
    - `analysis/output/ghidra_sh_findings.md`
    - `analysis/output/ghidra_sh_update_map.md`
- PASS:
  - no contradictory evidence stronger than current SuperH proof
- FAIL:
  - new contradictory evidence appears
- Evidence:
  - short note: "SuperH path remains/does not remain authoritative"

### Step 2.2 - Update spine verification
- Action:
  - reconfirm references for:
    - `ENTRY_INIT`
    - `FUN_00008c44`
    - `FUN_00008b8c`
    - `FUN_00008ed6`
    - `FUN_00008db4`
- PASS:
  - call chain remains reproducible in current artifacts
- FAIL:
  - missing function refs or contradictory callsites
- Evidence:
  - addresses and callsites listed in session notes

---

## Phase 3 - Candidate Patch Authoring Gate

### Step 3.1 - Patch target classification
- Action:
  - classify target as:
    - cosmetic (safe)
    - logic (moderate/high risk)
    - flash path / boot critical (high risk)
- PASS:
  - risk class declared and justified
- FAIL:
  - target selected without classification
- Evidence:
  - one-line rationale in trial log

### Step 3.2 - Spec construction (single variable)
- Action:
  - create JSON patch spec with exactly one change for first trial
  - enforce same-length replacement for cosmetic trial
- PASS:
  - spec parses and has expected/replacement length equality
- FAIL:
  - multiple uncontrolled edits or length mismatch
- Evidence:
  - spec file committed

### Step 3.3 - Deterministic apply
- Action:
  - run `firmware_patch_tool.py apply ... --manifest ...`
- PASS:
  - manifest generated
  - input/output sizes valid
  - patch count exactly expected
- FAIL:
  - expected bytes mismatch, range error, or missing manifest
- Evidence:
  - manifest JSON with hashes + byte-level diff

---

## Phase 4 - Static Candidate Validation Gate

### Step 4.1 - Byte-level verification
- Action:
  - inspect patched candidate at target offsets
- PASS:
  - only intended bytes changed
- FAIL:
  - unintended deltas found
- Evidence:
  - before/after byte dumps in manifest/log

### Step 4.2 - Candidate registry update
- Action:
  - append trial entry to `analysis/output/patch_experiment_log.md`
- PASS:
  - includes goal, hashes, offset, before/after, status
- FAIL:
  - missing log row or incomplete fields
- Evidence:
  - committed log diff

---

## Phase 5 - Hardware Dry-Run Gate (No Flash Commit)

### Step 5.1 - Media and filename discipline
- Action:
  - prepare media with controlled filename (start with expected updater naming)
  - record filesystem and filename
- PASS:
  - media prep method documented
- FAIL:
  - undocumented media/filename
- Evidence:
  - structured operator notes

### Step 5.2 - Device behavior capture
- Action:
  - capture photo/video of:
    - load attempt
    - acceptance/rejection message
    - whether candidate-specific visual change appears
- PASS:
  - clear outcome visible
- FAIL:
  - ambiguous/no capture
- Evidence:
  - media file references + textual summary

### Step 5.3 - Safety condition
- Action:
  - do not flash if dry-run evidence is incomplete
- PASS:
  - no destructive write attempted before dry-run conclusion
- FAIL:
  - flash attempt without gate closure
- Evidence:
  - explicit "no flash write executed" or staged approval note

---

## Phase 6 - Integrity Enforcement Characterization Gate

Run a controlled matrix (`A/B/C/...`) with one-variable edits.

Recommended minimal matrix:
1. late UI string patch
2. startup banner patch
3. single-byte neutral-region patch
4. control/original

### Step 6.1 - Matrix execution quality
- PASS:
  - each candidate has unique spec + manifest + outcome
- FAIL:
  - missing candidate artifacts or mixed variables

### Step 6.2 - Decision output
- PASS:
  - one of these conclusions is evidence-backed:
    - modified images always rejected (global integrity likely)
    - region-dependent acceptance (localized checks likely)
    - broad acceptance (weak/no integrity in tested path)
- FAIL:
  - conclusion based on anecdotes or partial data

---

## Phase 7 - Validation/Flash Routine RE Gate

### Step 7.1 - Error string branch mapping
- Action:
  - map branch conditions for:
    - `File data error`
    - `OS data error`
    - `Wrong file`
- PASS:
  - each error has triggering branch/function documented
- FAIL:
  - string known but no branch condition proof
- Evidence:
  - function+address+condition notes in findings doc

### Step 7.2 - Flash routine proof
- Action:
  - identify first proven erase/program/verify routines
  - prove by command-sequence behavior and address access patterns
- PASS:
  - erase/program/verify functions each identified with proof
- FAIL:
  - only "low-level I/O" found without flash command proof
- Evidence:
  - updated findings map with exact routines and callsites

---

## Phase 8 - Feature Patch Readiness Gate

### Step 8.1 - Readiness decision
- PASS only if all are true:
  1. acceptance/rejection behavior is characterized
  2. integrity strategy exists (recompute/bypass/etc. with evidence)
  3. rollback path exists
  4. first logic patch is minimal and reversible
- FAIL:
  - any missing condition

### Step 8.2 - First logic patch protocol
- Action:
  - one logic patch only
  - same artifact discipline (spec, manifest, outcome capture)
- PASS:
  - reproducible behavior change without uncontrolled side effects
- FAIL:
  - non-reproducible or broad regression

---

## Mandatory Fail-Path Actions (When Any Gate Fails)

1. Stop progression immediately.
2. Record:
   - failing step ID
   - observed output
   - hypothesis for cause
3. Open a recovery task:
   - smallest corrective action
   - expected proof artifact after fix
4. Re-run only the failed gate and dependent downstream gates.

No silent continuation after FAIL.

---

## Minimal Session Closeout (Required)

At end of each agent run, publish:

1. Completed steps (PASS)
2. Failed steps (FAIL) with cause
3. New/updated artifacts
4. Next single highest-priority gate

If this summary is missing, the run is incomplete.

