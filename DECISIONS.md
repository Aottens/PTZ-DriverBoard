# PTZ driver board — Decision Log

Append-only. Newest at top. Each entry: date, decision, alternatives, why, reversal trigger.

---

## 2026-11-10 — Rev A: the board grows to 100 × 80 mm

**Decision (owner, in chat):** The board may be 100 × 80 mm instead of 85 × 65 mm. It lies in the base, not in the head, where the first size came from. The RJ45 jack and the supply inlet sit in the base wall. The four M3 holes stay 4 mm from the edges in each corner.

**Alternatives considered:** staying at 85 × 65 mm with a router that pushes tracks aside and a redesigned driver cell (tried: 39 to 62 connections stayed open in six routing runs); six layers on the old size; dropping CAN (about 2 % of the area, and not where the congestion was).

**Why:** On 85 × 65 mm the parts' courtyards filled 73 % of the board, top side only, with two signal layers. On 100 × 80 mm they fill 50 %. The calculation from the brief's envelope (base 160 mm inside, motor 42 × 42 mm at 55.7 mm, board 1 mm from the motor) leaves 19.7 mm from the corners beside the motor to the wall and 11.9 mm from the far corners; the middle of each free edge has about 30 mm.

**Reversal trigger:** something along the base wall (screw bosses, the bearing seat, the jacks in the wall) needs more than the room the corners leave; then the far corners are cut off at an angle before the board shrinks.

---

## 2026-11-10 — Rev A: the Ethernet jack is off the board

**Decision:** The W5500 and all of its circuit stay on the board, but the RJ45 jack does not: J801 is a 7-pin header for a short lead to a jack with magnetics in the housing wall. The CAN connector stays.

**Alternatives considered:** the HR911105A on the board, as the brief asked first; a transformer on the board with a 4-wire header behind it; dropping CAN as well.

**Reasoning:** counted by courtyard area, everything on 85 x 65 mm with parts on one side came to about 76 % of the area where parts can go, which leaves no room to route. The brief names the jack as the first thing to go (CTL-03). The header costs a tenth of the jack's area. A transformer on the board would have been the cleaner electrical cut, but its pin order could not be checked against a maker's sheet in this run.

**Reversal trigger:** a later revision gets a larger outline or parts on both sides; then the jack returns to the board.

---

## 2026-11-10 — Rev A: one chip select per driver and per sensor, no daisy chain

**Decision:** The four drivers and four sensor ports each have their own chip select from a dual 2-to-4 decoder (two address lines, two strobes). The drivers are not daisy-chained.

**Alternatives considered:** the TMC5240 daisy chain with one chip select, which `docs/research/README.md` called possibly the best part; a 4-to-16 decoder that also selects the W5500.

**Reasoning:** a chain makes every access four times as long and lets one dead driver take the other three off the bus, on a prototype whose job is to be measured. Four separate writes at 4 MHz start four axes within about 40 microseconds of each other, by calculation (4 x 40 bits), which a camera head cannot show. Two strobes keep the decoder free of glitches when the address changes. The W5500 keeps a plain chip select, because Espressif's driver expects one.

**Reversal trigger:** the rig shows that axes must start within microseconds; then the chain is a board change, not a firmware one.

---

## 2026-11-10 — Rev A: slow signals on an I/O expander, the stop on direct pins

**Decision:** The ESP32-C6's 22 pins carry the SPI bus, chip selects, I2C, RS-485, CAN, USB, the fan, the supply reading, the boot button, and the two signals that stop motors: `DRV_ENN` and the expander's interrupt. DIAG0 and DIAG1 of all axes, the Ethernet interrupt and reset, the status LED and the camera outputs are on a PCAL6416A. No pin is spare.

**Alternatives considered:** DIAG wired together on one direct pin, which fails when one axis uses DIAG0 as a step output; an expander without an interrupt mask, which would flood the MCU with interrupts in that case.

**Reasoning:** the driver stops its own motor on a stall or a home switch, in the chip. What the MCU needs fast is a way to cut power, and that is `DRV_ENN` on a direct pin, pulled up so the bridges are off at reset. The same pin gates the buffer of the external driver ports, so it stops those too.

