# Functional brief for the blind review of the PTZ driver board, Rev B

This is everything the reviewer gets besides the design files and the datasheets. It says what the board must do,
not how or why it was designed the way it is. Do not read `specs/`, `DECISIONS.md`, `STATE.md`, `BACKLOG.md`,
`docs/`, `hardware/README.md`, `hardware/BUILD_NOTES.md`, `hardware/ASSEMBLY.md`, `hardware/tools/`,
`hardware/calc/`, `hardware/check_*.py`, `hardware/sourcing/`, `tests/`, other files in `hardware/review/` or git
history: they hold our reasoning.

## What the board is

A carrier board for one pan-tilt-zoom camera head, built once, for the owner's own use in theatres, as a hobby
project. It must be cheap: one order of five boards at JLCPCB, assembled with Economic PCBA (SMD parts on the top
side only, two layers, 1.6 mm, HASL), may cost at most €100 with shipping and tax. So the expensive parts are
modules the owner buys and plugs in or solders in himself, and every through-hole part is soldered by the owner
and is not in the JLC order. An order costs money and weeks and cannot be undone.

## What it must do

- **Supply:** one DC input of 11 to 17 V on a locking connector: a 12 V supply, or a D-Tap lead from a V-mount
  battery (16.8 V when full). Survive reverse polarity, a hot-plug, and a short on any output connector. Motor
  supply and logic supply fused separately. The margin to the stepper drivers' limits must be real at 17 V
  (TMC2240: 36 V operating, 41 V absolute maximum; TMC2209: 29 V operating, 32 V absolute maximum). USB on the MCU
  module alone powers the logic for flashing and setup, never the motors, and cannot feed back into the host.
  Firmware can read the motor supply voltage.
- **Motors:** four stepper axes, each a socket for a driver module in StepStick format. Default module: a
  BIGTREETECH TMC2240 V1.0, on SPI. The sockets also take TMC2209 modules (UART), chosen by solder jumpers. The MCU
  makes the step pulses. Current, microsteps and chopper mode are set from firmware; no trimmers. Stall and fault
  reach the MCU; one shared line is allowed when firmware can ask each driver. The drivers are off while the MCU
  is in reset.
- **Position sensing:** four identical I2C sensor ports (supply, ground, SDA, SCL), each on its own channel of a
  TCA9548A, for AS5600 or MT6701 breakout boards on cables that may be long and run beside motor wires. Pull-ups
  per port can be changed by solder jumper. One protected home or limit input per axis. A spare multiplexer
  channel on a header. ESD protection on the cabled ports.
- **Control:** an ESP32-S3-DevKitC-1U on headers (the N8 variant is preferred; the N16R8 is the one on sale), with
  its U.FL antenna connector, and its USB reachable at a board edge. Wired Ethernet from a W5500 module with its
  own RJ45 jack (WIZnet WIZ850io or a compatible one), on SPI.
- **Other:** one switched PWM output for a fan, off by default; board temperature readable by firmware; a status
  LED is the MCU module's own; a test point on every rail and bus.
- **Physical:** at most 100 x 80 mm, four M3 holes. It lies flat in a round base of 160 mm inner diameter beside
  a 42 x 42 mm motor: the south edge 1 mm from the motor, the other three edges at least 10 mm from the wall,
  everything including modules, heat sinks and mating plugs within 25 mm above the board. Cables arrive from above
  the middle of the board.

## What to review

The design files in `hardware/`: `ptz-driver.kicad_sch` with its sheets, `ptz-driver.kicad_pcb`, `ptz.kicad_sym`,
`ptz.pretty/`, `fab/` (Gerbers, `jlc/` BOM and CPL), and `firmware/include/pins.h` (pin assignments).
Datasheets and module drawings: `hardware/datasheets/README.md` lists the sources; copies of most are in that
folder; fetch what is missing.

Find what would make the board fail, be damaged, be unbuildable at JLC, cost more than it should, or be unusable
in the head. Check every part's pins against its datasheet, and every module socket against the module's own
drawing and pin table, pin by pin, from the netlist (`kicad-cli sch export netlist`), not from symbol names. Check
the ESP32-S3's pin use against Espressif's documents (strapping pins, pins taken by flash or PSRAM, USB, the
board's own LED). Check the layout: ERC, DRC with schematic parity, current paths and their widths, the ground
return on a two-layer board, decoupling, clearances, the Gerbers against the board, the CPL rotations against the
footprints, pin 1 and polarity marks, and whether a person can solder and plug everything in the order needed.

## What to deliver

`hardware/review/BLIND_REVIEW.md`, in Dutch, with a one-paragraph verdict first (order, order after fixes, or do
not order), then findings grouped KRITIEK, BELANGRIJK and KLEIN. Each finding: what, the evidence (file, pin,
datasheet page, number), the consequence, and a fix. Tag each `[zeker]` (checked against a datasheet, a file or a
calculation you show) or `[vermoeden]` (plausible, not verifiable with what you have). End with what you checked
and found in order, and what you could not check. Change nothing in the design; write only that one file, and
work in a temporary folder for anything else.
