# PTZ driver board — State

_Last updated: 2026-11-04_

This file is the handoff: where we are, what is next, what waits. It is not a log.

## Current focus
The research phase, before the hardware is fixed. Findings are in `docs/research/README.md`. The TMC5240 passed its datasheet check; on real hardware it is untested. Leading: stepper, about
30:1 belts, TMC5240, ESP32-S3-MINI-1U, SPI sensor, 24 V. No schematic exists.

## Next
1. R-01: the owner approves the targets, and gives the longest lens and sensor size.
2. R-TR: design a one-axis test rig with the owner. It answers motor, driver, reduction and sensor cable together.

## Waiting for a run on hardware (gate 3, owner)
- none

## Blocked
- none

## Owner decisions open
- Targets TGT-01..05 in `specs/PRD.md`.
- The remaining **[OPEN]** lines in `specs/PRD.md`.
