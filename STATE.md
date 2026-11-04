# PTZ driver board — State

_Last updated: 2026-11-04_

This file is the handoff: where we are, what is next, what waits. It is not a log.

## Current focus
The research phase, before the hardware is fixed. Findings are in `docs/research/README.md`. Targets are approved and the first camera is a G7 with a 14-140 mm. The
TMC5240 passed its datasheet check; on real hardware it is untested. Leading: stepper, about 30:1 belts, TMC5240, ESP32-S3-MINI-1U, SPI sensor. Open: 12 or 24 V. No schematic exists.

## Next
1. The owner orders the rig parts from `specs/modules/rig.md`, and prints the 96T first to test the tooth shape.
2. R-TR: write the rig firmware (RIG-08..12) and the wiring and bring-up checklists.

## Waiting for a run on hardware (gate 3, owner)
- none

## Blocked
- none

## Owner decisions open
- The remaining **[OPEN]** lines in `specs/PRD.md`.
