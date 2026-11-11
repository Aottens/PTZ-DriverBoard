# Bring-up checklist: driver board Rev B

Only the owner can run this. Copy it to `tests/hardware/runs/<date>-bringup-rev-b.md`, tick it there and write the
measured value behind each step. Stop at the first step that fails and note it under *Open points*.

Nothing on this board has been measured: every expected value below is a calculation (`hardware/calc/power.py`) or
a datasheet figure. Test points are named on the silkscreen. Use a lab supply with its current limit set **before**
connecting. The board comes from JLC with its SMD parts only; the steps say when to solder what
(`hardware/ASSEMBLY.md` has the full list). Keep the modules out until a step asks for one.

## 0. The bare board, before any soldering

- [ ] 0.1 Look at the board next to `hardware/fab/render_top.png`: every SMD part present, no bridges on U701 (the
      24-pin chip) and on the five six-pin ESD arrays (U301, U401, U501, U601, U702).
- [ ] 0.2 **Polarity as in the JLC preview list in the pull request:** the stripe of the six tantalum capacitors
      (three beside each 3.3 V regulator: C111, C116, C117 and C114, C118, C119; the stripe is the plus) is on the
      side the render shows; D101 (TVS) has its band towards the north edge; D102 has its band towards the west.
- [ ] 0.3 **TVS direction.** Multimeter on diode test: red lead on `GND`, black on `VM` reads 0.5 to 0.8 V; leads
      swapped reads open. If it is the other way round, D101 is fitted reversed: turn it before going on. The same
      for D103, the second TVS beside the 5 V module: red on `GND`, black on the module's `IN` pad.
- [ ] 0.4 Resistance to `GND`: `5V` above 1 kΩ, `3V3` above 500 Ω, `VSNS` above 500 Ω, `VIN` open (above 100 kΩ),
      `VM` above 50 kΩ (R103 and R104 are 110 kΩ).
- [ ] 0.5 Solder jumpers as delivered: the twelve `SPI` jumpers closed; in each `PU` pair the bridged one closed
      and the other open; `VSNS` on the `3V3` side.

## 1. Logic supply, current-limited (POW-01, POW-02, POW-03, POW-07, POW-08)

Solder J101, F102 (T 1 A, or its holder with the fuse in) and U101 (the 5 V module, a K7805-1000R3 or a Traco
TSR 1-2450; pin 1 at `IN`). **Not yet:**
F101, the capacitors, the sockets.

- [ ] 1.1 **Reverse polarity first, on purpose:** supply at 12 V, limit 50 mA, plus and minus swapped on J101.
      Expected: under 1 mA, `VIN` stays below 0.3 V. Switch off.
- [ ] 1.2 Correct polarity, 12 V, limit 100 mA. Expected: 10 to 30 mA. If the supply sits in its limit, switch off.
      In this section switch the lab supply on with the board connected; do not plug a live lead into J101.
