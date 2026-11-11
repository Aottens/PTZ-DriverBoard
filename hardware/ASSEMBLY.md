# Building Rev B and putting it in the base (BRD-08)

The board comes from JLC with its SMD parts on. Everything through-hole is the owner's to buy and solder. The head
does not exist yet, so the last part of this file is written against the working envelope in
`specs/modules/board.md`, and the 3D design has to keep it true. `check_fit.py` checks the envelope by code. A bolt,
tool or plug that cannot reach is a design error: change the base or the board, not the step.

## What to buy, for one board

| For | Part | Count | Notes |
| --- | --- | --- | --- |
| A201 | ESP32-S3-DevKitC-1U | 1 | Any memory variant: the board uses no pin that the N16R8's memory takes. The "1U" has the antenna connector |
| A201 | Female header 1×22, 2.54 mm, 8.5 mm tall | 2 | Use sockets: a regulator and other parts up to 2.1 mm tall sit under the module, and it is the part most likely to be swapped |
| A301 … A601 | TMC2240 driver in StepStick format, with heat sink | 4 | Drawn for the BIGTREETECH TMC2240 V1.0. TMC2209 modules fit after cutting three jumpers each |
| A301 … A601 | Female header 1×8 (two per socket) and 1×2 (one per socket) | 8 + 4 | The 1×2 takes the module's AIN and DIAG pins beside its EN pin |
| A202 | WIZnet WIZ850io, or a module sold as compatible | 1 | Solder it in, or use sockets no taller than 5 mm: on 8.5 mm sockets its jack is 28 mm above the board |
| U101 | 5 V 1 A switching regulator, SIP-3, 7805 pin order | 1 | RECOM R-78K5.0-1.0, Traco TSR 1-2450 or Mornsun K7805-1000R3. Not a linear 7805: it would burn 4 W |
| F101, F102 | Radial fuse, 5.08 mm pitch (TR5), time-lag: 5 A and 1 A | 1 + 1 | With a holder each, or soldered in. Schurter MST 250 is rated for DC |
| C101 … C104 | Electrolytic capacitor 100 µF 35 V, 6.3 mm, 2.5 mm pitch | 4 | A general-purpose type, not low-ESR: its resistance damps the supply lead (`calc/power.py`) |
| J101 | JST B2P-VH header, with VHR-2N housing and contacts | 1 | Supply. Pin 1 is plus |
| J301 … J601 | JST B4B-XH-A header, with XHP-4 housings | 4 | Motors |
| J303 … J603 | JST B4B-PH-K-S header, with PHR-4 housings | 4 | Sensors |
| J302 … J602 | JST B3B-PH-K-S header, with PHR-3 housings | 4 | Home inputs; fit only the ones the head uses |
| J701, J801 | Pin header 1×4 and 1×2, 2.54 mm | 1 + 1 | Spare I2C port and fan; fit when used |
| antenna | U.FL to SMA bulkhead lead, 2.4 GHz antenna | 1 | The module's connector is first-generation U.FL (Espressif datasheet v1.8, 10.2) |
| sensors | MT6701 or AS5600 board | up to 4 | Which one is the rig's question (R-T2) |

Shop links are in the pull request and in `docs/research/rev-b-cost.md`.

## Soldering, in the order the bring-up checklist asks for it

`tests/hardware/bringup-rev-b.md` powers the board up between these steps; follow it.

1. **J101, F102, U101.** The regulator's pin 1 goes to the pad marked `IN`; its body lies over the outline towards
   the north. Then the checklist's section 1.
2. **C101 to C104 and F101.** The capacitor's long lead goes to the pad marked `+`. Section 2.
3. **The two 22-pin sockets of A201.** Put them on the module's pins first, stand the module on the board and
   solder: that keeps the rows straight. Section 3 and 4.
4. **The PH connectors and the `I2C` header.** Section 5.
5. **The WIZ850io,** its jack over the east edge above the `RJ45` mark, its pin 1 (square pad) at the north-east.
   Section 6.
