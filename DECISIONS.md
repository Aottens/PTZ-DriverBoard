# PTZ driver board — Decision Log

Append-only. Newest at top. Each entry: date, decision, alternatives, why, reversal trigger.

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
