# PTZ driver board — PRD

Status: **DRAFT, not approved by the owner.** Nothing here is a commitment until gate 1. Lines marked
**[OPEN]** wait for an owner decision; the rest are proposals to strike or change. Ids are stable so the
owner can comment per line. They become full acceptance criteria in `specs/modules/` per slice.

## Core value

One board, with its own firmware, that can drive any PTZ head the owner builds: the same print whatever the
mechanics, motors or control source turn out to be.

**Success test (CORE-01).** A new head with different mechanics needs a configuration change only: no new
board, no new firmware build, no soldered wires.

## Hardware: on the board

### Power (POW)
- POW-01 Single DC input, 12 to 24 V nominal, through a locking connector.
- POW-02 Survives reverse polarity, a hot-plug spike and a short on any output connector. The previous board
  burned out on a 12 V/MOSFET problem, so this is checked by calculation and in the bring-up run.
- POW-03 Motor supply and logic supply are fused separately.
- POW-04 Margin: TMC2209 has an absolute maximum of 29 V, so at 24 V the spike clamp, the bulk capacitance
  and back-EMF are calculated, not assumed.
- POW-05 USB alone powers logic for flashing and setup, never the motors, and cannot backfeed the host.
- POW-06 Firmware reads input voltage and refuses to enable motors outside the allowed range.

### Motor drive (DRV)
- DRV-01 **Four** stepper axes with drivers on the board: pan, tilt, zoom, focus. **[OPEN: 4 or 3]**
- DRV-02 Driver: TMC2209, set up over UART (current, microsteps, StealthChop, SpreadCycle), one shared bus
  with four hardware addresses.
- DRV-03 Current per axis is set in firmware and survives a reboot; no trimmers.
- DRV-04 Stall and fault per axis reach the MCU (DIAG), so sensorless homing is possible.
- DRV-05 Thermal: at the specified current, with stated assumptions about the enclosure, the calculated driver
  temperature leaves margin. Copper and vias under each driver are sized for that.
- DRV-06 Each axis also has an **external driver port** (STEP, DIR, EN, UART, GND), so a closed-loop driver or a
  larger stage can replace the on-board driver without new hardware.

### Position sensing (ENC)
- ENC-01 One encoder port per axis, 3V3 I2C through a TCA9548A mux, so sensors with a fixed address work (AS5600
  and alike).
- ENC-02 Port pinout is identical on all axes and suits a small remote sensor board.
- ENC-03 One home/limit input per axis, 3V3 or 5 V sensor, protected, with a pull-up selected by solder jumper.
- ENC-04 Encoder cable integrity is proven for the longest run in the mechanics, by a bench test before the board
  is ordered (S1-05). A tilt encoder through a hollow pan shaft runs far beyond the 15 cm of the April brief, next
  to motor wires.

### Control (CTL)
- CTL-01 MCU: ESP32-S3-WROOM-1**U**-N16R8, with an external antenna. A PCB antenna inside a housing of carbon-filled
  filament with motors around it is a known risk (see MEC-05).
- CTL-02 WiFi and ESP-NOW from the module.
- CTL-03 Wired Ethernet (W5500), for fixed installs. **[OPEN: assembled, footprint only, or none]**
- CTL-04 RS-485 port, for DMX, Pelco-D and control from a console. **[OPEN]**
- CTL-05 RS-232 or RS-422 port, for classic VISCA. **[OPEN]**
- CTL-06 CAN port, for a remote axis node or expansion. **[OPEN]**
- CTL-07 USB-C for flashing and logs, reachable with the head closed.

### Camera (CAM)
- CAM-01 LANC port, for zoom and record on Sony and Canon cameras without a zoom motor. **[OPEN]**
- CAM-02 Tally output and record trigger. **[OPEN]**

### Other I/O (AUX)
- AUX-01 Spare I2C port for a display or sensor.
- AUX-02 Status RGB LED and a user button.
- AUX-03 One 12/24 V switched output with PWM, for a fan. **[OPEN]**
- AUX-04 Board temperature read by firmware.
- AUX-05 Test points on every rail and bus.