**Reversal trigger:** firmware needs a DIAG edge faster than an I2C read, about 0.1 ms.

---

## 2026-11-10 — Rev A: sensor ports on their own buffered bus, 3.3 V only

**Decision:** Each sensor port gets its own buffered clock and data-out, switched on only while a sensor is selected, and its data-in passes a buffer that opens only for that port. The ports are 3.3 V only. The home input shares the 7-pin connector.

**Alternatives considered:** the sensor cable directly on the bus that the drivers and Ethernet share; a solder jumper for 5 V sensors.

**Reasoning:** the brief asks to keep the long cable from loading the shared bus. Buffers do that, and gating them keeps Ethernet's clock edges out of a cable that runs beside motor wires. A 5 V option would need 5 V signal levels as well: a 3.3 V clock does not reach a 5 V sensor's input-high level.

**Reversal trigger:** R-T2 chooses a sensor that needs 5 V or another bus.

---

## 2026-11-10 — Rev A: the board alone carries about 1 A per axis continuously

**Decision:** The board gets nine vias and a bare ground window on the bottom under each driver, the fan output and temperature readings. It is not claimed to carry 1.5 A on all four axes in still air.

**Alternatives considered:** a larger board; a dedicated heat-sink footprint; leaving it to the datasheet's 2.1 A figure.

**Reasoning:** `hardware/calc/thermal.py` puts four axes at 1.5 A at about 120 C board temperature in still air, past what a printed housing and the chip allow; about 1.0 A on four axes, or 1.35 A on two, is the limit. The earlier estimate in `docs/research/README.md` counted the drivers only, cold, on a board with nothing else on it. With a metal bar on the windows or moving air the same calculation allows 1.5 A and more. Nothing here is measured.

**Reversal trigger:** the bring-up run (step 4.4 and 4.8) shows the calculation is far off, either way.

---

## 2026-11-10 — Rev A: smaller choices made in layout

**Decision:**
- Motor connector pins are A1, A2, B2, B1: coil B mirrored, because that is the order the driver's pins leave the chip.
- Motor, sensor, CAN and fan connectors are top entry and may stand inside the board; side-entry connectors are on the three free edges.
- No reset button: the chip resets over USB. A test point on EN remains.
- No ESD capacitors on the motor outputs: they did not fit. The motor housings must be grounded instead.
- Fuses are soldered, not in holders.
- The two bulk capacitors are ordinary aluminium electrolytics on purpose: their resistance damps a hot-plug.

**Alternatives considered:** each of these the other way round; see `specs/modules/` and `hardware/BUILD_NOTES.md`.

**Reasoning:** space on 85 x 65 mm with parts on one side, and tracks that do not cross.

**Reversal trigger:** an ESD reset on the rig brings the output capacitors back first.

---

## 2026-11-10 — Rev A is designed in one run by Fable 5.2, before the rig results

**Decision:** One Fable 5.2 session takes Rev A from requirements to files ready to order, from `docs/prompts/fable-board-rev-a.md`, without waiting for the rig. It uses the leading candidates, at most 85×65 mm, JLC Economic PCBA, a W5500 with RJ45, and two open-drain camera outputs. Gate 1 for this build is the owner's approval of that prompt. The order gate is unchanged, and only the owner orders.

**Alternatives considered:** waiting for the rig results; building in several reviewed slices as `BACKLOG.md` planned.

**Reasoning:** the owner wants one board that can do everything and wants to test this model on a task of this size. A prototype costs little next to weeks of slices. It can also replace the breakout boards on the rig.

**Risk accepted:** the rig can still overturn the motor, driver, sensor or voltage choice, or show that the sensor cable needs another design (R-T1, R-T2). Then Rev A is partly thrown away. The board is checked by calculation and review only until the owner's bring-up run.

**Reversal trigger:** the blind review finds the approach unsound, or the rig shows a part choice fails before the order is placed.

---

