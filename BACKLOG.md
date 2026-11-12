# PTZ driver board — Backlog

One sentence per task with a verifiable done criterion; T-shirt size (S ≤ 2 h, M ≤ half day,
L ≤ day, XL = split it); the owner reviews every PR.
Status (first word of the Status cell, checked by `scripts/check-tracking.py` in CI):
`todo` · `doing` · `done` · `gate3` · `blocked`, details in brackets or after a colon.
- A task PR sets its own row to `done (date, #PR)` in the PR itself: **merged = done**.
- `gate3: <checklist path>` = merged, only the owner's run on hardware is left; the path must exist.
- Open points found in a run become their own row (or an IDEA) in the same PR.

Everything after the research phase is a proposal: their `Builds:` lines and full criteria come when each slice starts.

## Slice 0 — harness

| Id | Task (one sentence, verifiable) | Spec ids | Size | Status |
| --- | --- | --- | --- | --- |
| S0-01 | The harness, tooling config and PRD draft are in this repo and `scripts/check-tracking.py` passes. | CORE-01 | S | done (2026-11-04) |
| S0-02 | A GitHub repository exists, with `tracking.yml` green on a first PR. | CORE-01 | S | done (2026-11-04, #1) |

## Research phase — before the hardware is fixed

Questions and first findings: `docs/research/README.md`. Each closes with an entry in `DECISIONS.md`.

| Id | Task (one sentence, verifiable) | Spec ids | Size | Status |
| --- | --- | --- | --- | --- |
| R-01 | The owner approves the targets, and gives the longest lens and sensor size. | CORE-01, TGT-01..05 | S | done (2026-11-04, #1) |
| R-02 | The motor technology is decided in `DECISIONS.md`, with R-T1 as evidence. | DRV-01 | S | todo |
| R-03 | The driver is decided, on its datasheet and R-T1. | DRV-02..06 | M | doing: TMC5240 datasheet checked, rig left |
| R-04 | The MCU is decided, with a pin table for every signal checked against its datasheet, including strapping pins. | CTL-01 | M | todo |
| R-05 | The sensor and bus are decided on repeatability data and R-T2. | ENC-01..04 | M | todo |
| R-06 | The board size, heat path and base layout are agreed with a first 3D concept, with a calculation of temperature at the current per axis. | BRD-01, BRD-04, DRV-05, MEC-01..08 | L | todo |
| R-07 | The supply voltage is decided from the R-01 numbers. | POW-01, POW-04 | S | todo |
| R-08 | The reduction per axis is decided from R-T1. | TGT-02..05 | S | todo |
| R-TR | A one-axis test rig is designed with the owner, printed and running on a TMC5240 breakout. | RIG-01..12 | L | doing: frame modelled for Ø165, firmware next |
| R-T1 | The owner's run on the rig records slowest clean move, fastest quiet move and the stop, on screen and by ear at 1 and 2 m, at 6.25:1 and 7.5:1. | TGT-02..05 | M | todo |
| R-T2 | On the rig, the owner's run counts sensor read errors over the longest cable next to the motor, I2C against SPI, records read noise at standstill, and how close a preset lands after a restart. | ENC-04, ENC-06 | M | todo |

## Rev A — one run

Covers S2-01 to S3-03 below. The research questions and slice 1 stay open: the rig can still overturn part choices, and the 3D head follows the board.

| Id | Task (one sentence, verifiable) | Spec ids | Size | Status |
| --- | --- | --- | --- | --- |
| RA-01 | One Fable 5.2 session delivers one PR with specs, checks, KiCad project, JLC files, bring-up checklist and handled blind review, from `docs/prompts/fable-board-rev-a.md`. | POW, DRV, ENC, CTL, CAM, AUX, BRD | XL | done (2026-11-11, #3) |

## Slice 1 — what the board is

| Id | Task (one sentence, verifiable) | Spec ids | Size | Status |
| --- | --- | --- | --- | --- |
| S1-01 | The owner approves the PRD with no OPEN line left and the research closed (gate 1). | CORE-01 | S | todo |
| S1-02 | The first 3D design of the new head holds the agreed board, heat path, bore and sensor positions. | MEC-01..07, BRD-01 | L | todo |

## Slice 2 — schematic

| Id | Task (one sentence, verifiable) | Spec ids | Size | Status |
| --- | --- | --- | --- | --- |
| S2-01 | Module specs have numbered criteria per block, with datasheet revisions noted (gate 1). | POW, DRV, ENC, CTL, CAM, AUX | L | done (2026-11-11, #3) |
| S2-02 | The KiCad project is set up and `check_netlist.py` fails on every expected pin of the approved specs. | POW, DRV, ENC, CTL | M | done (2026-11-11, #3) |
| S2-03 | Power section: its checks are green and ERC is clean. | POW-01..06 | M | done (2026-11-11, #3) |
| S2-04 | Drivers and MCU: their checks are green and ERC is clean. | DRV-01..06, CTL-01 | L | done (2026-11-11, #3) |
| S2-05 | Sensors, ports and I/O: all checks are green and ERC is clean. | ENC, CTL, CAM, AUX | L | done (2026-11-11, #3) |

## Slice 3 — board and order

| Id | Task (one sentence, verifiable) | Spec ids | Size | Status |
| --- | --- | --- | --- | --- |
| S3-01 | Placement and layout are routed, with DRC clean and 0 unconnected. | BRD-01..03, DRV-05 | L | done (2026-11-11, #3) |
| S3-02 | `make_jlc.py` produces BOM and CPL that fit the EasyEDA footprints. | BRD-02 | S | done (2026-11-11, #3) |
| S3-03 | The blind review is written and each finding is fixed or accepted. | CORE-01 | M | done (2026-11-11, #3) |
| S3-04 | The owner orders, after the order gate in `CLAUDE.md`. | BRD-02 | S | blocked: Rev A is not ordered on cost (2026-11-11), Rev B replaces it |

## Rev B — a cheap board for plug-in modules

| Id | Task (one sentence, verifiable) | Spec ids | Size | Status |
| --- | --- | --- | --- | --- |
| RB-01 | The owner approves the Rev B PRD and the cost estimate in `docs/research/rev-b-cost.md` (gate 1). | COST-01..03, CORE-01 | S | done (2026-11-11) |
| RB-02 | One Fable 5.2 session delivers one PR with Rev B's specs, checks, KiCad project, JLC files, a redone cost estimate within COST-01 and a handled blind review, from `docs/prompts/fable-board-rev-b.md`. | COST, POW, DRV, ENC, CTL, AUX, BRD | XL | done (2026-11-11, #5) |
| RB-03 | The owner uploads `hardware/fab/` to JLC, finds the quote at most €100, ticks the preview checklist of PR #5 and the stock of every line, and orders. | COST-01, BRD-02, BRD-12 | S | todo |
| RB-04 | The owner's current-limited bring-up run of Rev B passes, section by section, while the through-hole parts and modules go on. | POW, DRV, ENC, CTL, AUX | M | gate3: `tests/hardware/bringup-rev-b.md` |
| RB-05 | The base of the head gives the board what `hardware/ASSEMBLY.md` asks: 25 mm of height, openings for USB and the Ethernet jack, the antenna bulkhead, an air path along the drivers. | BRD-01, BRD-07, MEC-01 | M | todo |
| RB-06 | `hardware/sourcing/owner_bom.py` makes the owner's shopping list from the schematic: every part JLC does not assemble, with plugs, contacts and sockets, LCSC numbers, stock and prices, and a CSV for LCSC's BOM tool. | BRD-08 | S | done (2026-11-11, #6) |
| RB-07 | The shopping list names a 5 V regulator that comes with the LCSC order, YLPTEC's K7805-1000R3, with its data sheet read against POW-07 and the choice in `DECISIONS.md`. | POW-07, BRD-08 | S | done (2026-11-11, #7) |
| RB-08 | The shopping list buys inside the EU: the loose parts at Reichelt with article numbers and prices, the socket strips at TinyTronics, the Traco regulator again; the JLC estimate counts the EU import charge. | BRD-08, BRD-12, POW-07 | S | done (2026-11-11, #8) |
| RB-09 | A third blind review covers the board as it is ordered, the one routed again after the second review, and each finding is fixed, accepted or answered in `hardware/review/HANDLED.md`. | BRD-10, BRD-02 | S | done (2026-11-12, #9) |

## Slice 4 — bring-up and firmware

| Id | Task (one sentence, verifiable) | Spec ids | Size | Status |
| --- | --- | --- | --- | --- |
| S4-01 | The owner's current-limited bring-up run passes per power rail. | POW-01..06, AUX-05 | M | todo |
| S4-02 | A firmware skeleton builds and its host tests run. | FW-01 | M | todo |
| S4-03 | One axis moves through a command and stops on the watchdog, on the real board. | DRV-02, FW-02, FW-07 | L | todo |
