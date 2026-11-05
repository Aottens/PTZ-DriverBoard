# PTZ driver board — Ideas inbox

The owner drops ideas in chat. Claude records each one here, proposes a phase and module, and guards the scope. An idea
gets no criteria until its phase is planned.

How an idea moves: **new** → **triaged** → **specced** → **backlog** → **done** or **rejected** (with the reason). Every
`### IDEA-nn` section has a row in the table and the other way round (`scripts/check-tracking.py`).

## Ideas

| Id | Idea | Status | Phase | Module |
| --- | --- | --- | --- | --- |
| IDEA-01 | Field control box with joystick over ESP-NOW | triaged | after v1 | firmware |
| IDEA-02 | Remote axis node above pan | new | decide in R-06 | hardware |
| IDEA-03 | Power over Ethernet | new | after v1 | hardware |
| IDEA-04 | Capstan drive instead of a belt | new | if the rig shows a visible wave | mechanics |

### IDEA-01 — Field control box with joystick over ESP-NOW
From the June work in `PTZ-head` (`controlbox_main.cpp`, `ptz_link_packet.h`), which measured the raw link. The board
needs no extra hardware for it: the radio is on the module. It comes in as one more control source (FW-05).

### IDEA-02 — Remote axis node above pan
A small second board in the yoke with the tilt, zoom and focus drivers, fed by power and CAN through the pan shaft. Solves
the wire count (MEC-04) and moves heat out of the base, at the cost of a second design. CTL-06 keeps this door open. A slip
ring is off the table (MEC-07), so it is no longer needed for that.

### IDEA-03 — Power over Ethernet
No wall adapter in fixed installs. Open question: can it deliver enough for the motors, given what the power calculation
in slice 1 shows?

### IDEA-04 — Capstan drive instead of a belt
A thin cable around a small shaft and a large drum: about 18:1 in one stage on a Ø100 mm drum, fitting the base of Ø165 mm, with no teeth to hear and almost no backlash. A limited pan range suits it. Open questions, none researched yet: cable wear and stretch, how to mount and tension it, and whether it stays quiet.
