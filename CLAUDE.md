# CLAUDE.md — how to work in this repo

A driver board for PTZ camera heads and its firmware, designed together from scratch.
Read `PROJECT.md`, `STATE.md`, `ARCHITECTURE.md` and `DECISIONS.md` before doing anything.
Talk to the owner in **Dutch**; write specs, code, comments and commits in **English**.

## The loop: spec → test → build → review

1. **Spec first.** Every feature has a spec in `specs/modules/<module>.md` with numbered acceptance
   criteria (`POW-03`, `DRV-02`, …), growing out of the ids in `specs/PRD.md`. No net, part or code
   for a criterion that has no number. If the spec is missing or unclear, write or extend it and stop
   for owner approval (gate 1).
2. **Test second.** A criterion gets its check before the design that meets it:
   - **Schematic:** an expected pin → net entry in `hardware/check_netlist.py`, derived from the spec
     and a datasheet, never from the schematic. Named per criterion id: `def pow_03_...`.
   - **Board:** ERC and DRC clean through `kicad-cli`, and a check for each number the spec states.
   - **Firmware:** a host test named after the id (`test_drv_02_...`) in `firmware/test/`, against
     pure logic with no hardware.
3. **Build third, by a Sonnet subagent.** The main session writes spec and failing checks; a Sonnet
   subagent (`model: sonnet`) makes the smallest change that turns them green; the main session
   reviews the diff before it goes to the owner.
4. **Review.** One branch and one PR per build on GitHub; the owner reviews and merges (gate 2).
   Anything only a real board can show ships with a checklist in `tests/hardware/` that only the owner
   can tick (gate 3).
5. **Close the loop.** Update `STATE.md`, `BACKLOG.md` and `README.md` in the same PR. The README stays
   a README: a new feature goes under *What works today*; `## Status` is rewritten, never appended to,
   at most 8 lines (checked). A decision made along the way goes in `DECISIONS.md`.
   **Merged = done:** the PR sets its own `BACKLOG.md` row to `done (date, #PR)`, or
   `gate3: <checklist path>` when only the owner's run is left.
   Open points found in a run go under `## Open points` in the run file, each ending in `→` its backlog
   row, IDEA or checklist. `STATE.md` is the handoff, not a log. `scripts/check-tracking.py` checks this
   in CI. **Every PR description has a `## Tracking` section** with the output of
   `scripts/check-tracking.py --summary origin/main`.
6. **Clean up after the merge.** In the owner's checkout on `main`:
   `git fetch --prune && git branch -vv | awk '/: gone]/{print $1}' | xargs git branch -D`.

Use the `project-orchestrator` agent in `.claude/agents/` for pre-flight and post-flight checks.

## Builds and sessions

- A build is one session, one branch and one PR, holding one task or a few that belong together: at
  most three tasks and at most one of them M. An L or XL is a build of its own.
- One commit per task, so a task can be reverted alone. Each task gets its own Sonnet subagent with
  its own brief: criteria ids, failing checks, files to read and what the task before it left.
- When a task outgrows its size or review finds a defect in the approach, ship what is done and move
  the rest to the next build.
- A session that changes files gets its own worktree. Never check out or pull in the owner's checkout
  while another session works there.

## The order gate

A board order costs money and weeks, and cannot be undone. Nothing is ordered until all of these hold,
and then only the owner orders:
1. Every criterion in scope is checked, `check_netlist.py` is green, ERC and DRC are clean.
2. A **blind review** in `hardware/review/`: a fresh subagent gets only the functional brief, the
   design files and the datasheets, not our reasoning, and tags each finding `[zeker]` or `[vermoeden]`.
3. Every KRITIEK and BELANGRIJK finding is fixed or accepted in writing in `DECISIONS.md`.
4. All parts are in stock at JLC on the day of the order.
5. The JLC preview is checked for pin 1 and rotation of each polar part, by a checklist in the PR.

## Hardware rules

- **Claude cannot measure.** Every claim about behaviour is a calculation with its inputs written down,
  a datasheet page, or a run by the owner. Say "the calculation shows X", never "this works".
- **Datasheet per part.** Each active part has its datasheet revision noted in the spec, and its pinout
  is checked against the pages, pin by pin.
- **The schematic holds the truth.** The LCSC number is a field on the symbol, so BOM and schematic
  cannot drift apart (scoreboard review, K7).
- **All SMD on the top side** unless a spec says otherwise (bottom-side CPL rotation was the scoreboard's
  largest open risk, B1).
- **Silkscreen is part of the design:** pin 1, polarity and voltage at every connector, port names, and
  board name with revision and date (scoreboard review, B2 and K1).
- **Leave the knob.** Anything the real world can move stays adjustable from firmware or a solder jumper:
  current per axis, thresholds, offsets, polarities.
- **Every power-up of a new board is current-limited first**, from a checklist in `tests/hardware/`.

## Firmware rules

- Logic that decides anything (trajectories, limits, protocol parsing) is plain C++ with no framework
  includes, so it runs in host tests. Hardware access stays in thin glue.
- A motor never runs without a watchdog: lost control input, a failed sensor read or a fault flag stops it.
- Pins live in one place only, which `check_netlist.py` reads too, so firmware and board cannot disagree.

## Ideas intake

The owner drops ideas in chat. Record each one in `IDEAS.md` and ask the owner to confirm its phase. No
criteria or design for an idea until its phase is planned.

## Toolchain notes

- **KiCad 10.0.6.** CLI: `/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli`. Python with `pcbnew`:
  `/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3`.
- **KiCAD-MCP-Server** in `~/Tools/KiCAD-MCP-Server`, wired through `.mcp.json`; loads at session start.
- **Review:** plugin `kicad-happy`, enabled in `.claude/settings.json`.
- **Routing:** Freerouting 2.4.1, `~/.kicad-mcp/freerouting.jar`, run with
  `/opt/homebrew/opt/openjdk@26/bin/java` directly on a DSN export of the file. Not through the MCP's
  `autoroute`, which exports its own possibly stale copy from memory.
- **Production:** `hardware/fab/make_jlc.py` fits rotation and centre on the EasyEDA footprint JLC uses
  (template: `RunningScoreboard/hardware/fab/make_jlc.py`). Rerun after every board change.
- **Firmware:** PlatformIO at `~/.platformio/penv/bin/pio`. Stack still to decide (`specs/PRD.md`, FW-01).

## Commit style

`<area>: <imperative summary>`, for example `hardware: add input protection (POW-02)`.
Reference criterion ids in the body. One commit per task, one build per PR.
