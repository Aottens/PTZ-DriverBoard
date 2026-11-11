# PTZ driver board — State

_Last updated: 2026-11-11_

This file is the handoff: where we are, what is next, what waits. It is not a log.

## Current focus
**Rev A of the driver board is designed and waits for the owner's review of its pull request (#3).** Nothing is ordered.
The board is 100 × 80 mm, four layers, all parts on top: four TMC5240, ESP32-C6-MINI-1U, W5500 with the jack off the board,
RS-485, CAN, USB-C, four sensor ports, four external driver ports. Its checks are green (DRC 0 violations and 0 unconnected,
ERC 0, `check_netlist.py` 963 pins, `check_board.py`, `check_fit.py`), and the blind review found nothing critical; a second look after the fixes says the board can be ordered. What was
done with each finding is in `hardware/review/HANDLED.md` and `DECISIONS.md` (2026-11-11). Nothing on it has been measured.

The research phase goes on beside it: findings in `docs/research/README.md`. The rig can still overturn part choices
(12 or 24 V, the sensor, the belt ratio). The rig's frame is modelled and reviewed on paper: `specs/modules/rig.md`.
Nothing is printed, ordered or built.

## Next
1. The owner reviews and merges PR #3 (gate 2).
2. Before any order (S3-04, order gate in `CLAUDE.md`): the owner uploads `hardware/fab/ptz-driver_gerbers.zip` and the two
   files in `hardware/fab/jlc/` to JLCPCB, walks the preview checklist in the pull request (pin 1 and rotation of every
   polar part, D102 first), and rechecks stock against `hardware/sourcing/jlc_check.md`. Only the owner orders.
3. When boards arrive: `tests/hardware/bringup-rev-a.md`, current-limited, copied to `tests/hardware/runs/`.
4. Rig: the owner prints `pulley_120T`, `fit_seat` and `fit_shaft` and orders the parts in `specs/modules/rig.md`;
   then R-TR, the rig firmware and its checklists.
5. To rebuild the rig model after a change: `mechanica/rig/fusion_rebuild.py`, then `check_print.py`. The model in Fusion is
   not saved; `export/rig.f3d` is the copy.

## Waiting for a run on hardware (gate 3, owner)
- `tests/hardware/bringup-rev-a.md`: the first power-up of Rev A, once boards exist (S4-01).

## Blocked
- none

## Owner decisions open
- PR #3: review and merge.
- Order Rev A now, or wait for the rig? A rig result can still change the board: see the pull request's list.
- JLC options at the order: HASL or ENIG, and the X-ray charge for the module (`hardware/review/HANDLED.md`, K13).
- The remaining **[OPEN]** lines in `specs/PRD.md`.
- Confirm owned: ESP32 dev board, lab supply to 24 V, 1/4" camera bolt, ball-end hex key. Which 14-140 mm: 265 g or 460 g.
- The repository is public without a licence, so all rights stay reserved until one is added.
