# Diagnostic A/B Instructions (Single CF Card)

## Files to test

- Control diagnostic: `hardware_candidates/mpc2500_t0009_diag_control_force_status10.bin`
- T0008 diagnostic: `hardware_candidates/mpc2500_t0010_diag_t0008_force_status10.bin`

## Purpose

These builds force the dispatch status register to `10` before the compare site:

- T0009 keeps compare as `cmp/eq #10,r0`
- T0010 uses `cmp/eq #11,r0` (T0008 logic shift)

If logic patch is active, these two should diverge in visible message path.

## Procedure (one CF card)

1. Copy `mpc2500_t0009_diag_control_force_status10.bin` to CF as `mpc2500.update`.
2. Boot into update flow and reach the result/error message screen.
3. Capture screenshot of message text.
4. Replace file on same CF with `mpc2500_t0010_diag_t0008_force_status10.bin` (same filename `mpc2500.update`).
5. Repeat exact same steps and capture screenshot.
6. Repeat entire A/B once more for consistency.

## Evidence required

For each run:
- firmware variant (`T0009` or `T0010`)
- message text shown
- photo reference
- whether flash commit was reached/executed

## Pass criterion for behavior-change proof

T0008 logic change is considered proven if T0010 consistently shows a different message/path than T0009 under the same forced-status diagnostic scenario.
