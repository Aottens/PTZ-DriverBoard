# PTZ driver board — PRD

Status: **The hardware and cost sections are approved for Rev B by the owner (2026-11-11, gate 1), including the lines marked *(proposal)*.** The firmware and mechanics sections are still a draft. Rev A was designed and not ordered: the JLC quote came to almost €400 for five boards (2026-11-11). Rev B moves drivers, MCU and Ethernet onto plug-in modules and keeps the board itself cheap. Lines marked **[OPEN]** wait for an owner decision. Ids are stable; struck ids stay, so old references still resolve.

**Part names are candidates** until the rig closes the research (`docs/research/README.md`). What the board must do is the requirement; which chip does it is not.

## Core value

One board, with its own firmware, that can drive any PTZ head the owner builds: the same print whatever the mechanics, motors or control source turn out to be. Built for one head, the owner's own, as a hobby project.

**Success test (CORE-01).** A new head with different mechanics needs a configuration change only: no new
board, no new firmware build, no soldered wires.

## Targets (approved by the owner, 2026-11-04)

Numbers and reasoning in `docs/research/README.md`, R-01. First camera: Panasonic G7 with a 14-140 mm (Micro Four Thirds).

- TGT-01 Payload 2.5 kg including plate: a camera up to 2 kg.
- TGT-02 Slowest clean pan and tilt 0.08°/s.
- TGT-03 Fastest quiet pan and tilt 60°/s.
- TGT-04 No louder than NC35 up to 60°/s; slow moves inaudible at 2 m in a quiet room, judged by the owner. Used in theatres among the audience.
- TGT-05 A preset lands within about 0.005°, from the same side each time.

## Cost (COST)

- COST-01 One JLC order of five assembled boards costs at most **€100**, shipping and tax included (owner, 2026-11-11). The plug-in modules for one head are bought separately and estimated apart.
- COST-02 A Basic part wherever one does the job. Every Extended part is listed with its reason, because each one adds a loading fee per order.
- COST-03 A cost estimate exists before the schematic (`docs/research/rev-b-cost.md`), and is redone before the order. A change that raises it by more than €5 goes to the owner first.

## Hardware: on the board

### Power (POW)
- POW-01 One DC input for **11 to 17 V**: a 12 V supply, or a D-Tap from a V-mount battery, which reads 16.8 V when full (owner, 2026-11-11). Through a locking connector.
- POW-02 Survives reverse polarity, a hot-plug spike and a short on any output connector. The previous board
  burned out on a 12 V/MOSFET problem, so this is checked by calculation and in the bring-up run.
- POW-03 Motor supply and logic supply are fused separately.
- POW-04 Margin to the drivers' absolute maximum is calculated, not assumed: spike clamp, bulk capacitance and back-EMF, at 17 V.
- POW-05 USB on the MCU board alone powers logic for flashing and setup, never the motors, and cannot backfeed the host.
- POW-06 Firmware reads input voltage and refuses to enable motors outside the allowed range.

### Motor drive (DRV)
- DRV-01 **Four** axes, pan, tilt, zoom and focus, each a socket for a **plug-in driver module in StepStick format** (owner, 2026-11-11).
- DRV-02 Default module: TMC2240 (36 V, built-in current sensing, programmable microstep table, SPI). The sockets also take TMC2209 modules (UART), selected by solder jumpers *(proposal)*. Current, microsteps and chopper mode are set from firmware.
- DRV-03 Current per axis is set in firmware and survives a reboot; no trimmers.
- DRV-04 Stall and fault per axis reach the MCU. One shared line is allowed when firmware can tell the axis over the driver bus *(proposal)*.
- DRV-05 Thermal: the modules carry their own heat sinks; the board leaves room and an air path for them, and for the fan (AUX-03).
- DRV-06 Struck: an external driver plugs into the same socket through an adapter, so no separate port (2026-11-11, *proposal*).

### Position sensing (ENC)
- ENC-01 **Four** absolute sensor ports on I2C, each on its own channel of an I2C multiplexer, for cheap AS5600 or MT6701 boards (owner, 2026-11-11).
- ENC-02 Port pinout is identical on all axes: supply, ground, SDA, SCL.
- ENC-03 One home/limit input per axis, protected, for heads without an absolute sensor on that axis.
- ENC-04 Sensor cable integrity is proven for the longest run in the mechanics, by a bench test before the board
  is ordered (R-T2). A tilt sensor through a hollow pan shaft runs a long way next to motor wires, and I2C is the weaker bus for that.
- ENC-05 Pull-ups per port can be changed by solder jumper, and the bus clock in firmware, so a long cable can be tuned *(proposal)*.
- ENC-06 After a restart, pan and tilt find their position from the encoders, with no homing move. How close a preset then lands is measured on the rig (R-T2). That result decides between the AS5600, the MT6701, or an extra reference such as a hall sensor on the home input (owner, 2026-11-11).

