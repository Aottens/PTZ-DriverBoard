# PTZ driver board — State

_Last updated: 2026-11-12_

This file is the handoff: where we are, what is next, what waits. It is not a log.

## Current focus
**Rev B of the board is designed and ready for a JLC quote** (RB-02, PR #5): a two-layer carrier of 100 × 80 mm for
plug-in drivers, MCU and Ethernet. The estimate for five assembled boards is €68 to €90, of the €100 in COST-01
(`docs/research/rev-b-cost.md`). A third blind review of the board as ordered says order, with nothing to change
(`hardware/review/HANDLED.md`). Nothing is ordered and nothing is measured.

Rev A is under the git tag `rev-a`; `hardware/` now holds Rev B.

The research phase goes on beside it: findings in `docs/research/README.md`. The rig can still overturn part choices
(the sensor, the belt ratio). The rig's frame is modelled and reviewed on paper: `specs/modules/rig.md`.

## Next
1. The owner reviews and merges PR #5, then uploads `hardware/fab/ptz-driver_gerbers.zip` and the two files in
   `hardware/fab/jlc/` to JLC for the real quote, ticks the preview checklist in the PR, and orders (RB-03).
2. The owner buys the modules and through-hole parts for one head: `hardware/sourcing/owner_bom.md`. The loose parts
   come from Reichelt (`owner_bom_reichelt.csv`), the modules and socket strips from TinyTronics.
3. Bring-up from `tests/hardware/bringup-rev-b.md`, soldering section by section (RB-04).
4. Rig: the owner prints `pulley_120T`, `fit_seat` and `fit_shaft` and orders the parts in `specs/modules/rig.md`;
   then R-TR, the rig firmware and its checklists.
5. The first firmware spec (FW-01): four axes of step pulses on the ESP32-S3, with `firmware/include/pins.h` as given.

## Waiting for a run on hardware (gate 3, owner)
- Rev B bring-up: `tests/hardware/bringup-rev-b.md` (after the order arrives).

## Blocked
- none

## Owner decisions open
- The remaining **[OPEN]** lines in `specs/PRD.md`.
- Which W5500 module to buy: two are named, with what differs.
- Confirm owned: lab supply to 17 V with a current limit, 1/4" camera bolt, ball-end hex key. Which 14-140 mm: 265 g or 460 g.
- The repository is public without a licence, so all rights stay reserved until one is added.
