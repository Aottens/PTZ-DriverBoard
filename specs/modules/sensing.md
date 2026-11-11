# Module spec: position sensing (ENC), Rev B

Status: **written in the Rev B one-run build (2026-11-11); gate 1 is the owner's approval of `docs/prompts/fable-board-rev-b.md`.**
Grows out of ENC-01..06 in `specs/PRD.md`. Nets and references here are the contract that `hardware/check_netlist.py` checks.
Rev A's version of this file is under the git tag `rev-a`.

## What it does

```
MCU I2C_SDA / I2C_SCL ── U701 TCA9548A ─┬─ channel 0..3 ─ 100 Ω ─ J303 … J603   sensor port 1..4
   (4.7 kΩ to +3V3)       address 0x70  └─ channel 4 ──── 100 Ω ─ J701          spare header (AUX-01)
V_SNS = +3V3_SNS (as delivered) or +5V, by JP101: supply and pull-ups of all five ports
MCU HOMEn ── 10 kΩ ── HOMEn_IN ── J302 … J602                                   home input 1..4
```

The AS5600 has one fixed I2C address (0x36, datasheet v1-06) and the MT6701 defaults to 0x06 (datasheet Rev 0.1), so
each sensor sits alone behind its own channel of the multiplexer. Axis n has its references in the hundreds a = n + 2.

## Parts

| Ref | Part | LCSC | Fitted by | Datasheet read |
| --- | --- | --- | --- | --- |
| U701 | TCA9548APWR, 8-channel I2C switch, TSSOP-24 | C130026 (Extended) | JLC | TI SCPS207H, September 2024, pin table |
| U702, U703, U704 | SRV05-4, four-line ESD array, SOT-23-6 | C7420376 (Preferred) | JLC | see `hardware/datasheets/README.md` |
| D302 … D602 | BAV99, two diodes in series, SOT-23 | C2500 | JLC | Nexperia BAV99: 1 anode, 2 cathode, 3 common |
| J303, J403, J503, J603 | JST B4B-PH-K-S, 4 pins, 2.0 mm, top entry | none | owner | |
| J302, J402, J502, J602 | JST B3B-PH-K-S, 3 pins, 2.0 mm, top entry | none | owner | |
| J701 | Pin header 1×4, 2.54 mm | none | owner | |
| resistors and capacitors | 0603, values in the criteria | Basic | JLC | |
| JP304 … JP605, JP701, JP702 | Solder jumpers, two pads | none | bare copper | |

## Acceptance criteria

- **ENC-01 Multiplexer.** U701: pin 24 `+3V3`, pin 12 `GND`, C701 (100 nF) across them; pins 1, 2 and 21 (A0, A1,
  A2) to `GND`, so its address is 0x70; pin 23 `I2C_SDA`, pin 22 `I2C_SCL`; pin 3 (RESET, active low, no pull-up
  inside) on `PERIPH_RST_N` (CTL-06). R701 and R702 (4.7 kΩ) pull `I2C_SDA` and `I2C_SCL` to `+3V3`. Channel k is
  on pins SDk / SCk: channel 0 = pins 4 / 5, 1 = 6 / 7, 2 = 8 / 9, 3 = 10 / 11, 4 = 13 / 14. Channels 5, 6 and 7
  (pins 15 to 20) are not connected.
- **ENC-02 Sensor ports.** Port n is on channel n − 1: `MUXn_SDA` and `MUXn_SCL`. Ja03 has the same pin order on
  all axes: 1 = `V_SNS`, 2 = `GND`, 3 = `SNSn_SDA`, 4 = `SNSn_SCL`. Ra04 (100 Ω) joins `MUXn_SDA` to `SNSn_SDA`
  and Ra05 (100 Ω) joins `MUXn_SCL` to `SNSn_SCL`: they take the edge off a long cable and limit what a discharge
  can push into U701.
- **ENC-03 Home inputs.** Ja02: 1 = `V_SNS` (for a hall sensor), 2 = `GND`, 3 = `HOMEn_IN`. Ra02 (10 kΩ) pulls
  `HOMEn_IN` to `+3V3`, so a switch to ground reads low. Ra03 (10 kΩ) joins `HOMEn_IN` to `HOMEn`, which goes to
  the MCU and has Ca03 (10 nF) to `GND` and Da02 as a clamp: pin 1 `GND`, pin 2 `+3V3`, pin 3 `HOMEn`. With 17 V
  on the pin, the calculation in `hardware/calc/power.py` gives 1.3 mA into the clamp and 19 mW in Ra02.
- **ENC-04** The longest sensor cable is proven on the rig (R-T2), not here. What the board gives that test:
  ENC-05, ENC-06 and a test point on the bus.
- **ENC-05 Pull-ups per port, by solder jumper.** Each port has two pairs of pull-ups from its SDA and SCL lines
  on the connector side (`SNSn_SDA`, `SNSn_SCL`):
  - Ra06 and Ra07 (4.7 kΩ) to `PUn_A`, which JPa04 joins to `V_SNS`: closed as delivered;
  - Ra08 and Ra09 (2.2 kΩ) to `PUn_B`, which JPa05 joins to `V_SNS`: open as delivered.

  That gives none, 4.7 kΩ, 2.2 kΩ or 1.5 kΩ per port. Sensor boards often carry their own pull-ups; then JPa04 is
  cut. The bus clock is a firmware setting.
- **ENC-06 Supply of the ports.** `V_SNS` is `+3V3_SNS` as delivered, from its own regulator, so a short on a
  sensor cable does not take down the logic supply (POW-08). JP101 can move `V_SNS` to `+5V`: the multiplexer then
  translates, since each side has its own pull-ups (TCA9548A datasheet, voltage translation). With `V_SNS` on 5 V
  a short on a sensor cable does take down `+5V`.
- **ENC-07 ESD.** Every line that leaves the board on a sensor port has a channel of an SRV05-4 at its connector:
  U702 holds `SNS1_SDA`, `SNS1_SCL`, `SNS2_SDA`, `SNS2_SCL` on pins 1, 3, 4, 6 in that order; U703 the same for
  ports 3 and 4; U704 holds `AUX_SDA` and `AUX_SCL` on pins 1 and 3, with pins 4 and 6 not connected. On each,
  pin 2 is `GND` and pin 5 is `V_SNS`. The home inputs are protected by their resistors and clamp (ENC-03), which
  also survive a steady 17 V; an SRV05-4 would not.
- **ENC-08 Spare channel (AUX-01).** J701: 1 = `V_SNS`, 2 = `GND`, 3 = `AUX_SDA`, 4 = `AUX_SCL`, on channel 4
  (`MUX5_SDA`, `MUX5_SCL`) through R703 and R704 (100 Ω). Pull-ups as on a sensor port: R705 and R706 (4.7 kΩ) to
  `PU5_A` with JP701 closed, R707 and R708 (2.2 kΩ) to `PU5_B` with JP702 open.

## Not verified in this build

- Which sensor board the head will use, and whether it has pull-ups, is open until the rig (R-T2). The MT6701
  datasheet that could be downloaded is Rev 0.1; its address can be reprogrammed.
- The SRV05-4's pin order is from the part's datasheet as linked by LCSC; its rotation is on the JLC preview checklist.