### Control (CTL)
- CTL-01 MCU: a plug-in **ESP32-S3-DevKitC-1U** (N8 preferred) on headers, with its U.FL antenna connector (owner, 2026-11-11). The antenna goes out through the housing wall on a U.FL-to-SMA lead.
- CTL-02 WiFi and ESP-NOW from the MCU board.
- CTL-03 Wired Ethernet from a **plug-in W5500 module with its own RJ45 jack**, on SPI (owner, 2026-11-11).
- CTL-04 Struck: no RS-485. Pelco-D and VISCA run over the network, and a console uses Art-Net or sACN instead of DMX (owner, 2026-11-11).
- CTL-06 Struck: no CAN (owner, 2026-11-11).
- CTL-07 The MCU board's USB port is reachable with the head closed, for flashing and logs.

### Camera (CAM)
- CAM-01 Struck: the owner's camera has no LANC, and a zoom motor is needed anyway (2026-11-04).
- CAM-02 Struck: no tally or record output (owner, 2026-11-11).

### Other I/O (AUX)
- AUX-01 A spare multiplexer channel on a header, for a display or sensor.
- AUX-02 A status LED, dark during a show; the MCU board's own LED may serve.
- AUX-03 One switched output with PWM, for a fan (owner, 2026-11-11). Off by default; the head must meet its targets without it.
- AUX-04 Board temperature read by firmware.
- AUX-05 Test points on every rail and bus.

### Physical (BRD)
- BRD-01 Outline and mounting fit the base of the new head, which is designed together with the board (owner, 2026-11-11; R-06).
- BRD-02 SMD parts on top, assembled by JLC with Economic PCBA, so no part may be Standard Only. Plug-in modules and connectors are soldered by the owner.
- BRD-03 Two layers, unless a calculation shows a need for more *(proposal)*.
- BRD-04 No fixed outline; it must fit the base (MEC-08), with connectors at the edges. Smaller is better when it costs no more.

## Firmware (FW)

A new code base. The old firmware in `PTZ-head` is reference only.

- FW-01 Stack, decided in the first firmware spec. C++ in any case. The MCU makes the step pulses: FastAccelStepper drives four axes with hardware-generated steps on the ESP32-S3.
- FW-02 Motion core: velocity and position moves with acceleration limits per axis, coordinated preset moves that
  arrive together, and soft limits. Pure logic, tested on the host.
- FW-03 Absolute position at boot when the encoder sits on the output axis; homing via a home input or stall otherwise.
  Which applies is configuration per axis.
- FW-04 Presets: store and recall named positions, kept across power loss.
- FW-05 Control sources run side by side behind one command interface: OSC first. VISCA over IP, ESP-NOW, Art-Net and sACN, and Pelco-D over IP follow. **[OPEN: order]**
- FW-06 Feedback: position, state and faults to whoever controls the head.
- FW-07 Safety: a watchdog stops motion on lost control, a failed sensor read, a driver fault or bad input voltage.
- FW-08 Every per-head value (ratios, directions, currents, limits, sensor type) is configuration, set without a rebuild.
- FW-09 OTA updates over the network, so the head need not be opened.
- FW-10 A web page for setup and calibration. **[OPEN: v1 or later]**
- FW-11 A preset always lands from the same side, to take out backlash and hysteresis (R-08).

## What the 3D design must provide (MEC)

These flow from the software and electronics into the mechanics, and are the input the design is waiting for.

- MEC-01 Board space in the base: outline, height including the plug-in modules and their heat sinks, mounting points and where connectors exit. The 3D head does not exist yet, so Claude helps design both.
- MEC-02 Absolute at boot only works with a **magnet on the output axis** that turns less than once over the whole
  range. On a motor shaft behind a reduction, the position is gone after a restart.
- MEC-03 A magnet must sit on the axis centre, with no steel within about 5 mm. A hollow pan shaft has its centre taken
  by cables, so pan needs a 1:1 belt to a separate sensor shaft, or a different sensor type.
- MEC-04 **Wire count through the shafts.** With a separate I2C cable per sensor: motors 12 + sensors 12 = 24 wires for tilt, zoom and focus. The bore is sized for that, or a remote node sits above pan (IDEA-02).
- MEC-05 An SMA bulkhead in the housing wall for the antenna, outside the carbon-filled walls.
- MEC-06 Heat: designed to work without a fan, with room to add one (AUX-03). The board stays off the plastic.
- MEC-07 Pan range is limited, with a cable service loop (owner, 2026-11-04). No slip ring.
- MEC-08 The base is at most Ø165 mm (owner, 2026-11-04). One belt stage per axis, no double belt (owner, 2026-11-04).

## Out of scope for v1

- Closed-loop control in our own firmware.
- Selling: CE marking, a release process and series production. One head, for the owner (2026-11-04).

## Part check (JLC, 2026-11-11)

Library type and price from JLC's parts search, checked once; recheck at order time. Rev A's full sourcing is in `hardware/sourcing/`.

| Part | LCSC | Library | Price |
| --- | --- | --- | --- |
| TCA9548APWR (I2C multiplexer) | C130026 | Extended | $0.82 |
| XL1509-5.0E1 (5 V buck, up to 40 V in) | C61063 | Basic | $0.25 |
| AMS1117-3.3 | C6186 | Basic | $0.19 |
| SS34 (Schottky) | C8678 | Basic | $0.04 |
| AO3400A (fan MOSFET) | C20917 | Basic | $0.08 |
