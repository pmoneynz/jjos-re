# Third Diagnostic Pair Instructions (All-Dispatch Forced A/B)

## Files

- `hardware_candidates/mpc2500_t0014_diag_control_all_dispatch_force_idx10.bin`
- `hardware_candidates/mpc2500_t0015_diag_t0008_all_dispatch_force_idx11.bin`

## Why this pair exists

Prior diagnostics may not have reached the intended callsite.  
This pair forces index values at **all three** `FUN_000016fc` dispatch callsites:

- T0014 forces index `10`
- T0015 forces index `11` (+ T0008 cmp shift retained)

So whichever dispatch path is active, A/B should diverge if diagnostic code is executing.

## One-card tester procedure

1. Put T0014 on CF as `mpc2500.update`.
2. Enter same update workflow used in previous tests.
3. Capture first message/result screen.
4. Replace with T0015 (same filename), repeat exactly.
5. Run A/B twice for consistency.

## Interpretation

- **Different messages (e.g., index-10-like vs index-11-like):**
  - logic-path forcing worked, and branch-controlled behavior is proven.
- **Still identical `Wrong card !!`:**
  - device is rejecting before any patched dispatch path executes in current workflow/media state.
