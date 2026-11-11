# PTZ driver board — State

_Last updated: 2026-11-11_

This file is the handoff: where we are, what is next, what waits. It is not a log.

## Current focus
**Rev B is specified: a cheap board for plug-in modules, at most €100 per JLC order of five.** The PRD and the
cost estimate (`docs/research/rev-b-cost.md`, about €58 to €92) are approved (RB-01). No schematic exists yet.

Rev A is designed, merged (#3) and not ordered: the quote came to almost €400. It stays in `hardware/` as reference; its
schematic, checks and tools can be reused.

The research phase goes on beside it: findings in `docs/research/README.md`. The rig can still overturn part choices
(12 or 24 V, the sensor, the belt ratio). The rig's frame is modelled and reviewed on paper: `specs/modules/rig.md`.
Nothing is printed, ordered or built.

## Next
1. Rev B build (RB-02): one Fable 5.2 session from `docs/prompts/fable-board-rev-b.md`, from `main` once this is merged.
2. At its end the owner uploads the files to JLC for a real quote, against COST-01.
3. Rig: the owner prints `pulley_120T`, `fit_seat` and `fit_shaft` and orders the parts in `specs/modules/rig.md`;
   then R-TR, the rig firmware and its checklists.
4. To rebuild the rig model after a change: `mechanica/rig/fusion_rebuild.py`, then `check_print.py`. The model in Fusion is
   not saved; `export/rig.f3d` is the copy.

## Waiting for a run on hardware (gate 3, owner)
- none (Rev A is not ordered; its bring-up checklist stays as reference)

## Blocked
- none

## Owner decisions open
- The remaining **[OPEN]** lines in `specs/PRD.md`.
- Confirm owned: ESP32 dev board, lab supply to 24 V, 1/4" camera bolt, ball-end hex key. Which 14-140 mm: 265 g or 460 g.
- The repository is public without a licence, so all rights stay reserved until one is added.
