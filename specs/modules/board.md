# Module spec: the board (BRD)

Status: **written in the Rev A one-run build (2026-11-10); gate 1 is the owner's approval of `docs/prompts/fable-board-rev-a.md`.**
Grows out of BRD-01..04 in `specs/PRD.md`. The numbers here are checked by `hardware/check_board.py` and `hardware/check_fit.py`.

## The envelope, as modelled

From the owner's brief. `hardware/check_fit.py` holds the same numbers.

- The base is a cylinder of 160 mm inner diameter, its axis the pan axis.
- The pan motor is a 42 × 42 mm square, centred 55.7 mm from the axis.
- The board lies flat next to the motor: one long edge parallel to the motor's face, 1 mm from it, and centred on it. That puts the pan axis above the board.
- The free volume is 35 mm tall; parts and mating plugs may use 25 mm above the board's top face.
- The other three edges must keep at least 28 mm to the wall.

## Acceptance criteria

- **BRD-01** The outline is a rectangle of at most 85 × 65 mm with four M3 mounting holes: 3.2 mm, not plated, 4.0 mm from both edges in each corner, with a 7.0 mm circle around each free of parts and copper.
- **BRD-02** Every SMD part is on the top side. Every assembled part is "Economic and Standard" on its JLC part page, recorded with stock in `hardware/sourcing/jlc_check.md`. Through-hole connectors are on the top side too. No connector sits on the motor-side edge. Side-entry connectors are on the three free edges; top-entry connectors (motors, sensor ports, CAN, fan) may stand inside the board, since their cables come down from the pan shaft above it.
- **BRD-03** Four layers on JLC's standard 1.6 mm stack-up JLC04161H-7628, 1 oz outer and 0.5 oz inner copper: top = parts and signals, inner 1 = an unbroken `GND` plane, inner 2 = supply planes (`VM`, `+3V3`, `+5V`), bottom = signals and `GND`.
- **BRD-04** At most 85 × 65 mm. A feature that does not fit goes in the order CTL-03 gives, and is reported.
- **BRD-05 Design rules** inside JLC's Economic limits: tracks and gaps at least 0.15 mm; vias at least 0.3 mm drill and 0.6 mm pad; copper at least 0.3 mm from the board edge; smallest package 0402; smallest IC pitch 0.5 mm.
- **BRD-06 Current paths.** `VIN_RAW`, `VIN` and `VM` are planes or pours, and where they neck down the copper is at least 3.0 mm wide in total (7 A, the fuse rating, at about 10 K rise on 1 oz outer copper by IPC-2221). Motor outputs are at least 0.6 mm wide. `+5V`, `VSYS` and `+3V3` feeds are at least 0.4 mm or a plane.
- **BRD-07 Fit, checked by code** in `hardware/check_fit.py` with each connector and its mating plug and cable bend as a box:
  - the board and every box stay inside the cylinder and clear of the motor;
  - nothing is higher than 25 mm above the board;
  - the USB-C socket and the antenna connector have a free straight path: USB-C outward to the wall along its plug axis, the antenna connector upward and then sideways to the wall;
  - no two plugs' boxes overlap.
- **BRD-08 Assembly** is written out in `hardware/ASSEMBLY.md`: the order of mounting and plugging, and which tool reaches which bolt. A bolt, tool or plug that cannot reach is a design error.
- **BRD-09 Silkscreen:** board name, revision and date; at every connector its name, pin 1 and the voltage or signal names; polarity at every polarised part that is soldered or plugged by hand; a label at every solder jumper and test point.
- **BRD-10** ERC is clean; DRC is clean with 0 unconnected items and schematic parity, both through `kicad-cli`.
- **BRD-11** Each TMC5240's exposed pad has at least 9 vias to the ground planes, and the bottom layer has `GND` copper under it (DRV-05).

## Not verified in this build

The real housing does not exist yet, so the fit is against the envelope above and nothing else. JLC's own preview of rotation and pin 1 is a step only the owner can do, from the checklist in the pull request.
