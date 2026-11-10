# Functional brief for the blind review of the PTZ driver board, Rev A

This is everything the reviewer gets besides the design files and the datasheets. It says what the board must do,
not how or why it was designed the way it is. Do not read `specs/`, `DECISIONS.md`, `hardware/BUILD_NOTES.md`,
`hardware/tools/`, `hardware/calc/`, `hardware/check_*.py`, `docs/` or git history: they hold our reasoning.

## What the board is

A driver board for one pan-tilt-zoom camera head, built once, for the owner's own use in theatres. A prototype:
it is ordered from JLCPCB with Economic PCBA (parts on the top side only, standard 4-layer 1.6 mm stack-up, HASL,
smallest package 0402, smallest IC pitch 0.4 mm). An order costs money and weeks and cannot be undone.

## What it must do

- **Supply:** one DC input of 12 to 24 V on a locking connector. Survive reverse polarity, a hot-plug, and a short
  on any output connector. Motor supply and logic supply fused separately. The stepper driver's absolute maximum is
  41 V; the margin to it must be real. USB alone powers the logic for flashing and setup, never the motors, and
  cannot feed back into the host. Firmware can read the input voltage.
- **Motors:** four stepper axes, each with a TMC5240 on the board, up to 1.5 A RMS per phase; current, microsteps and
  chopper mode set from firmware over SPI; no trimmers. Stall and fault of each axis reach the MCU. Anything that
  stops a motor is on a direct MCU pin. Each axis also has a port for an external step/direction driver.
- **Position sensing:** per axis a port for a remote absolute sensor on SPI at 3.3 V, on a cable that may be long and
  runs beside motor wires, and one protected home or limit input. The sensor cable must not load the SPI bus that
  the drivers and Ethernet share.
- **Control:** ESP32-C6-MINI-1U-H4 with an external antenna (22 GPIOs, one user SPI bus; strapping pins GPIO4, 5, 8,
  9, 15). WiFi from the module. Wired Ethernet with a W5500: the RJ45 jack with magnetics is off the board, on a
  header. RS-485 for DMX and Pelco-D. CAN. USB-C for flashing and logs.
- **Camera:** two open-drain outputs on one connector, for tally and record trigger.
- **Other:** a spare I2C port, a status RGB LED that can be dark, a user button, one switched PWM output for a fan,
  board temperature readable by firmware, a test point on every rail and bus.
- **Physical:** at most 85 x 65 mm, four M3 holes. It lies flat in a round base of 160 mm inner diameter beside a
  42 x 42 mm motor: one long edge (the one without connectors) 1 mm from the motor, the other three edges at least
  28 mm from the wall, parts and mating plugs within 25 mm above the board. Cables arrive from above the middle of
  the board. USB-C and the antenna connector must be reachable from outside.

## What to review

The design files in `hardware/`: `ptz-driver.kicad_sch` with its sheets, `ptz-driver.kicad_pcb`, `ptz.kicad_sym`,
`ptz.pretty/`, `fab/` (Gerbers, `jlc/` BOM and CPL), and `firmware/include/pins.h` (pin assignments).
Datasheets: `hardware/datasheets/README.md` lists sources; fetch what you need.

Find what would make the board fail, be damaged, be unbuildable at JLC, or be unusable in the head. Check every
active part's pins against its datasheet, pin by pin, from the netlist (`kicad-cli sch export netlist`), not from
symbol names. Check the layout: ERC, DRC with schematic parity, current paths, decoupling at the pins, the
antenna, clearances, the Gerbers against the board, the CPL rotations against the footprints, pin 1 marks.

## What to deliver

`hardware/review/BLIND_REVIEW.md`, in Dutch, with a one-paragraph verdict first (order, order after fixes, or do
not order), then findings grouped KRITIEK, BELANGRIJK and KLEIN. Each finding: what, the evidence (file, pin,
datasheet page, number), the consequence, and a fix. Tag each `[zeker]` (checked against a datasheet, a file or a
calculation you show) or `[vermoeden]` (plausible, not verifiable with what you have). End with what you checked
and found in order, and what you could not check. Change nothing in the design; work in a temporary folder.
