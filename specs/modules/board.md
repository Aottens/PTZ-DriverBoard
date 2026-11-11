# Module spec: the board (BRD), Rev B

Status: **written in the Rev B one-run build (2026-11-11); gate 1 is the owner's approval of `docs/prompts/fable-board-rev-b.md`.**
Grows out of BRD-01..04 and COST-01..03 in `specs/PRD.md`. The numbers here are checked by `hardware/check_board.py`
and `hardware/check_fit.py`. Rev A's version of this file is under the git tag `rev-a`.

## The envelope, as modelled

From the owner's Rev A brief and the size entry of 2026-11-10 in `DECISIONS.md`. `hardware/check_fit.py` holds the same numbers.

- The base is a cylinder of 160 mm inner diameter, its axis the pan axis.
- The pan motor is a 42 × 42 mm square, centred 55.7 mm from the axis.
- The board lies flat next to the motor: its south edge parallel to the motor's face, 1 mm from it, and centred on
  it. That puts the pan axis above the board. North is the edge away from the motor; west is where the MCU
  module's USB sockets are.
- The free volume is 35 mm tall; parts, modules and mating plugs may use 25 mm above the board's top face.
- The west, north and east edges keep at least 10 mm to the wall.
- Rev B stands taller than Rev A: the modules sit on sockets. What lines the wall is still not known, and the head
  is designed together with the board (BRD-01 in the PRD), so openings for USB and Ethernet are the base's to give.

## Acceptance criteria

- **BRD-01** The outline is a rectangle of at most 100 × 80 mm with four M3 mounting holes: 3.2 mm, not plated,
  4.0 mm from both edges in each corner, with a 7.0 mm circle around each free of parts and copper.
- **BRD-02** Every SMD part is on the top side and is assembled by JLC. Every assembled part is "Economic and
  Standard" on its JLC part page, recorded with library type and stock in `hardware/sourcing/jlc_check.md`.
  Through-hole parts are on the top side too and are soldered by the owner: they carry no LCSC number and are not
  in the JLC files. No connector opens towards the south edge.
- **BRD-03** Two copper layers, 1.6 mm, 1 oz. The calculation that this is enough: the widest current path
  (BRD-06) fits on one layer, and the fastest signal is the SPI clock, at most 10 MHz on a bus the firmware can
  slow down. The bottom layer is a ground pour that tracks cross as shortly as routing allows; the top layer is
  poured with ground as well.
- **BRD-04** At most 100 × 80 mm, the size that fits the envelope (`DECISIONS.md`, 2026-11-10) and stays in JLC's
  cheapest size class of 100 × 100 mm.
- **BRD-05 Design rules,** wider than JLC's limits because nothing here needs fine lines: tracks 0.25 mm, necked
  to no less than 0.15 mm where they leave a fine-pitch pad; gaps at least 0.2 mm; vias at least 0.3 mm drill and
  0.6 mm pad; copper at least 0.3 mm from the board edge; smallest
  passive 0603; smallest IC pitch 0.65 mm.
- **BRD-06 Current paths,** by the IPC-2221 figures in `hardware/calc/power.py`:
  - `VIN_RAW`, `VIN` and `VM` from J101 through Q101 and F101 and along the row of driver sockets are tracks at
    least 3.0 mm wide (5 A with about 10 °C rise); the branch from there to each socket's pad 9 is at least
    2.0 mm wide, and the branch to F102 at least 1.0 mm;
  - motor outputs `Mn_1` to `Mn_4` are at least 1.0 mm wide (2 A RMS) and at most 15 mm long;
  - `VIN_L`, `+5V_REG`, `+5V`, `+3V3`, `+3V3_SNS`, `V_SNS`, `FAN_V` and `FAN_N` tracks are at least 0.5 mm wide,
    necked to no less than 0.35 mm where they enter a fine-pitch pad, for at most 3 mm per net;
  - each bulk capacitor's plus pad is within 12 mm of pad 9 of its driver socket.
- **BRD-07 Fit, checked by code** in `hardware/check_fit.py`, with each module, heat sink, connector, mating plug
  and cable bend as a box:
  - the board and every box stay inside the cylinder and clear of the motor;
  - nothing is higher than 25 mm above the board, with the driver and MCU modules on ordinary 8.5 mm sockets and
    the Ethernet module soldered in (on 8.5 mm sockets its jack would reach 26.3 mm);
  - the MCU module's USB sockets and the Ethernet jack face a free edge, and the distance from each to the wall
    is reported for the base's design;
  - the antenna connector on the MCU module is free above;
  - no two boxes overlap, and a screwdriver reaches each mounting screw from above.
- **BRD-08 Assembly** is written out in `hardware/ASSEMBLY.md`: what the owner solders and in which order, the
  order of mounting and plugging, and which tool reaches which bolt.
- **BRD-09 Silkscreen.** Top: a name at every connector, socket, fuse, jumper and test point; pin 1 at every
  connector and socket; plus, minus and the voltage range at the supply input; the fuse ratings; which way round
  each module goes; board name, revision and date. Bottom: the pin order of every connector and what each jumper
  does, because the top has no room for it. No text smaller than 0.8 mm high with a 0.15 mm stroke.
- **BRD-10** ERC is clean; DRC is clean with 0 unconnected items and schematic parity, both through `kicad-cli`.
- **BRD-11 Under the modules.** No part taller than 2.2 mm stands under a module, so a module may also be
  soldered in without sockets. No solder jumper and no test point is under a module or a connector.
- **BRD-12 Cost (COST-01..03).** At most three BOM lines are Extended parts with a loading fee, each with its
  reason in `docs/research/rev-b-cost.md`; every other assembled line is Basic or Preferred. The estimate for
  five assembled boards, with shipping and tax, is at most €100 (`hardware/calc/cost.py`).

## Not verified in this build

The real housing does not exist yet, so the fit is against the envelope above and nothing else. JLC's own preview
of rotation and pin 1 is a step only the owner can do, from the checklist in the pull request. The price is an
estimate until the owner has JLC's quote.