## 2026-11-10 — The MCU for Rev A is the ESP32-C6-MINI-1U

**Decision:** Rev A uses the ESP32-C6-MINI-1U-H4 (LCSC C20627095), assembled by JLC with Economic PCBA. This replaces the ESP32-S3-MINI-1U as the design basis. The owner chose it.

**Alternatives considered:** an ESP32-S3-WROOM-1U soldered by hand on an otherwise JLC-assembled board, which has the most pins and two cores; a bare ESP32-S3FN8, which needs our own RF section, tuned with a network analyser, and 0201 parts that Economic cannot place; an RP2350B with a separate radio and second firmware; Standard PCBA, whose 70 mm minimum size excludes a 65 mm wide board without a panel.

**Reasoning:** one "Standard Only" part moves the whole order to Standard, and JLC lists the ESP32-S3 modules that way. The C6 module keeps the radio in a finished module. The TMC5240 generates the motion, so the MCU has less to do. The price is 22 GPIOs for about 27 signals, one user SPI bus and one core, so the board needs an I2C expander and a chip-select decoder and has almost no spare pins.

**Reversal trigger:** the pin plan does not close, one core cannot hold the control and sensor loop on the rig, or JLC changes a part's PCBA type.

---

## 2026-11-09 — Working rules for board design, from Anthropic's electronics work

**Decision:** Schematic and layout go to the strongest model available instead of Sonnet. Added to `CLAUDE.md`: route the hard nets first, a layout may overturn the pin table, check the board in its housing by code, sort every manufacturability and sourcing flag. The owner approved this.

**Alternatives considered:** keeping Sonnet for all building; waiting with these rules until the board starts.

