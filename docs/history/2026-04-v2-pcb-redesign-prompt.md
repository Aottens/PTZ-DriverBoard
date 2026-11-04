# PTZHead v2 — PCB Redesign for Encoder Integration

## Project Context

I have a working ESP32-based 3-axis Pan-Tilt-Zoom camera head controller. v1.0 is shipped and bench-validated: pure OSC control over WiFi from Bitfocus Companion, FastAccelStepper-driven motion, 3 stepper motors (pan, tilt, zoom) with TMC-style drivers (active-low enable).

I'm now planning v2, and the first hardware step is **adding absolute position feedback** via AS5600 magnetic rotary encoders on each axis. This requires a PCB revision.

## Current ESP32 Pin Usage (do not change)

| GPIO | Function |
|---|---|
| 16, 17, 25 | Pan step / dir / enable (active-low) |
| 18, 19, 26 | Tilt step / dir / enable (active-low) |
| 22, 23, 27 | Zoom step / dir / enable (active-low) |

Note: GPIO22 is occupied by Zoom STEP, so default I2C pins (21/22) are unusable. Motor pins stay as-is.

## What's Being Added

Three **AS5600** 12-bit absolute magnetic rotary encoders (I2C, fixed address 0x36), one per axis, multiplexed through a **TCA9548A** I2C multiplexer because all three AS5600s share the same address.

### New pin assignments (free GPIOs, no strapping/ADC conflicts)

| Signal | GPIO |
|---|---|
| I2C SDA | 32 |
| I2C SCL | 33 |
| TCA9548A RESET | 4 |

### Components

- 1x **TCA9548A** I2C multiplexer, address 0x70 (A0/A1/A2 tied GND)
- 3x **AS5600** breakout boards (off-the-shelf, one per axis: pan, tilt, zoom)
- 3x diametrically-magnetized neodymium magnets (typ. 6x3mm) mounted on each shaft end
- 3x **10kΩ** pull-up resistors to 3V3 on SDA, SCL, and RESET (main I2C bus only — AS5600 breakouts already have their own pull-ups downstream of the mux)
- Decoupling: 100nF near each breakout VCC, 10µF bulk near mux

### Topology

```
ESP32 ── main I2C (SDA/SCL/RST, 10k pull-ups) ── TCA9548A
                                                     ├── Ch0 → AS5600 (Pan)
                                                     ├── Ch1 → AS5600 (Tilt)
                                                     └── Ch2 → AS5600 (Zoom)
```

Star topology from mux to each breakout. I2C branch cable runs up to ~15cm.

## Design Requirements

1. **Mechanical mounting** — Each AS5600 breakout must sit rigidly above the end of its axis shaft, with the chip face 0.5–3mm from a diametric magnet glued/pressed onto the shaft end. Magnet must be centered within ~1mm of the chip. **No ferrous material within ~5mm** of the sensor (watch for steel set screws).
2. **Power** — All 3.3V logic. Steppers run off separate 12V (existing).
3. **I2C integrity** — 15cm max branch runs, twisted or adjacent routing for SDA/SCL pairs on each channel, keep away from stepper cables.
4. **Reset control** — TCA9548A RESET line pulled high via 10kΩ to 3V3, driven by GPIO4 for firmware-controlled bus recovery.
5. **Test points** on main SDA/SCL/RST and on each downstream channel pair for scope/logic-analyzer debugging.
6. **Keep existing motor driver layout and connectors unchanged** where possible.

## What I Need Help With

1. **Review the electrical design** — Am I missing anything? Protection, ESD, bulk caps, routing concerns with steppers nearby?
2. **Mechanical mounting strategy** — How should the AS5600 breakouts be physically mounted over each axis shaft? I'll need custom brackets or PCB mount points. What's the cleanest approach for:
   - A rotating pan axis (large shaft, likely)
   - Tilt axis (perpendicular to pan)
   - Zoom axis (smaller, attached to lens ring)
3. **Magnet sourcing and attachment** — Recommendations for diametric magnets and reliable attachment to existing stepper shafts (which may already have couplers/pulleys).
4. **PCB layout** — Should encoder mount points live on the main board, or on small daughter boards connected via cable? Tradeoffs?
5. **Schematic + layout** — Help me draft a schematic for the encoder subsystem that I can recreate in **EasyEDA (online editor)** and merge into my existing board revision. Reference EasyEDA/LCSC part numbers where possible.

## What I Don't Want

- **No AS5600L** (address is OTP programmable — one-time burn, too risky)
- **No closed-loop stepper motors** (considered, rejected — prefer absolute position on boot without homing)
- **No changes to the existing OSC/motor control firmware architecture** — encoders are additive

## Starting Point

Assume I'm comfortable with electronics and firmware but want a sanity check on mechanical/PCB design choices before committing to a board spin. Walk me through it step by step, starting with the mechanical mounting question since that's the biggest unknown.
