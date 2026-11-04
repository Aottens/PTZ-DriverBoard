# PTZ driver board — Architecture

Draft, until `specs/PRD.md` passes gate 1. **This reflects the first draft (ESP32-S3 WROOM, TMC2209, I2C mux); the research phase in
`docs/research/README.md` may replace all of it, and this file is rewritten when R-03, R-04 and R-05 close.**

## Blocks

```
 12-24 V ─► protection ─┬─► motor rail ─► 4× TMC2209 ─► motors (+ external driver ports)
                        └─► buck 5 V ─► buck/LDO 3V3 ─► logic

 USB-C ───────────► ESP32-S3-WROOM-1U (external antenna)
                     ├─ STEP/DIR ×4, TMC UART ───────► drivers
                     ├─ I2C ─┬─ TCA9548A ────────────► encoder ports ×4 + spare
                     │       └─ TCA9555 ─────────────► EN, DIAG, home inputs, tally
                     ├─ SPI ─► W5500 ────────────────► Ethernet
                     └─ UART/TWAI ───────────────────► RS-485, RS-232/422, CAN, LANC
```

## Pin budget (estimate, to verify against the datasheet)

ESP32-S3-WROOM-1U-N16R8 brings out about 33 usable GPIOs (octal PSRAM takes 35 to 37). Wiring everything directly
needs about 51 (both tables below), so it does not fit.

| Direct on the MCU | Pins |
| --- | --- |
| STEP and DIR, 4 axes | 8 |
| TMC UART | 2 |
| I2C + mux reset | 3 |
| USB, boot | 3 |
| UART0 for logs | 2 |
| W5500 (SPI, INT, RST) | 6 |
| RS-485 (TX, RX, DE) | 3 |
| RS-232/422 | 2 |
| CAN | 2 |
| LANC | 2 |
| Status LED, expander INT | 2 |
| **Total** | **35 of about 33** |

| On the TCA9555, 16 pins | Pins |
| --- | --- |
| EN, 4 axes | 4 |
| DIAG, 4 axes | 4 |
| Home inputs, 4 axes | 4 |
| Tally, record, fan enable, button | 4 |

Even with the expander this is over budget by about two, so dropping a port (or sharing RS-232/422 with RS-485) is
part of the OPEN port choice in the PRD. Time-critical signals stay direct; signals on the expander arrive with I2C
latency, which is fine for homing but must not be the only stop on a fast move. FW-07 must account for that.

## Firmware layers (proposal)

- `firmware/src/core/`: plain C++ without framework includes. Motion planning, limits, presets, protocol parsing.
  Runs in host tests.
- `firmware/src/hal/`: thin glue to steppers, sensors and network.
- `firmware/src/sources/`: one adapter per control source, all behind one command interface.

## Folder layout

| Folder | What |
| --- | --- |
| `specs/` | PRD and module specs |
| `hardware/` | KiCad project, `check_netlist.py`, `fab/`, `review/`, `datasheets/`, `archief/` |
| `firmware/` | Firmware and host tests |
| `mechanica/` | Belt calculations, and in `rig/` the test rig's generator script and exports |
| `tests/hardware/` | Bring-up checklists and runs (gate 3) |
| `docs/history/` | Earlier designs, kept for reference only; never a source of requirements |

## Dependencies

Tools, not shipped: KiCad, Freerouting, KiCAD-MCP-Server, kicad-happy, PlatformIO.
Planned in firmware: FastAccelStepper (licence to check when FW-01 is decided).
