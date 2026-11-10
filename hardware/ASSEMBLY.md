# Putting the board in the base (BRD-08)

The head does not exist yet, so this is written against the working envelope in `specs/modules/board.md`, and the
3D design has to keep it true. `check_fit.py` checks the envelope by code; the steps below are what a hand and a tool
must be able to do. A bolt, tool or plug that cannot reach is a design error: change the base or the board, not the step.

## What the base must provide

- Four M3 stand-offs under the mounting holes, 4.0 mm from the board's corners, at least 5 mm tall and no wider than
  6 mm, so nothing on the board's underside is touched. The underside carries no parts, only solder joints of the
  through-hole connectors (up to 2 mm) under the top edge and the bottom-right corner.
- A flat on the wall, or a bracket, in line with the USB-C socket on the left short edge, with a slot for the plug:
  the socket's face is 36 mm from the wall by calculation, so a normal USB-C plug (about 25 to 30 mm of body) passes
  through the wall. Without the slot the board cannot be flashed in place.
- A hole for the antenna's bulkhead connector, anywhere within the pigtail's reach of the module (U201, bottom-left
  quarter of the board). The module's connector is a W.FL / MHF III type: an ordinary U.FL pigtail does not fit.
- The Ethernet jack is not on the board. Mount a jack with magnetics (for example an HR911105A on a small carrier)
  in the wall near the left edge, within 10 cm of lead from J801.
- **Ground the motor housings.** The motor outputs have no ESD capacitors (DRV-10), and a belt on a plastic housing
  builds up charge. Run a wire from each motor's housing to a `GND` point: pin 2 or the mounting tabs of any GH
  connector, or `TP906` / `TP907`.
- Optional, for more than about 1 A per axis continuously (`calc/thermal.py`): a flat aluminium bar of about
  60 x 10 mm under the driver row, pressed with a 0.5 to 1 mm thermal pad against the four bare copper windows on
  the underside (centres 13.6 mm apart, 11.5 mm below the top edge). The pad must be an insulating one: there are
  vias of other nets between the windows, under solder mask. Or a 5 V fan on J902.

## Order of work

1. **On the bench, before the board goes in:** solder nothing; JLC fits every part. Check jumpers: `T485` open,
   `TCAN` closed, fan supply on `5V`.
2. **Plug the top-entry connectors first, with the board still out of the base** or with the pulley plate off. These
   stand upright and are reached from above only: the four motors `M1` to `M4` along the top edge, the supply
   `12-24V` in the top-left corner, the four sensor ports `S1` to `S4` in the middle, `CAN` and `FAN` near the
   bottom edge. Their plugs with a cable bend stay under 24 mm; the limit is 25 mm.
3. Lower the board onto the stand-offs with its bottom long edge (the one without connectors) 1 mm from the pan motor.
4. **Four M3 x 6 screws from above,** one in each corner. A 2.5 mm hex key or a PH1 driver reaches each straight
   down: the nearest parts are the camera connector and the supply connector at the top-left hole (both lower than
   10 mm within 5 mm of the screw), `X1` at the top-right, `I2C` at the bottom-left and the fan connector at the
   bottom-right. Screw heads up to 6 mm fit the 7 mm bare circle.
5. **Side-entry plugs go in last, from the three free sides,** with at least 15 mm to the wall, and about 30 mm at the middle of each free edge: `CAM`, `ETH`, `USB`
   and `I2C` on the left edge, `X1` to `X4` and `RS485` on the right edge. Each needs about 13 mm of straight room
   for plug and bend.
6. Antenna pigtail onto the module, pressed straight down until it clicks.
7. Cables from the pan shaft come down above the middle of the board: tie them so they cannot rest on the two tall
   capacitors (10.5 mm) or pull sideways on the upright plugs.

## Taking it out

The reverse. The side-entry plugs come out first, by their housings, never by the wires. With the pulley plate on,
the upright plugs cannot be reached: the board comes out with those cables attached, or the plate comes off first.
The 3D design should leave the cables long enough for the board to be lifted 30 mm.
