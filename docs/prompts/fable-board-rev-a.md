# Fable 5.2 prompt: board Rev A in one run

Status: **approved by the owner on 2026-11-10** (gate 1 for this build). Not run yet.

## How to run it

- A new Claude Code session in its own worktree, model Fable 5.2, effort `high`. Anthropic's guide puts long unattended runs at `high` and keeps `xhigh` for work where it measurably helps. Permission mode must allow file edits and the KiCad tools, or the run stalls on prompts.
- Start from `main`, after PR #1 and #2 are merged.
- Paste the prompt as the first message.

The exceptions this run needs are written into the rules themselves (`CLAUDE.md`, `specs/PRD.md`, `docs/research/README.md`, `BACKLOG.md`), because Fable 5.2 applies written rules closely and a separate exception line works much less well in Anthropic's tests.

## The prompt

```text
You are the electronics engineer on this repository. Take a motor-control board from requirements to files ready to order at JLCPCB, in one run.

# Why
I am building one PTZ camera head for myself, for use in theatres among the audience. I want one compact driver board, with its own firmware later, that can drive this head and later ones through configuration alone. The 3D head does not exist yet. Rev A is a real prototype: it will first replace the breakout boards on my one-axis test rig, and that rig may still overturn some part choices. So I value a board that is correct, measurable and adjustable over one that is clever. I also want to learn what you can do on a task of this size.

# Deliverable
Rev A on branch `board-rev-a`, in one pull request: module specs with numbered criteria, the checks for them, a KiCad 10 project in `hardware/`, JLC production files, a bring-up checklist in `tests/hardware/`, and a blind review with its findings handled. It is finished when every item of the order gate in CLAUDE.md that can be done before ordering is met.

# Read first
CLAUDE.md is the working agreement; follow it, including the changes made for this build. Then specs/PRD.md, docs/research/README.md, DECISIONS.md, IDEAS.md, specs/modules/rig.md. For how I built my last board with these same tools: ~/Documents/Projects/RunningScoreboard/hardware (check_netlist.py, fab/make_jlc.py, review/BLINDE_REVIEW.md, DESIGN.md).

# Fixed for Rev A
Requirements: the POW, DRV, ENC, CTL, CAM, AUX and BRD sections of specs/PRD.md count as approved, with these changes.
- Parts: the leading candidates in docs/research/README.md are the design basis: TMC5240 on each of four axes, an SPI position sensor port per axis, 12 to 24 V input with margin to the driver's 41 V absolute maximum by calculation. Replace a candidate only when a datasheet or sourcing rules it out, and name that in the PR.
- MCU: ESP32-C6-MINI-1U-H4 (LCSC C20627095), assembled by JLC. I chose it over the ESP32-S3 because JLC lists every ESP32-S3 module as Standard Only, and because the TMC5240 generates the motion itself. It brings out 22 GPIOs including USB, and has one user SPI bus (datasheet v1.5). My rough count is about 27 signals, so expect an I2C expander and a chip-select decoder, but the pin plan is yours. Anything that stops a motor stays on a direct pin. Mind the strapping pins GPIO4, 5, 8, 9 and 15, and keep the long sensor cable from loading the bus that the drivers and Ethernet share.
- Ethernet: W5500 and an RJ45 jack on the board, assembled. If space runs out, replace the jack with a header for an off-board jack first, then drop the CAN connector, and record what you did.
- Camera: two open-drain outputs on one small connector, for tally and record trigger.
- Size: at most 85 x 65 mm. Smaller is welcome only when heat, routing and probing do not suffer. Four M3 mounting holes.

Assembly is JLC Economic PCBA (jlcpcb.com/capabilities/pcb-assembly-capabilities, read 2026-11-10): top side only, standard stack-up only, 0.8 to 1.6 mm, smallest package 0402, smallest IC pitch 0.4 mm, no castellated holes or edge plating, HASL (ENIG only on some green 1.6 mm boards), no solder paste inspection, fixed 255 C reflow. One BOM line marked Standard Only moves the whole order to Standard. The field "PCBA Type" on https://jlcpcb.com/partdetail/<LCSC number> says which it is, and WebFetch reads it. Check every assembled line that way and keep the result in the repo. WS2812-style 5050 LEDs have been Standard Only.

Fit: my working envelope is a base of 160 mm inner diameter, with a 42 x 42 mm pan motor centred 55.7 mm from the axis. The board lies flat beside that motor in a volume about 35 mm tall, below the pulley plane. Cables from the hollow pan shaft arrive above the board. One long edge faces the motor with about 1 mm gap, so no connectors there. The other three edges have at least 28 mm to the wall. Parts plus mating plugs stay within 25 mm above the board. USB-C and the antenna connector must be reachable from outside. Check this envelope by code, with connectors and their mating plugs.

# Scope
hardware/ does not exist yet and is yours: how it is built is your call, and later boards will build on it. You may also write in specs/modules/, tests/hardware/, and the tracking files CLAUDE.md requires. Firmware is out of scope, except the single pin source that check_netlist.py reads. Do not change mechanica/, firmware decisions or IDEAS.md. Add no port or function that the PRD does not ask for; RS-232, LANC and a slip ring were struck on purpose.

Only two actions need my go-ahead: placing an order or spending money, and merging into main. Everything else on your branch needs none: commits, pushing the branch, opening the PR, retrying tools, swapping parts or pins, deleting and rerouting your own layout, writing helper scripts or a small router in hardware/.

Do not stop while you still owe work. Diagnose errors, timeouts and tool failures and work through them. Stop for me only when the work cannot move without an answer only I can give; if that answer concerns one part of the board, carry on with the rest. Datasheets from analog.com and LCSC do not load through WebFetch or curl; open them in the built-in browser. Do not disguise a client to get past a block.

# Verification
- Write the expected pin-to-net checks from the specs and datasheets before the schematic exists, or have a fresh subagent write them without seeing the schematic.
- ERC and DRC through kicad-cli, clean, with 0 unconnected, and a check for each number the specs state.
- By calculation with inputs written down: driver temperature with all four axes at 1.5 A in still air, input spike and bulk capacitance, supply current budget.
- Inspect rendered views of copper and silkscreen yourself, cropped and zoomed, before calling the layout done.
- Blind review as the order gate describes: a fresh subagent with only a functional brief, the design files and the datasheets. Fix or accept each KRITIEK and BELANGRIJK finding, and review again after real changes.
- Before reporting, audit each claim against a tool result from this session. Say what was only calculated and what is not verified.
- Keep what must survive a long run in hardware/BUILD_NOTES.md, one lesson per entry.

# Report
The PR follows CLAUDE.md, with a `## Tracking` section and the sorted manufacturability and sourcing flags. Your final message is in Dutch, for a reader who saw none of the work, in plain full sentences. Start with whether the board is ready for me to order. Then give the size and layer count, what is not verified, which rig results could still change the board and what that would cost, the three design choices that shaped the board most and why, and exactly what I must do next.
```

## What was left out on purpose

- No step list. The guide warns that older, prescriptive scaffolding degrades output on this model.
- No request to show its reasoning, which can trigger a `reasoning_extraction` refusal. The report asks for the three main choices instead.
- No token budget and no hard style limits, for the same guide's reasons.
- Nothing already in `CLAUDE.md` is repeated, such as silkscreen, routing order or the datasheet rule.
