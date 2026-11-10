# PTZ driver board — PRD

Status: **The hardware sections (POW, DRV, ENC, CTL, CAM, AUX, BRD) are approved for Rev A by the owner (2026-11-10). The firmware and mechanics sections are still a draft.** Lines marked
**[OPEN]** wait for an owner decision; the rest are proposals to strike or change. Ids are stable so the
owner can comment per line. They become full acceptance criteria in `specs/modules/` per slice.

**Part names are candidates until the research phase closes** (`docs/research/README.md`), but the leading candidates are the design basis for Rev A. What the board must do is
the requirement; which chip does it is not.

## Core value

One board, as small as possible, with its own firmware, that can drive any PTZ head the owner builds: the same print
whatever the mechanics, motors or control source turn out to be. Built for one head, the owner's own.

**Success test (CORE-01).** A new head with different mechanics needs a configuration change only: no new
board, no new firmware build, no soldered wires.

## Targets (approved by the owner, 2026-11-04)

Numbers and reasoning in `docs/research/README.md`, R-01. First camera: Panasonic G7 with a 14-140 mm (Micro Four Thirds).

- TGT-01 Payload 2.5 kg including plate: a camera up to 2 kg.
- TGT-02 Slowest clean pan and tilt 0.08°/s.
- TGT-03 Fastest quiet pan and tilt 60°/s.
- TGT-04 No louder than NC35 up to 60°/s; slow moves inaudible at 2 m in a quiet room, judged by the owner. Used in theatres among the audience.
- TGT-05 A preset lands within about 0.005°, from the same side each time.

## Hardware: on the board

### Power (POW)
- POW-01 Single DC input of 12 to 24 V through a locking connector. Which of the two the head runs on follows from the rig (R-07).
- POW-02 Survives reverse polarity, a hot-plug spike and a short on any output connector. The previous board
  burned out on a 12 V/MOSFET problem, so this is checked by calculation and in the bring-up run.
- POW-03 Motor supply and logic supply are fused separately.
- POW-04 Margin to the driver's absolute maximum is calculated, not assumed: spike clamp, bulk capacitance and
  back-EMF. Voltage per R-07.
- POW-05 USB alone powers logic for flashing and setup, never the motors, and cannot backfeed the host.
- POW-06 Firmware reads input voltage and refuses to enable motors outside the allowed range.

### Motor drive (DRV)
- DRV-01 **Four** motor axes with drivers on the board: pan, tilt, zoom, focus (owner, 2026-11-04). Motor technology per R-02.
- DRV-02 Driver per R-03. Candidates: TMC5240 (leading), TMC2240, TMC2209. Current, microsteps and chopper mode are set from firmware.
- DRV-03 Current per axis is set in firmware and survives a reboot; no trimmers.
- DRV-04 Stall and fault per axis reach the MCU (DIAG), so sensorless homing is possible.
- DRV-05 Thermal: at the specified current, with stated assumptions about the enclosure, the calculated driver
  temperature leaves margin. Copper and vias under each driver are sized for that.
- DRV-06 Each axis also has an **external driver port** (STEP, DIR, GND at the least), so a closed-loop driver or a
  larger stage can replace the on-board driver without new hardware. The TMC5240 can output STEP and DIR itself (datasheet p60).

### Position sensing (ENC)
- ENC-01 One absolute sensor port per axis. Sensor and bus per R-05. Candidates: an SPI sensor (leading), or I2C through a mux.
- ENC-02 Port pinout is identical on all axes and suits a small remote sensor board.
- ENC-03 One home/limit input per axis, protected, for heads without an absolute sensor on that axis.
- ENC-04 Sensor cable integrity is proven for the longest run in the mechanics, by a bench test before the board
  is ordered (R-T2). A tilt sensor through a hollow pan shaft runs far beyond the 15 cm of the April brief, next
  to motor wires.

### Control (CTL)
- CTL-01 MCU: ESP32-C6-MINI-1**U**-H4, with an external antenna (owner, 2026-11-10). JLC Economic cannot place ESP32-S3 modules. A PCB antenna inside a housing of
  carbon-filled filament with motors around it is a risk to measure (see MEC-05).
- CTL-02 WiFi and ESP-NOW from the module.
- CTL-03 Wired Ethernet (W5500) with an RJ45 jack, assembled, for fixed installs (owner, 2026-11-10). If BRD-04 runs out of room, the jack becomes a header for an off-board jack first, and the CAN connector goes next.
- CTL-04 RS-485 port, for DMX, Pelco-D and control from a console.
- CTL-06 CAN port, for a remote axis node or expansion.
- CTL-07 USB-C for flashing and logs, reachable with the head closed.

### Camera (CAM)
- CAM-01 Struck: the owner's camera has no LANC, and a zoom motor is needed anyway (2026-11-04).
- CAM-02 Two open-drain outputs on one small connector, for tally and record trigger (owner, 2026-11-10).

