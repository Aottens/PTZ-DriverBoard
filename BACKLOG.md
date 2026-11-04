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
| R-01 | The owner gives camera, lens, axes, speeds, noise and landing accuracy, and they are written down as numbers. | CORE-01 | S | todo |
| R-02 | The motor technology is decided in `DECISIONS.md`, with T-1 as evidence. | DRV-01 | S | todo |
| R-03 | The driver is decided, with every `[geheugen]` and `[bron]` claim for it checked against the datasheets. | DRV-02..06 | M | todo |
| R-04 | The MCU is decided, with a pin table for every signal checked against its datasheet, including strapping pins. | CTL-01 | M | todo |
| R-05 | The sensor and bus are decided on repeatability data and T-2. | ENC-01..04 | M | todo |
| R-06 | The board size, heat path and base layout are agreed with a first 3D concept, with a calculation of temperature at the current per axis. | BRD-01, BRD-04, DRV-05, MEC-01..06 | L | todo |
| R-07 | The supply voltage is decided from the R-01 numbers. | POW-01, POW-04 | S | todo |
| R-T1 | The owner records the slowest clean pan on the old head, fully zoomed in. | DRV-01 | S | todo |
| R-T2 | The owner's bench test counts sensor read errors over the longest cable next to a running stepper, I2C against SPI. | ENC-04 | M | todo |

## Slice 1 — what the board is

| Id | Task (one sentence, verifiable) | Spec ids | Size | Status |
| --- | --- | --- | --- | --- |
| S1-01 | The owner approves the PRD with no OPEN line left and the research closed (gate 1). | CORE-01 | S | todo |
| S1-02 | The first 3D design of the new head holds the agreed board, heat path, bore and sensor positions. | MEC-01..07, BRD-01 | L | todo |

## Slice 2 — schematic

| Id | Task (one sentence, verifiable) | Spec ids | Size | Status |
| --- | --- | --- | --- | --- |
| S2-01 | Module specs have numbered criteria per block, with datasheet revisions noted (gate 1). | POW, DRV, ENC, CTL, CAM, AUX | L | todo |
| S2-02 | The KiCad project is set up and `check_netlist.py` fails on every expected pin of the approved specs. | POW, DRV, ENC, CTL | M | todo |
| S2-03 | Power section: its checks are green and ERC is clean. | POW-01..06 | M | todo |
| S2-04 | Drivers and MCU: their checks are green and ERC is clean. | DRV-01..06, CTL-01 | L | todo |
| S2-05 | Sensors, ports and I/O: all checks are green and ERC is clean. | ENC, CTL, CAM, AUX | L | todo |

## Slice 3 — board and order

| Id | Task (one sentence, verifiable) | Spec ids | Size | Status |
| --- | --- | --- | --- | --- |
| S3-01 | Placement and layout are routed, with DRC clean and 0 unconnected. | BRD-01..03, DRV-05 | L | todo |
| S3-02 | `make_jlc.py` produces BOM and CPL that fit the EasyEDA footprints. | BRD-02 | S | todo |
| S3-03 | The blind review is written and each finding is fixed or accepted. | CORE-01 | M | todo |
| S3-04 | The owner orders, after the order gate in `CLAUDE.md`. | BRD-02 | S | todo |

## Slice 4 — bring-up and firmware

| Id | Task (one sentence, verifiable) | Spec ids | Size | Status |
| --- | --- | --- | --- | --- |
| S4-01 | The owner's current-limited bring-up run passes per power rail. | POW-01..06, AUX-05 | M | todo |
| S4-02 | A firmware skeleton builds and its host tests run. | FW-01 | M | todo |
| S4-03 | One axis moves through a command and stops on the watchdog, on the real board. | DRV-02, FW-02, FW-07 | L | todo |
