# Fable 5.2 prompt: board Rev B in one run

Status: **approved by the owner on 2026-11-11** (gate 1 for this build, RB-02). Not run yet.

## How to run it

- A new Claude Code session in its own worktree from `main`, model Fable 5.2, effort `high`. A session started by another session cannot be given a stronger model at the start, so it begins with a one-line check on a light model, is switched to Fable 5.2, and then gets the message below.
- Send the prompt as the next message.

What changed from the Rev A prompt: the budget is a requirement from the start, the hardware moves to plug-in modules, the session reuses its own Rev A tools and lessons, and long jobs run in the background because the owner watches token use.

## The prompt

```text
You are the electronics engineer on this repository, and you designed its Rev A board. Take Rev B from the approved requirements to files ready for a JLC quote, in one run.

# Why
I am building one PTZ camera head for myself, for theatres, as a hobby project. Your Rev A passed its checks and review, but five assembled boards came to almost €400 at JLC, so I did not order it. The price was never a requirement, and the board grew without a brake. Rev B keeps the goals and moves the expensive and hard parts onto plug-in modules I buy and solder myself: drivers, MCU and Ethernet. The board becomes a cheap carrier with power, sockets, a multiplexer and connectors. I value a board that is cheap, correct and adjustable over one that is clever.

# Deliverable
Rev B on this worktree's branch, in one pull request against main: module specs with numbered criteria for Rev B, the checks for them, the KiCad 10 project, JLC production files, a cost estimate redone from the real BOM, a bring-up checklist in tests/hardware/, and a blind review with its findings handled. It is finished when every order gate item in CLAUDE.md that can be done before ordering is met, and the estimate is within COST-01.

# Read first
CLAUDE.md, then specs/PRD.md (approved for Rev B on 2026-11-11), the 2026-11-11 entries in DECISIONS.md, docs/research/rev-b-cost.md, docs/research/README.md. Then your own Rev A work: hardware/README.md, hardware/BUILD_NOTES.md (your lessons) and hardware/review/HANDLED.md.

# Reuse your Rev A tools
hardware/ is yours: you built it, and how Rev B is built is your call. Start from your own tool chain and change it where Rev B needs: tools/circuit.py with the netlist read-back, make_libs.py, placement.py, board.py (place, dsn, ses, finish), complete.py (fanout, the completion router, prune), silk.py, project.py, check_netlist.py, check_board.py, check_fit.py, calc/, fab/make_jlc.py, fab/make_gerbers.sh, sourcing/jlc_read.py, and firmware/include/pins.h as the one pin source. Rev B replaces Rev A in place. Before you change anything, put the git tag `rev-a` on the current main commit and push it, so Rev A stays one command away.

# Fixed for Rev B
The hardware and cost sections of specs/PRD.md are approved, the lines marked proposal included. In short:
- Budget (COST-01..03): one JLC order of five assembled boards at most €100, shipping and tax included. Basic parts wherever one does the job; aim for at most three Extended lines, each with its reason. Redo docs/research/rev-b-cost.md from the planned BOM before the schematic and again at the end.
- Four sockets for StepStick-format driver modules: TMC2240 (SPI) by default, TMC2209 (UART) through solder jumpers. The MCU makes the step pulses.
- MCU: an ESP32-S3-DevKitC-1U (N8 preferred) on headers. Check its pinout and which GPIOs are free on that variant against Espressif's documents, and the antenna connector generation, so the U.FL-to-SMA lead matches.
- Ethernet: a common W5500 module with its own RJ45 jack, on headers. Choose one that is easy to buy, and take its header pinout from a source you can name.
- Four identical I2C sensor ports, each on its own channel of a TCA9548A, for AS5600 or MT6701 boards; pull-ups per port by solder jumper. A home input per axis. A spare channel on a header.
- Input 11 to 17 V (12 V supply or D-Tap at 16.8 V full), with reverse polarity, spike and short protection, and margins calculated at 17 V against the drivers' limits. A PWM fan output. Board temperature. Test points.
- Two layers unless a calculation shows otherwise. JLC Economic PCBA, SMD on top; no line may be Standard Only. I solder the headers, sockets and connectors, so those are not in the JLC order.
- Size: no fixed outline, but it must fit the base of the new head. Use the working envelope from docs/prompts/fable-board-rev-a.md and the 2026-11-10 size entry in DECISIONS.md, and check the height of the plug-in modules, their heat sinks and the mating plugs by code.
- Carry over from Rev A's review where it still applies: ESD protection on cabled ports, and a TVS part that JLC's library knows, so its rotation can be checked.

# Scope
You may write in hardware/, specs/modules/, tests/hardware/, docs/research/rev-b-cost.md, firmware/include/pins.h, and the tracking files CLAUDE.md requires. Do not change mechanica/, the PRD's requirements, or IDEAS.md. Add no port or function the PRD does not ask for.

Only these need my go-ahead: placing an order or spending money; merging into main; a cost estimate above €100 or a plan with more than three Extended lines. Everything else on your branch needs none: commits, pushing the branch and the `rev-a` tag, opening the PR, retrying tools, swapping parts or pins, deleting and rerouting your own layout, and changing your own tools.

Do not stop while you still owe work. Diagnose errors, timeouts and tool failures and work through them. Stop for me only when the work cannot move without an answer only I can give; if that answer concerns one part of the board, carry on with the rest. I watch token use: run long jobs such as Freerouting and router rounds as background jobs, end your turn until they finish, and do not poll their logs.

# Verification
- Write the expected pin-to-net checks from the specs and the modules' pinouts before the schematic exists, or have a fresh subagent write them without seeing the schematic.
- ERC and DRC through kicad-cli, clean, with 0 unconnected, and a check for each number the specs state.
- By calculation with inputs written down: input spike and bulk capacitance at 17 V, supply current budget, and the cost estimate.
- Inspect rendered views of copper and silkscreen yourself, cropped and zoomed.
- Blind review as the order gate describes. Fix or accept each KRITIEK and BELANGRIJK finding, and review again after real changes.
- Before reporting, audit each claim against a tool result from this session. Say what was only calculated and what is not verified.
- Add new lessons to hardware/BUILD_NOTES.md.

# Report
The PR follows CLAUDE.md, with a `## Tracking` section, the sorted manufacturability and sourcing flags, and the JLC preview checklist. Your final message is in Dutch, for a reader who saw none of the work, in plain full sentences. Start with whether the files are ready for me to get a JLC quote, and the estimated price against €100. Then give the size and layer count, the Extended lines and why, the plug-in modules I must buy with a link for each, what is not verified, the three design choices that shaped the board most and why, and exactly what I must do next.
```