### Other I/O (AUX)
- AUX-01 Spare I2C port for a display or sensor.
- AUX-02 Status RGB LED, dark during a show, and a user button.
- AUX-03 One optional switched output with PWM, for a fan (owner, 2026-11-04). Off by default; the head must meet its targets without it.
- AUX-04 Board temperature read by firmware.
- AUX-05 Test points on every rail and bus.

### Physical (BRD)
- BRD-01 Rev A's outline and mounting follow the working envelope in `docs/prompts/fable-board-rev-a.md`. The new 3D head is then designed around the board (R-06).
- BRD-02 All SMD on top, assembled by JLC with Economic PCBA, so no part may be Standard Only; connectors at the board edges.
- BRD-03 Layers follow from the thermal and routing need of DRV-05. Proposal: 4 layers.
- BRD-04 **At most 85×65 mm** (owner, 2026-11-10), smaller only when heat, routing and probing do not suffer. When a feature and size conflict, CTL-03 sets what goes first and the choice is reported to the owner.

## Firmware (FW)

A new code base. The old firmware in `PTZ-head` is reference only.

- FW-01 Stack, decided in the first firmware spec. C++ in any case. If R-03 keeps step pulses on the MCU: FastAccelStepper, which drives
  at least 4 axes with hardware-generated steps on ESP32-S3. With a motion-controller driver it is not needed.
- FW-02 Motion core: velocity and position moves with acceleration limits per axis, coordinated preset moves that
  arrive together, and soft limits. Pure logic, tested on the host.
- FW-03 Absolute position at boot when the encoder sits on the output axis; homing via hall or stall otherwise.
  Which applies is configuration per axis.
- FW-04 Presets: store and recall named positions, kept across power loss.
- FW-05 Control sources run side by side behind one command interface: OSC first. VISCA-over-IP (the only VISCA, no
  serial port), ESP-NOW, DMX and Pelco-D follow. **[OPEN: order]**
- FW-06 Feedback: position, state and faults to whoever controls the head.
- FW-07 Safety: a watchdog stops motion on lost control, a failed sensor read, a driver fault or bad input voltage.
- FW-08 Every per-head value (ratios, directions, currents, limits, sensor type) is configuration, set without a rebuild.
- FW-09 OTA updates over the network, so the head need not be opened.
- FW-10 A web page for setup and calibration. **[OPEN: v1 or later]**
- FW-11 A preset always lands from the same side, to take out backlash and hysteresis (R-08).

## What the 3D design must provide (MEC)

These flow from the software and electronics into the mechanics, and are the input the design is waiting for.

- MEC-01 Board space in the base: outline, height, mounting points and where connectors exit. The 3D head does not exist yet, so Claude helps design both.
- MEC-02 Absolute at boot only works with a **magnet on the output axis** that turns less than once over the whole
  range. On a motor shaft behind a reduction, the position is gone after a restart.
- MEC-03 A magnet must sit on the axis centre, with no steel within about 5 mm. A hollow pan shaft has its centre taken
  by cables, so pan needs a 1:1 belt to a separate sensor shaft, or a different sensor type.
- MEC-04 **Wire count through the shafts.** With absolute sensors on a shared SPI bus and no home switches: motors 12 + sensors 8 =
  20 wires for tilt, zoom and focus (R-05). The bore is sized for that, or a remote node sits above pan (IDEA-02).
- MEC-05 A place for the external antenna outside the carbon-filled walls.
- MEC-06 Heat: designed to work without a fan, with room to add one (AUX-03). The board stays off the plastic; a printed part softens long before the chips reach their limit (R-03).
- MEC-07 Pan range is limited, with a cable service loop (owner, 2026-11-04). No slip ring.
- MEC-08 The base is at most Ø165 mm (owner, 2026-11-04). One belt stage per axis, no double belt (owner, 2026-11-04).

## Out of scope for v1

- Closed-loop control in our own firmware. External closed-loop drivers can connect through DRV-06.
- Motor drive above 2 A RMS per axis on the board. Larger motors use DRV-06.
- Selling: CE marking, a release process and series production. One head, for the owner (2026-11-04).

## Part check (JLC, 2026-11-04)

Stock and first-tier price from the JLC parts search, checked once. To be rechecked at order time. Alternatives are in `docs/research/README.md`.

| Part | LCSC | Stock | Price |
| --- | --- | --- | --- |
| TMC2209-LA-T | C2150710 | 22,495 | $2.83 |
| ESP32-S3-WROOM-1U-N16R8 | C3013946 | 33,286 | $5.19 |
| TCA9548APWR | C130026 | 22,826 | $0.82 |
| TCA9555PWR (I/O expander) | C465732 | 28,985 | $0.71 |
| W5500 | C32843 | 12,692 | $2.84 |
| TJA1051T/3 (CAN) | C38695 | 154,640 | $0.58 |
| SP3485EN (RS-485) | C8963 | 360,578 | $0.26 |
| TPS54360 (buck, up to 60 V) | C44377 | 51,291 | $0.72 |
| AS5600-ASOM (for a remote sensor board) | C79815 | 401 | $1.71 |
