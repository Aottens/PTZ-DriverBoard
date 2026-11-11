# PTZ driver board — Architecture

This describes **Rev B as designed** (2026-11-11, `hardware/`): a two-layer carrier board for plug-in modules. The
firmware part is still a proposal. Rev A, with its drivers on the board, is under the git tag `rev-a`.
The research questions in `docs/research/README.md` stay open: the rig can still overturn a part choice.

## Blocks

```
 11-17 V ─ J101 ─ P-FET (reverse) ─┬─ fuse T 5 A ─ VM ─ TVS, 4 × 100 µF ─► 4 driver sockets ─► motors M1..M4
                                   └─ fuse T 1 A ─ 5 V module (SIP-3) ─ diode ─ +5V
 +5V ─┬─► MCU module's 5V pin (its own USB feeds the same net through the module's diodes)
      ├─ regulator ─ +3V3      multiplexer, Ethernet module, drivers' logic supply, pull-ups
      ├─ regulator ─ +3V3_SNS ─ jumper (or +5V) ─ V_SNS ─► sensor ports, home plugs, spare port
      └─ jumper (or VM) ─► fan

 ESP32-S3-DevKitC-1U on sockets (28 pins used, none spare; firmware/include/pins.h is the one place they are assigned)
  ├─ SPI ─┬─ 4 × driver socket (TMC2240), each behind three solder jumpers and with its own select line
  │       └─ WIZ850io Ethernet module (W5500, own RJ45 jack)
  ├─ STEP, DIR × 4 ─► driver sockets                 ├─ DRV_ENN ─► all four (pulled up: off at reset)
  ├─ DIAG_OR ◄─ diode-OR of the four drivers' DIAG   ├─ HOME × 4 ◄─ protected inputs
  ├─ I2C ─ TCA9548A ─┬─ channel 0..3 ─► sensor ports S1..S4 (AS5600 or MT6701 boards)
  │                  └─ channel 4 ─► spare header
  ├─ ADC ◄─ VM / 11, board thermistor                ├─ PWM ─► fan switch
  └─ RST ─ diode ─► reset of multiplexer and Ethernet module
```

Per axis: a socket for a StepStick driver module, a motor connector, a sensor port on its own multiplexer channel
with pull-ups chosen by solder jumper and an ESD array, and a home input with a clamp.

What JLC assembles is 108 small SMD parts on 24 BOM lines. What the owner buys and fits: the MCU, driver and
Ethernet modules, the 5 V regulator, two fuses, four capacitors, and every connector (`hardware/ASSEMBLY.md`).

## What stops a motor

1. The MCU: `DRV_ENN` high, on a direct pin, to all four drivers.
2. Nothing drives the bridges at reset: `DRV_ENN` is pulled up on the board and on every module.
3. A stall or fault of any driver raises `DIAG_OR`; firmware asks the drivers over SPI which one.
Unlike Rev A's TMC5240, these drivers do not stop a motor on a home input by themselves: the MCU makes the step
pulses, so the watchdog and the limits are firmware's (FW-07).

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
board builds did not need them: schematic and board are written by the scripts in `hardware/tools/`.
