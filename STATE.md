# PTZ driver board — State

_Last updated: 2026-11-10_

This file is the handoff: where we are, what is next, what waits. It is not a log.

## Current focus
The research phase, before the hardware is fixed. Findings are in `docs/research/README.md`. Targets are approved and the first camera is a G7 with a 14-140 mm. The
TMC5240 passed its datasheet check; on real hardware it is untested. Leading: stepper, one belt stage at 6.25:1 to 7.5:1 in a base of at most Ø165 mm, TMC5240, ESP32-C6-MINI-1U (chosen for JLC Economic), SPI sensor. Open: 12 or 24 V. No schematic exists.

The rig's frame is modelled and reviewed on paper for a base of Ø165 mm: `specs/modules/rig.md` holds print list, parts and assembly order. Nothing is printed, ordered or built. The reviewer did not see the last round of fixes.

## Next
Rev A runs as one Fable 5.2 session from `docs/prompts/fable-board-rev-a.md`, once PR #1 and #2 are merged. The rig work below continues alongside it.

1. The owner prints `pulley_120T`, `fit_seat` and `fit_shaft` to test tooth shape and fits, and orders the parts in `specs/modules/rig.md`. Results may change `BEARING_FIT`, `SHAFT_D`, `HEX_FIT`, `GROOVE_W` or `GROOVE_D`.
2. R-TR: write the rig firmware (RIG-08..12) and the wiring and bring-up checklists. The owner chose to print first.
3. To rebuild the model after any change: `mechanica/rig/fusion_rebuild.py` build, check and export, then `check_print.py`. The model in Fusion is not saved; `export/rig.f3d` is the copy.

## Waiting for a run on hardware (gate 3, owner)
- none

## Blocked
- none

## Owner decisions open
- PR #1, then PR #2 on top of it: both open, for the owner to review and merge.
- The remaining **[OPEN]** lines in `specs/PRD.md`.
- Confirm owned: ESP32 dev board, lab supply to 24 V, 1/4" camera bolt, ball-end hex key. Which 14-140 mm: 265 g or 460 g.
- The repository is public without a licence, so all rights stay reserved until one is added.
