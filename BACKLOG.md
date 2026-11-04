# PTZ driver board — Backlog

One sentence per task with a verifiable done criterion; T-shirt size (S ≤ 2 h, M ≤ half day,
L ≤ day, XL = split it); the owner reviews every PR.
Status (first word of the Status cell, checked by `scripts/check-tracking.py` in CI):
`todo` · `doing` · `done` · `gate3` · `blocked`, details in brackets or after a colon.
- A task PR sets its own row to `done (date, #PR)` in the PR itself: **merged = done**.
- `gate3: <checklist path>` = merged, only the owner's run on hardware is left; the path must exist.
- Open points found in a run become their own row (or an IDEA) in the same PR.

Slices after 1 are a proposal: their `Builds:` lines and full criteria come when each slice starts.

## Slice 0 — harness

| Id | Task (one sentence, verifiable) | Spec ids | Size | Status |
| --- | --- | --- | --- | --- |
| S0-01 | The harness, tooling config and PRD draft are in this repo and `scripts/check-tracking.py` passes. | CORE-01 | S | done (2026-11-04) |
| S0-02 | A GitHub repository exists, with `tracking.yml` green on a first PR. | CORE-01 | S | todo |

## Slice 1 — what the board is

| Id | Task (one sentence, verifiable) | Spec ids | Size | Status |
| --- | --- | --- | --- | --- |
| S1-01 | The owner approves the PRD with no OPEN line left (gate 1). | CORE-01 | S | todo |
| S1-02 | The 3D design has the MEC requirements, and a written board outline, height and connector zones come back. | MEC-01..07, BRD-01 | S | blocked: where does the 3D design live? |
| S1-03 | A power and thermal calculation shows how many amps per axis the board can carry at 12 and 24 V. | POW-04, DRV-05 | M | todo |
| S1-04 | A pin table for every signal fits the ESP32-S3 against its datasheet, including strapping pins. | CTL-01, DRV-04 | M | todo |
| S1-05 | The owner's bench test shows encoder reads stay clean over the longest cable run, next to a running stepper. | ENC-04 | M | todo |

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