### Physical (BRD)
- BRD-01 Outline and mounting from the 3D design. **[OPEN: dimensions come from MEC-01]**
- BRD-02 All SMD on top, assembled by JLC; connectors at the board edges.
- BRD-03 Layers follow from the thermal and routing need of DRV-05. Proposal: 4 layers.

## Firmware (FW)

A new code base. The old firmware in `PTZ-head` is reference only.

- FW-01 Stack. Proposal: C++ with FastAccelStepper, which on ESP32-S3 drives at least 4 axes with hardware-generated
  steps. Arduino core 3.x or ESP-IDF is decided in the first firmware spec.
- FW-02 Motion core: velocity and position moves with acceleration limits per axis, coordinated preset moves that
  arrive together, and soft limits. Pure logic, tested on the host.
- FW-03 Absolute position at boot when the encoder sits on the output axis; homing via hall or stall otherwise.
  Which applies is configuration per axis.
- FW-04 Presets: store and recall named positions, kept across power loss.
- FW-05 Control sources run side by side behind one command interface: OSC first. VISCA-over-IP, ESP-NOW, DMX and
  Pelco-D follow as their ports arrive. **[OPEN: order]**
- FW-06 Feedback: position, state and faults to whoever controls the head.
- FW-07 Safety: a watchdog stops motion on lost control, a failed sensor read, a driver fault or bad input voltage.
- FW-08 Every per-head value (ratios, directions, currents, limits, sensor type) is configuration, set without a rebuild.
- FW-09 OTA updates over the network, so the head need not be opened.
- FW-10 A web page for setup and calibration. **[OPEN: v1 or later]**

## What the 3D design must provide (MEC)

These flow from the software and electronics into the mechanics, and are the input the design is waiting for.

- MEC-01 Board space in the base: outline, height, mounting points, and where connectors may exit.
- MEC-02 Absolute at boot only works with a **magnet on the output axis** that turns less than once over the whole
  range. On a motor shaft behind a reduction, the position is gone after a restart.
- MEC-03 A magnet must sit on the axis centre, with no steel within about 5 mm. A hollow pan shaft has its centre taken
  by cables, so pan needs a 1:1 belt to a separate sensor shaft, or a different sensor type.
- MEC-04 **Wire count through the shafts.** Per axis above pan: motor 4, encoder 4, home 3. Tilt, zoom and focus together
  come to 33 wires, against a bundle of 7 in the July design. Either the bore grows or a remote node sits above pan (IDEA-02).
- MEC-05 A place for the external antenna outside the carbon-filled walls.
- MEC-06 Heat: four drivers and their path out of a closed base (vent, fan, or a metal plate).
- MEC-07 Pan range: limited with a service loop, or continuous with a slip ring. **[OPEN]** A slip ring rules out long I2C.

## Out of scope for v1

- Closed-loop control in our own firmware. External closed-loop drivers can connect through DRV-06.
- Motor drive above 2 A RMS per axis on the board. Larger motors use DRV-06.
- Selling: CE marking and a release process. **[OPEN: is this one head or a product?]**

## Part check (JLC, 2026-11-04)

Stock and first-tier price from the JLC parts search, checked once. To be rechecked at order time.

| Part | LCSC | Stock | Price |
| --- | --- | --- | --- |
| TMC2209-LA-T | C2150710 | 22,495 | $2.83 |
| ESP32-S3-WROOM-1U-N16R8 | C3013946 | 33,286 | $5.19 |
| TCA9548APWR | C130026 | 22,826 | $0.82 |
| TCA9555PWR (I/O expander) | C465732 | 28,985 | $0.71 |
| W5500 | C32843 | 12,692 | $2.84 |
| TJA1051T/3 (CAN) | C38695 | 154,640 | $0.58 |
| SP3485EN (RS-485) | C8963 | 360,578 | $0.26 |
| SP3232EEN (RS-232) | C9378 | 142,434 | $0.36 |
| TPS54360 (buck, up to 60 V) | C44377 | 51,291 | $0.72 |
| AS5600-ASOM (for a remote sensor board) | C79815 | 401 | $1.71 |
