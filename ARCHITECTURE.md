# PTZ driver board — Architecture

This describes **Rev A as designed** (2026-11-10, `hardware/`). The firmware part is still a proposal.
The research questions in `docs/research/README.md` stay open: the rig can still overturn a part choice.

## Blocks

```
 12-24 V ─ J101 ─ P-FET (reverse) ─┬─ 7 A fuse ─ VM ─ TVS, 2 × 220 µF ─► 4 × TMC5240 ─► motors M1..M4
                                   └─ 1.5 A fuse ─ buck ─ +5V ─┬─► external driver ports, fan
                                                               └─ diode ─┐
 USB-C ─ VBUS ───────────────────────────────────────────────── diode ─┴─ VSYS ─ buck ─ +3V3 ─► logic

 ESP32-C6-MINI-1U (22 pins, all used; firmware/include/pins.h is the one place they are assigned)
  ├─ SPI ─┬─ 4 × TMC5240, one chip select each ─┐
  │       ├─ W5500 ─ header J801 ─► off-board  │  chip selects for drivers and sensors come from
  │       │          RJ45 jack with magnetics   │  a dual 2-to-4 decoder: two address lines, two strobes
  │       └─ buffers ─► 4 sensor ports S1..S4 ──┘
  ├─ DRV_ENN ─► all four drivers and the external-port buffer (pulled up: off at reset)
  ├─ I2C ─┬─ PCAL6416A expander: DIAG0/1 × 4, Ethernet INT/RST, RGB LED, tally, record
  │       ├─ TMP1075 board temperature
  │       └─ spare port (Qwiic pin order)
  ├─ expander interrupt (direct pin)
  ├─ UART ─► SP3485 ─► RS-485            ├─ TWAI ─► SN65HVD230 ─► CAN
  ├─ ADC ◄─ VM / 11                      ├─ PWM ─► fan switch
  └─ USB serial/JTAG, boot button
```

Per axis: a TMC5240 that generates the motion itself, a motor connector, a sensor port (SPI, 3.3 V, with the home
input on pin 7 going to the driver's REFL), and an external driver port that carries the driver's own STEP and DIR,
buffered to 5 V and gated by `DRV_ENN`.

## What stops a motor

1. The driver, in the chip: a stall (StallGuard) or the home input. No MCU involved.
2. The MCU: `DRV_ENN` high, on a direct pin. This also cuts the steps to an external driver.
3. Nothing drives the bridges at reset: `DRV_ENN` is pulled up, the chip selects are pulled up.
The expander's interrupt is on a direct pin too, so firmware can act before it has read which input changed.

## Firmware layers (proposal)

- `firmware/src/core/`: plain C++ without framework includes. Motion planning, limits, presets, protocol parsing.
  Runs in host tests.
- `firmware/src/hal/`: thin glue to drivers, sensors and network.
- `firmware/src/sources/`: one adapter per control source, all behind one command interface.
- `firmware/include/pins.h`: pin assignments, read by the schematic generator and the netlist check as well.

## Folder layout

| Folder | What |
| --- | --- |
| `specs/` | PRD and module specs with numbered criteria |
| `hardware/` | KiCad project, checks (`check_netlist.py`, `check_board.py`, `check_fit.py`), `tools/` that generate schematic and board, `calc/`, `fab/`, `review/`, `sourcing/`, `datasheets/` |
| `firmware/` | So far only `include/pins.h` |
| `mechanica/` | Belt calculations and the test rig |
| `tests/hardware/` | Bring-up checklists and runs (gate 3) |
| `docs/history/` | Earlier designs, kept for reference only; never a source of requirements |

## Dependencies

Tools, not shipped: KiCad 10, Freerouting, PlatformIO. The KiCad MCP server and kicad-happy are configured but the
Rev A build did not need them: schematic and board are written by the scripts in `hardware/tools/`.