6. **The four driver sockets and the XH connectors.** Solder the sockets on a module's pins too. Section 7.
7. **The fan header,** when a fan is used. Section 8.

Ground pins sit solid in the copper pour, without thermal spokes: give them a second longer with the iron.

**Which way round.** A driver module has `EN` and `VM` printed at its two top corners; the board prints the same
two names inside each socket outline. The MCU module's USB sockets go to the west edge, over the box marked `USB`.
The Ethernet module's jack points east. A driver module put in the other way round is destroyed at power-up.

## Jumpers, as delivered and what they do

| Jumper | Delivered | Change it when |
| --- | --- | --- |
| `SPI`, three per driver socket | closed | a TMC2209 module goes in that socket: cut all three |
| `PU`, two per sensor port and at the `I2C` header | the bridged one closed (4.7 kΩ), the other open (2.2 kΩ) | the sensor board has pull-ups of its own: cut the bridged one. A long cable needs stronger ones: close the open one |
| `VSNS` | on `3V3` | a sensor needs 5 V: cut the bridge, close the `5V` side. All ports and home plugs change together |
| `FAN V` | on `5V` | a fan for the supply voltage is used: cut the bridge, close the `VM` side. Then only F101 protects that output |

## What the base must provide

- Four M3 stand-offs under the mounting holes, 4.0 mm from the board's corners, at least 5 mm tall and no wider
  than 6 mm. The underside carries no parts, only solder joints up to 2 mm.
- 25 mm of height above the board's top face. The tallest things are the driver modules with a 12 mm heat sink on
  ordinary 8.5 mm sockets (24.6 mm, an assumption about the heat sink), and the supply plug with its cable bend
  (24.5 mm). A lower heat sink or lower sockets give room.
- **USB:** the MCU module's two USB-C sockets are at the middle of the west edge; the wall is 30 mm from them by
  calculation. That is about the length of a plug's body, so the wall needs a slot there, or the base carries a
  short USB-C panel extension.
- **Ethernet:** the jack's face is at the east edge; the wall is 29 mm from it. Either a hole in line with the
  jack, large enough for a plug and its boot to reach in, or a short patch lead to a coupler in the wall.
- **Antenna:** a hole for the SMA bulkhead anywhere within the lead's reach of the MCU module's east end.
- **Air:** the four driver modules stand in a row along the north edge with their heat sinks up; a fan on `FAN`
  should blow along that row. The pan motor's face is 1 mm from the south edge.
- **Ground the motor housings** to a `GND` test point or to pin 2 of the supply connector: a belt on a plastic
  housing builds up charge, and the motor outputs have no ESD parts of their own.

## Order of work in the base

1. With the board on the bench: all modules in, jumpers set, fuses in.
2. Plug the connectors that stand inside the board first, while it is still out of the base or the pulley plate
   is off: the four motors `M1` to `M4` along the north edge, the supply on the east side, the sensors `S1` to `S4`
   and home inputs `H1` to `H4` along the south edge, the fan and the spare port on the west side. All are top
   entry: they are reached from above only.
3. Lower the board onto the stand-offs with its south edge (sensor connectors) 1 mm from the pan motor.
4. **Four M3 × 6 screws from above,** one in each corner. A 2.5 mm hex key or a PH1 driver reaches each straight
   down (`check_fit.py`): the nearest tall parts are C101 and the spare port at the north-west, the TVS at the
   north-east, the Ethernet module at the south-east and the first home connector at the south-west.
5. The antenna lead onto the module, pressed straight down until it clicks. Network and USB cables from outside.
6. Cables from the pan shaft come down above the middle of the board, over the MCU module: tie them so they cannot
   rest on the driver heat sinks or pull sideways on the upright plugs.

## Taking it out

The reverse. With the pulley plate on, the upright plugs cannot be reached: the board comes out with those cables
attached, or the plate comes off first. The 3D design should leave the cables long enough to lift the board 30 mm.
