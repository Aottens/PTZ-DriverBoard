# PTZ driver board — State

_Last updated: 2026-11-04_

This file is the handoff: where we are, what is next, what waits. It is not a log.

## Current focus
The research phase, before the hardware is fixed. Findings are in `docs/research/README.md`. Targets are approved and the first camera is a G7 with a 14-140 mm. The
TMC5240 passed its datasheet check; on real hardware it is untested. Leading: stepper, one belt stage at 6.25:1 to 7.5:1 in a base of at most Ø165 mm, TMC5240, ESP32-S3-MINI-1U, SPI sensor. Open: 12 or 24 V. No schematic exists.

## Next
1. R-TR: rebuild the rig model in Fusion from `mechanica/rig/build_rig.py`, and export. Needs Fusion running and connected to the session. The old exports are removed; there are none until then.
2. The owner prints one pulley to test the tooth shape, then orders the parts in `specs/modules/rig.md`.

## Waiting for a run on hardware (gate 3, owner)
- none

## Blocked
- none

## Owner decisions open
- The remaining **[OPEN]** lines in `specs/PRD.md`.
