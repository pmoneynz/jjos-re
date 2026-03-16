# T0016/T0017 Normal-Boot Logic Pair Test (No updater path required)

## Objective

Validate a logic-path behavior change in a guaranteed startup UI path, independent of update-flow card checks.

## Files

- Control (no-op): `hardware_candidates/mpc2500_t0016_control_noop_boot_display.bin`
- Test (logic): `hardware_candidates/mpc2500_t0017_logic_boot_display_ptr_shift.bin`

## Patch behavior

- T0016: exact baseline behavior.
- T0017: one-byte instruction change at `0xB50` (`59d6` -> `5bd6`) retargeting a boot display pointer selection in the RAM-check UI code path.

## Procedure (single CF card)

1. Put **T0016** on CF as `mpc2500.update` (or the filename that your hardware currently accepts for this workflow).
2. Boot and capture the RAM-check/startup display screen.
3. Put **T0017** on same CF with same filename.
4. Boot again and capture the same RAM-check/startup display screen.
5. Repeat once to confirm consistency.

## Required captures

- One clear photo per run showing the same boot stage.
- Label photos as `T0016_runX` and `T0017_runX`.
- Record whether both variants still boot into normal UI (regression check).

## Pass criteria for 8.2 evidence

- **Behavior-change proven** if T0017 consistently shows a startup-display difference vs T0016 in the same stage, with no uncontrolled boot regression.
- If identical output appears in both, this logic change did not produce a visible differential and another runtime logic target is needed.
