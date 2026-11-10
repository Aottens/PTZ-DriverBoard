# Bring-up checklist: driver board Rev A

Only the owner can run this. Copy it to `tests/hardware/runs/<date>-bringup-rev-a.md`, tick it there and write the
measured value behind each step. Stop at the first step that fails and note it under *Open points*.

Nothing on this board has been measured: every expected value below is a calculation (`hardware/calc/`) or a datasheet figure.
Test points are named on the silkscreen. Use the lab supply with its current limit set **before** connecting.

## 0. Before any power

- [ ] 0.1 Look at the board next to `hardware/fab/` renders: every part present, no bridges on the four drivers (U301, U401, U501, U601), the W5500 (U801) and the USB-C socket.
- [ ] 0.2 Pin 1 and polarity as in the JLC preview list in the pull request: the four drivers, U201, U801, D102 (band towards the board's top edge side marked on silk), C101 and C102 (plus mark), Q101.
- [ ] 0.3 With a multimeter, no supply connected: `VM` to `GND` (TP902 to TP906) is not a short (expect it to climb as the capacitors charge); `+3V3` to `GND` (TP905) above 100 Ω; `+5V` to `GND` (TP903) above 100 Ω; `VIN` to `GND` (TP901) not a short.
- [ ] 0.4 Solder jumpers as delivered: JP801 open (RS-485 terminator off), JP802 closed (CAN terminator on), JP901 on the `5V` side.
- [ ] 0.5 Nothing plugged in: no motors, no sensors, no USB.

## 1. USB only (POW-05)

- [ ] 1.1 Plug USB-C into a computer or a 5 V supply through a USB power meter. Expected: below 150 mA, no heat anywhere.
- [ ] 1.2 `VSYS` (TP904) 4.4 to 4.8 V. `+3V3` (TP905) 3.23 to 3.43 V (calculated 3.33 V).
- [ ] 1.3 `+5V` (TP903) below 0.5 V and `VM` (TP902) below 0.5 V: USB must not feed the motor side or the 5 V rail.
- [ ] 1.4 The computer sees the ESP32-C6 as a USB serial/JTAG device. Flash a blink or hello program; it runs after a reset over USB.
- [ ] 1.5 Hold BOOT (SW201) while resetting over USB: the chip enters download mode.
- [ ] 1.6 Unplug USB.

## 2. First power on the input, current-limited (POW-01 to POW-04, POW-07, POW-08)

- [ ] 2.1 **Reverse polarity first, on purpose:** lab supply at 12 V, limit 50 mA, plus and minus swapped on J101. Expected: under 1 mA, `VIN` (TP901) stays below 0.5 V. Then switch off.
- [ ] 2.2 Correct polarity, 12 V, limit 100 mA. Expected: a short charging pulse, then 20 to 50 mA. If the supply stays in current limit for more than 2 s, switch off.
- [ ] 2.3 `VIN` (TP901) within 0.1 V of the supply. `VM` (TP902) equal to `VIN`: fuse F101 conducts.
- [ ] 2.4 `+5V` (TP903) 4.8 to 5.2 V (calculated 4.97 V). `VSYS` (TP904) 4.3 to 4.8 V. `+3V3` (TP905) 3.23 to 3.43 V.
- [ ] 2.5 Lower the supply slowly: `+5V` drops out between 7.5 and 8.7 V (calculated 8.1 V). Raise it again: it returns between 8.6 and 9.8 V (calculated 9.2 V).
- [ ] 2.6 Raise to 24 V, limit 150 mA: the same rail voltages; no part warmer than hand-warm after 5 minutes. Note the input current.
- [ ] 2.7 With firmware that reads the ADC: `VM_SENSE` reads the supply voltage within 5 % at 12 V and at 24 V (POW-06). Each driver's own supply reading over SPI agrees within 5 %.
- [ ] 2.8 Pull the supply plug and put it back at 24 V five times, with the limit at 3 A: nothing resets oddly, F101 survives. If you have a scope: `VM` peaks below 30 V on plugging in (calculated: no overshoot with 1 m of lead).

## 3. Logic

- [ ] 3.1 I2C scan finds 0x20 (expander U203) and 0x48 (temperature sensor U204). The temperature reads room temperature within 3 °C (AUX-04).
- [ ] 3.2 Status LED D201: each of red, green and blue lights when its expander pin goes low. **Note the order you see**: the pin order of this LED could not be checked against the maker's drawing. Green and blue may be dim on 3.3 V.
- [ ] 3.3 The BOOT button reads low on its GPIO when pressed (AUX-02).
- [ ] 3.4 With all four drivers still unconfigured: `DRV_ENN` (TP913) is high at reset (3.3 V), both decoder strobes (TP915, TP916) are high.
- [ ] 3.5 SPI to each driver in turn (address 0 to 3, driver strobe low): the IOIN register returns version 0x40 on all four (DRV-02). With the supply off and only USB on, the drivers must not answer.
- [ ] 3.6 Each driver reports its chip temperature and supply voltage (AUX-04, POW-06).

## 4. Motors, one axis at a time (DRV-01 to DRV-10)

- [ ] 4.1 Supply at 12 V, limit 1 A. One motor on J301 (pins 1-2 one coil, 3-4 the other). Configure axis 1 for 0.3 A, StealthChop. Drive `DRV_ENN` low: the motor holds. Input current as expected, about 0.1 to 0.2 A.
- [ ] 4.2 Move slowly both ways. If the direction is wrong, set it in configuration, not by swapping wires.
- [ ] 4.3 Drive `DRV_ENN` high while moving: the motor is free at once (DRV-07).
- [ ] 4.4 Raise the current in steps to the motor's rated current. Read the driver temperature after 10 minutes holding, and the board temperature from U204. Write both down: **the calculation says four axes at 1.5 A continuously are too much in still air** (`hardware/calc/thermal.py`), so these numbers decide the current limits and whether the spreader or the fan is needed.
- [ ] 4.5 Stall the motor by hand with StallGuard enabled: DIAG0 of that axis shows on the expander and `XINT_N` (TP914) goes low (DRV-04).
- [ ] 4.6 Short one motor output to `GND` through the supply's 1 A limit with the driver enabled: the driver reports a short and switches off; it recovers after `DRV_ENN` is cycled (POW-02c). Do this once, on one axis.
- [ ] 4.7 Repeat 4.1 to 4.3 on J401, J501 and J601.
- [ ] 4.8 All four axes moving together at the currents the head will use, 24 V, for 30 minutes on the bench, board lying free: note board and driver temperatures every 10 minutes.

## 5. Sensor ports and home inputs (ENC-01 to ENC-07)

- [ ] 5.1 Pin 1 of each sensor port (J302, J402, J502, J602) carries 3.2 to 3.4 V; pin 2 is `GND`.
- [ ] 5.2 An AS5047P or another 3.3 V SPI sensor on J302 through a 15 cm lead: reads a stable angle with sensor strobe and address 0. Repeat on the other three ports.
- [ ] 5.3 With a scope on the sensor's clock pin: no clock edges while the firmware talks to a driver or to Ethernet (ENC-05).
- [ ] 5.4 Short pin 7 (HOME) of J302 to pin 2: the driver's REFL input reads active over SPI (ENC-03). Repeat on the other ports.
- [ ] 5.5 Short pin 1 of a sensor port to pin 2 for 5 s: the board may reset; it works again after the short is gone (POW-02c).
- [ ] 5.6 The cable test with the longest lead next to a running motor is R-T2 on the rig; note here if it was done with this board.

## 6. External driver ports (DRV-06)

- [ ] 6.1 Supply on. Pin 1 of J303 carries 4.8 to 5.2 V.
- [ ] 6.2 Configure axis 1 to output step and direction on DIAG0 and DIAG1. With `DRV_ENN` low and a move commanded: a 5 V step signal on pin 2, direction on pin 3.
- [ ] 6.3 Drive `DRV_ENN` high: the step signal stops at once.
- [ ] 6.4 Repeat 6.2 on J403, J503 and J603.

## 7. Ethernet, RS-485, CAN, USB (CTL-02 to CTL-07)

- [ ] 7.1 Ethernet: wire an RJ45 jack with magnetics (for example an HR911105A) to J801 with leads under 10 cm: J801 pin 3 and 4 to the jack's TD+ and TD-, 5 and 6 to RD+ and RD-, 1 to TCT, 7 to RCT, 2 to the jack's ground and shield. The LINK LED lights on a switch; the board answers a ping.
- [ ] 7.2 RS-485: receive DMX or a known serial stream on J802; then transmit and check on the far end. Close JP801 if this board is at the end of the line.
- [ ] 7.3 CAN: with a second node and both ends terminated, frames pass both ways at 500 kbit/s. Without motor power the CAN transceiver is off.
- [ ] 7.4 WiFi with the antenna on the module's connector (a W.FL or MHF III plug, **not** U.FL): the board joins the network; note the signal strength with the board in its place in the base.

## 8. Camera, fan, spare port (CAM-02, AUX-01, AUX-03)

- [ ] 8.1 Tally and record outputs on J901: each pulls a 1 kΩ resistor from 5 V to below 0.2 V when on, and lets it go when off. Both are off at reset.
- [ ] 8.2 Fan on J902 with JP901 on `5V`: runs when the output is on, slows under PWM, is off at reset.
- [ ] 8.3 A Qwiic or STEMMA QT device on J202 answers on I2C.

## 9. In the base

- [ ] 9.1 The board fits its place; every plug can be put in and taken out in the order `hardware/ASSEMBLY.md` gives.
- [ ] 9.2 USB-C and the antenna lead reach the outside.

## Open points

- none
