# PTZ driver board — Decision Log

Append-only. Newest at top. Each entry: date, decision, alternatives, why, reversal trigger.

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