- [ ] 1.3 `VIN` within 0.1 V of the supply. `5V` 4.5 to 4.9 V (the module's 5.0 V less D102). `3V3` 3.23 to 3.37 V.
      `VSNS` 3.23 to 3.37 V. `VM` below 0.1 V: F101 is not fitted.
- [ ] 1.4 Raise the supply slowly to 17 V: the current falls a little, the three rails do not move. Back to 12 V.
- [ ] 1.5 Lower the supply to 11 V: the rails hold.
- [ ] 1.6 `RST` reads 3.3 V (nothing holds the peripherals in reset without the MCU module).

## 2. Motor supply (POW-02, POW-04, POW-06)

Switch off. Solder C101 to C104 (stripe = minus, away from the `+` on the silkscreen) and F101 (T 5 A).

- [ ] 2.1 12 V, limit 200 mA. Expected: a short charging pulse, then the same current as in 1.2. `VM` within 0.1 V
      of the supply.
- [ ] 2.2 17 V: `VM` follows. No part warm.
- [ ] 2.3 **Hot-plug:** supply on at 17 V, limit 1 A, then plug J101 in. If an oscilloscope is at hand: the peak on
      `VM` stays below 20 V with general-purpose capacitors (calculated 18.5 V at worst). Without one: skip, and
      note it.
- [ ] 2.4 Switch off: `VM` falls slowly (only the divider discharges the capacitors: about two minutes to 1 V).

## 3. The MCU module on USB alone (POW-05, CTL-01, CTL-07)

Solder the two 22-pin sockets for A201. Supply disconnected. Plug the ESP32-S3-DevKitC-1U in: USB sockets at the
west edge, over the `USB` box on the silkscreen; its `3V3` corner pin at the pad marked `3V3`.

- [ ] 3.1 USB cable into the module's `USB` port, through a USB power meter if there is one. Expected: under 150 mA.
- [ ] 3.2 `5V` 4.4 to 4.9 V. `3V3` and `VSNS` 3.2 to 3.4 V. `M3V3` (the module's own regulator) 3.2 to 3.4 V.
- [ ] 3.3 **USB must not reach the motor side:** `VIN` below 0.3 V and `VM` below 0.3 V.
- [ ] 3.4 The computer sees the module; a blink program flashes and runs. The module's own LED is the status light.
- [ ] 3.5 Unplug USB. Connect the supply at 12 V, limit 300 mA: the module starts from the board's 5 V. Then plug
      USB in as well: nothing changes, and with the supply switched off again the module keeps running from USB.
- [ ] 3.6 With the supply on and USB unplugged, measure across the USB socket's shell and its VBUS pin if you can
      reach it (or trust the module's diodes D1 and D7): no 5 V comes out of the USB socket.

## 4. What firmware reads (POW-06, AUX-04, DRV-04, DRV-05, CTL-06)

A test program that prints the ADC readings and pin states.

- [ ] 4.1 `VM_SENSE` (GPIO1): supply voltage divided by 11: 1.09 V at 12 V, 1.55 V at 17 V. Pull F101: it reads 0.
- [ ] 4.2 `NTC_SENSE` (GPIO2): about 1.65 V at 25 °C; it falls when you warm RT801 (marked `NTC`) with a finger.
- [ ] 4.3 `ENN` reads 3.3 V while the module's RST button is held, and whenever firmware does not drive it low.
- [ ] 4.4 `DIAG` (GPIO3) reads 0 V with no driver plugged in.
- [ ] 4.5 `RST` falls below 0.5 V while the module's RST button is held, and returns to 3.3 V.
- [ ] 4.6 Download mode still works with everything soldered: hold BOOT, tap RST, and the computer sees the ROM's
      serial port. GPIO46 carries DIR2 and must be low for this; nothing on the board pulls it up.

## 5. Sensor ports and home inputs (ENC-01 to ENC-08)

Solder the PH connectors and the `I2C` header.

- [ ] 5.1 An I2C scan on GPIO40 (SDA) and GPIO39 (SCL) finds the multiplexer at 0x70 and nothing else.
- [ ] 5.2 Pin 1 of every `S` and `H` connector and of `I2C` carries `VSNS`; pin 2 is ground.
- [ ] 5.3 One sensor board on `S1`, channel 0 selected: the scan finds it (AS5600 at 0x36, MT6701 at 0x06). Repeat
      on `S2` to `S4` (channels 1 to 3) and on `I2C` (channel 4). With another channel selected it is not found.
- [ ] 5.4 On a scope or by reading back: SDA and SCL rest at `VSNS`. If the sensor board has pull-ups of its own
      and the edges are slow or the low level is above 0.4 V, cut that port's bridged `PU` jumper.
- [ ] 5.5 The longest cable the head will have, beside a running motor: count read errors (this is R-T2 on the rig).
- [ ] 5.6 Each `H` input reads high open and low with pins 2 and 3 joined. GPIO43 (`H4`) prints the boot log at
      reset: that is expected.
- [ ] 5.7 **Short test:** `VSNS` to ground on one `S` connector through an ammeter, briefly: about 1 A, `5V` may
      dip and the module restart; `3V3` stays. Remove the short: everything returns. U103 gets hot and switches
      itself off if the short stays; that is its protection.

## 6. Ethernet (CTL-03)

Solder the WIZ850io in (or on low sockets), jack towards the east edge over the `RJ45` mark.

- [ ] 6.1 Supply current rises by 60 to 140 mA. `3V3` still 3.2 to 3.4 V.
- [ ] 6.2 Firmware reads the W5500's version register (0x04) over SPI with `ETH_CS_N` (GPIO42).
- [ ] 6.3 Link comes up on a switch; a ping answers. Start at 8 MHz SPI clock.

## 7. Drivers, one at a time (DRV-01 to DRV-09)

Solder the driver sockets (2 × 8 pins and the 2-pin piece each) and the motor connectors. Supply at 12 V, limit 0.5 A.

- [ ] 7.1 Before plugging any module: on each socket, the `VM` corner pin carries the supply, the pin next to it is
      ground, the `EN` corner pin reads 3.3 V. **A module plugged in the wrong way round is destroyed:** its `VM`
      and `EN` corners are printed on the board and on the module.
- [ ] 7.2 One TMC2240 module in `DRIVER 1`, no motor. Current rises by under 50 mA. Firmware reads its
      IOIN register (0x04) over SPI with `DRV1_CS` (GPIO13): the version field is neither 0x00 nor 0xFF.
- [ ] 7.3 Set DIAG0 to push-pull, active high (`diag0_pushpull` in GCONF: as an open-drain output it cannot raise
      the shared line); force a fault flag (or stall test later): `DIAG` goes to about 3 V.
- [ ] 7.4 Motor on `M1`, current set to 0.3 A, limit of the supply 1 A, `ENN` low: the motor holds, and turns on
      step pulses (GPIO12 step, GPIO11 direction). `ENN` high: it is free.
- [ ] 7.5 Repeat 7.2 to 7.4 for sockets 2, 3 and 4, then with all four modules in. Read all four over SPI in turn:
      no driver answers for another.
- [ ] 7.6 With Ethernet traffic running (a ping flood), read the drivers 1000 times: no read error.
- [ ] 7.7 Raise the currents to what the head needs, supply limit 4 A. After ten minutes, read each driver's
      temperature (the TMC2240 reports it) and `NTC_SENSE`. Note them. Nothing above 80 °C.
- [ ] 7.8 A TMC2209 module, if one is to be used: cut the three `SPI` jumpers of its socket first. Firmware talks to
      it on that socket's select pin as a one-wire UART.

## 8. Fan (AUX-03)

- [ ] 8.1 `FAN` pin 1 carries about 4.6 V: the output is for a 5 V fan of at most 0.2 A, never one for the supply
      voltage. With GPIO45 low the fan is off; high, it runs; PWM changes its speed.
- [ ] 8.2 The fan stays off while the module's RST button is held.

## 9. In the base

- [ ] 9.1 The steps of `hardware/ASSEMBLY.md` can be done as written: every screw, plug and module is reachable.
- [ ] 9.2 Nothing touches the pulley plate: the driver heat sinks and the supply plug are the tallest (24.6 and
      24.5 mm by calculation).

## Open points

- none
