# Second Diagnostic Pair Instructions (Post-Card-Check Branch)

## Files

- `hardware_candidates/mpc2500_t0012_diag_control_postcard_force_idx10.bin`
- `hardware_candidates/mpc2500_t0013_diag_t0008_postcard_force_idx11.bin`

## What this pair tests

This pair forces the **later dispatch callsite** at `0x1080`:
- T0012 forces message-table index `10`
- T0013 forces message-table index `11` and keeps T0008 compare shift

If this post-card-check path is actually reached, T0012 and T0013 should diverge.

## One-CF-card procedure

1. Copy T0012 file to CF as `mpc2500.update`.
2. Enter update flow exactly as in successful prior runs.
3. Capture the displayed message/result.
4. Replace with T0013 file (same filename).
5. Repeat exact same steps and capture message/result.
6. Repeat A/B once more for consistency.

## Interpretation

- **Different messages/paths:** post-card-check branch is being exercised; strong logic-path proof.
- **Same `Wrong card !!` again:** test is still failing upstream before forced post-card-check dispatch, and this branch path is not being reached in your current workflow.
