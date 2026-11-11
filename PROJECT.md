# PTZ driver board

A driver board for PTZ camera heads and its firmware, designed together from scratch. One board that can drive any
head the owner builds. A new 3D head is being designed at the same time, so each can shape the other.

## Owner
Aernout Ottens: product owner, reviewer, orders the boards and does the bring-up. Claude designs and builds.

## Core value
A new head with different mechanics needs a configuration change only: no new board, no new firmware (CORE-01).

## Scope
- v1, later and out of scope: `specs/PRD.md`. Criteria in `specs/modules/`.
- Unplaced ideas: `IDEAS.md`.
- Earlier designs in `docs/history/` and the firmware in `../PTZ-head` are reference only.

## Stack
KiCad 10 with KiCAD-MCP-Server, kicad-happy and Freerouting; JLCPCB with SMD assembly; an ESP32-S3 module and C++ firmware.