**Reasoning:** [Anthropic's write-up with Diode Computers](https://www.anthropic.com/research/claude-electronics-design) reports a benchmark for placement and rerouting going from 25 % to 69 % between two model generations, and describes these habits. Diode has a commercial relationship with Anthropic, and the prototypes were not electrically validated, so this is a working habit and not proof.

**Reversal trigger:** a Sonnet layout holds up against the blind review, or the rules slow the work without catching defects.

---

## 2026-11-04 — The base is at most Ø165 mm

**Decision:** The head's base is at most Ø165 mm. The motor sits under the pulley, so the centres are at most 55.7 mm. The rig keeps to that and compares 6.25:1 without idlers against 7.5:1 with two idlers. This replaces the 9:1 and 12.5:1 rig in the entry below.

**Alternatives considered:** 12.5:1 with a 200T (Ø196 with idlers, about Ø300 without); 9:1 with a 144T, which reaches the limit with no margin.

**Reasoning:** the owner rejected the size of a 200T and a 400 mm belt, and small is a stated goal. Claude had let tooth grip set the layout. A rig with the head's real geometry also tests the right question.

**Reversal trigger:** the rig shows neither ratio is acceptable; then the capstan (IDEA-04) comes first, within the same base.

---

## 2026-11-04 — One belt stage, no double belt

**Decision:** The head uses one belt stage per axis. The rig compares 9:1 and 12.5:1, with 26 and 42 Ncm motors. This replaces the 30:1 two-stage layout and the 17 Ncm motor in the rig entry below.

**Alternatives considered:** 30:1 in two stages; a capstan drive (IDEA-04); gearboxes, worm gears and harmonic drives, set aside for backlash, noise or price.

**Reasoning:** the owner does not want a double belt. Claude's case for 30:1 counted absolute stepper error, while a preset landing from the same side mostly repeats it. The remaining risk is a slow wave at very low speed, which the rig measures.

**Reversal trigger:** the wave stays visible at 12.5:1 even with a tuned microstep table; then a capstan comes first, before a second belt.

---

## 2026-11-04 — The rig spec is approved

**Decision:** `specs/modules/rig.md` is approved (gate 1), with the 17HE08-1004S and 17HE12-1204S motors instead of the 0.4 A motor from the July design.

**Alternatives considered:** the 17HS13-0404S1, which needs 35 V at 300 rpm at rated current by calculation.

**Reasoning:** low-resistance motors reach the speed on 12 V and are thinner, which suits a small base.

**Reversal trigger:** R-T1 shows these motors are too weak or too loud.

---

## 2026-11-04 — Targets approved, G7 first, and the rig goes ahead

**Decision:** TGT-01..05 are approved. The first camera is a Panasonic G7 with a 14-140 mm, Micro Four Thirds. A one-axis test rig goes ahead.

**Alternatives considered:** designing the board first and measuring on it.

**Reasoning:** at 140 mm on this sensor a pixel is smaller than the 200 mm assumed so far, so exactness gets harder. The rig tests motor, reduction, voltage and cable before an order that costs weeks.

**Reversal trigger:** the rig shows the targets are out of reach within DIY means; then the targets go back to the owner.

---

## 2026-11-04 — The fan output stays, as an option

**Decision:** Keep a switched PWM output for a fan (AUX-03), off by default. This corrects "No fan" in the entry below: the head is still designed to meet its targets without one.

**Alternatives considered:** striking the output, to save a pin and some board space.

**Reasoning:** the owner wants the option. It costs one pin and a small switch, and it is a reserve if the heat calculation proves optimistic.

**Reversal trigger:** it turns out to be the part that keeps the board from getting smaller.

---

## 2026-11-04 — Theatre use sets the bar, and the old head is out

**Decision:** The head carries a DSLR or mirrorless up to 2 kg, in theatres among the audience, as exact as DIY allows. No LANC, since the camera has none. No fan. The old head is left out, so
the evidence comes from a new one-axis test rig. Targets TGT-01..05 are proposed, from a professional head, for the owner to approve.

**Alternatives considered:** measuring the old head as a baseline; keeping LANC for other cameras (the board is for one head and should be small).

**Reasoning:** the owner does not know the speeds yet, so a reference gives something to change. A rig answers noise, smoothness, reduction and cable questions on real hardware before any board is ordered.

**Reversal trigger:** another camera with LANC comes into use; then CAM-01 returns.

---

## 2026-11-04 — One head, small, a research phase first

**Decision:** The board is for one head, the owner's own, and as small as possible. Four axes. Limited pan with a cable loop, no
slip ring. RS-232 is dropped, so VISCA only runs over IP. ESP32-S3 and TMC2209 go back to being candidates, and a joint research phase
comes before the hardware is fixed. The new 3D head does not exist yet, and Claude helps design it.

**Alternatives considered:** fixing the proposed parts directly, as in the first PRD draft.

**Reasoning:** the owner named those parts as examples and wants to look for better solutions together. One head means CE and series cost
do not steer the choices, so a dearer driver can win if it makes the board smaller.

**Reversal trigger:** selling it after all; then this entry and the out-of-scope list get reopened.

---

## 2026-11-04 — A new hardware and software pair, as one driver board for all heads

**Decision:** Start over on both board and firmware, in this repo. The board carries its stepper drivers in SMD and is
meant to drive any PTZ head. The owner's words: a driver board for PTZ heads that can do everything.

**Alternatives considered:** upgrading the existing head with encoders (April brief); the custom board for one 3D head
with SERVO42C drives (July design).

**Reasoning:** the owner wants one print that does not depend on the mechanics, and has the freedom to redesign the 3D
head alongside it. With JLC assembly and the KiCad flow from the scoreboard, SMD drivers are within reach.

**Reversal trigger:** "everything" does not fit a board or budget; then ports drop, per the OPEN lines in the PRD.

---

## 2026-11-04 — Scoreboard flow for KiCad, CMDMX and Kikkuh harness for the work

**Decision:** Take the KiCad tooling and blind review from `RunningScoreboard`, and the spec → test → build → review
loop with its tracking from `ColourmotionDMX` and `Kikkuh`. Not the separate `Harnas` project, which neither uses.

**Alternatives considered:** EasyEDA, as in the April brief.

**Reasoning:** the owner's experience with this KiCad flow was good, and the check of a schematic against a spec fits
the same loop as a test against code.

**Reversal trigger:** the loop slows hardware work down without catching defects.
