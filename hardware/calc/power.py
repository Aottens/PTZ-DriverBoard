#!/usr/bin/env python3
"""Power calculations for Rev A (POW-02, -04, -07, -08, -09, ENC-03, CAM-02). Nothing here is measured.

Run: python3 hardware/calc/power.py     Every input is named with its source; asserts hold the spec's numbers.
"""
import math

print("== 1. Input range and the TVS (POW-01, POW-04)")
VIN_MAX = 24.0 * 1.05            # V, a 24 V supply at +5 %
TVS_STANDOFF, TVS_VBR_MIN, TVS_VCLAMP, TVS_IPP = 24.0, 26.7, 38.9, 15.4   # SMBJ24A: V, V, V at A (10/1000 us)
TMC_ABS_MAX, TMC_OP_MAX = 41.0, 36.0                                      # TMC5240 datasheet p10
assert VIN_MAX < TVS_VBR_MIN
print(f"highest supply {VIN_MAX:.1f} V < lowest TVS breakdown {TVS_VBR_MIN} V: the TVS does not conduct in normal use")
print(f"TVS clamp at its full rated pulse {TVS_VCLAMP} V at {TVS_IPP} A: {TMC_ABS_MAX - TVS_VCLAMP:.1f} V below the driver's {TMC_ABS_MAX} V absolute maximum")
assert TVS_VCLAMP < TMC_ABS_MAX

print("\n== 2. Hot-plug (POW-02b)")
L_CABLE = 2.0e-6                 # H, about 1 m of two-wire supply lead per metre pair: an assumption, 2 and 10 uH tried
C_BULK = 2 * 220e-6              # F, C101 + C102
ESR_BULK = 0.30 / 2              # ohm, two 220 uF 50 V general-purpose electrolytics at about 0.3 ohm each: an assumption to check on the part
R_PATH = 0.015 + 0.012 + 0.03    # ohm: Q101 on (15 mOhm), F101 cold (about 12 mOhm), connector and copper (estimate)
for L in (2e-6, 10e-6):
    z0 = math.sqrt(L / C_BULK)
    zeta = (ESR_BULK + R_PATH) / (2 * z0)
    over = math.exp(-math.pi * zeta / math.sqrt(1 - zeta * zeta)) if zeta < 1 else 0.0
    print(f"cable {L * 1e6:.0f} uH: Z0 {z0 * 1000:.0f} mOhm, damping {zeta:.2f}, overshoot {over * 100:.0f} % -> peak {VIN_MAX * (1 + over):.1f} V")
    assert VIN_MAX * (1 + over) < TMC_OP_MAX
print("With ceramic capacitors alone the same loop would ring to twice the supply; the electrolytics' resistance is what damps it.")
energy = 0.5 * C_BULK * VIN_MAX ** 2
i2t = energy / (ESR_BULK + R_PATH)        # all of the charging energy lost in the loop resistance, worst case
F101_I2T = 123.8                 # A2s, nominal melting, 0452007: from a distributor listing, the Littelfuse sheet did not load
print(f"inrush: {energy:.2f} J into the bulk capacitors gives at most {i2t:.1f} A2s; F101 melts at about {F101_I2T} A2s ({F101_I2T / i2t:.0f} times more)")
assert i2t * 10 < F101_I2T

print("\n== 3. Energy coming back from the motors (POW-04)")
J_LOAD = 2.5 * 0.10 ** 2         # kg m2: 2.5 kg payload (TGT-01) at 0.10 m radius, a generous estimate
W_MAX = math.radians(60)         # rad/s at the output (TGT-03)
e_kin = 0.5 * J_LOAD * W_MAX ** 2
dv = math.sqrt(VIN_MAX ** 2 + 2 * e_kin / C_BULK) - VIN_MAX
print(f"all of the head's kinetic energy at 60 deg/s is {e_kin * 1000:.0f} mJ; in {C_BULK * 1e6:.0f} uF it lifts {VIN_MAX:.1f} V by {dv:.2f} V")
KE = 0.42 / (1.5 * math.sqrt(2))  # V s/rad per phase, from 42 Ncm holding torque at 1.5 A RMS (17HE15-1504S): Kt = T / (sqrt(2) I)
w_hand = 2 * math.pi * 1.0 * 7.5  # rad/s at the motor when the head is spun by hand at 1 turn/s through 7.5:1
print(f"a head spun by hand at 1 turn/s: back-EMF peak {KE * w_hand:.1f} V per phase, below the supply, so it cannot pump the rail above it")
assert VIN_MAX + dv < TMC_OP_MAX and KE * w_hand < TMC_OP_MAX

print("\n== 4. Reverse polarity (POW-02a)")
print("Q101 off with its body diode blocking: it sees the reversed supply as Vds, -25.2 V of -40 V rated; gate-source is 0 V")
print(f"forward: gate clamped to 12 V by D101, {(VIN_MAX - 12) / 100e3 * 1e6:.0f} uA through R101; loss at 5 A: {25 * 0.015:.2f} W (15 mOhm, AOD4185 at -10 V)")

print("\n== 5. The 5 V converter U101 (POW-07), TPS54360 datasheet SLVSBB4G equations")
RT = 220.0                       # kOhm
fsw = 92417 * RT ** -0.991       # kHz, eq. 7
R_UV1, R_UV2 = 330e3, 47e3       # R102, R103
v_start = 1.2 + R_UV1 * (1.2 / R_UV2 - 1.2e-6)      # eq. 4/5 solved for the voltages: Vena 1.2 V, I1 1.2 uA, Ihys 3.4 uA
v_stop = v_start - 3.4e-6 * R_UV1
vout = 0.8 * (1 + (47e3 + 5.1e3) / 10e3)            # R106 + R112 over R107, Vref 0.8 V
L, IOUT = 22e-6, 1.5
ripple = (VIN_MAX - vout) * vout / (VIN_MAX * L * fsw * 1e3)
print(f"switching frequency {fsw:.0f} kHz; starts above {v_start:.1f} V, stops below {v_stop:.1f} V; output {vout:.2f} V")
print(f"inductor ripple at {VIN_MAX:.1f} V in: {ripple:.2f} A, peak {IOUT + ripple / 2:.2f} A at {IOUT} A out (L101 saturates above 3 A)")
COUT = 2 * 22e-6 * 0.55          # F: two 22 uF 25 V X5R with about 45 % lost to DC bias at 5 V (estimate)
fp = IOUT / (2 * math.pi * vout * COUT)
fco = math.sqrt(fp * fsw * 1e3 / 2)
rcomp = 2 * math.pi * fco * vout * COUT / (12 * 0.8 * 350e-6)       # gmps 12 A/V, gmea 350 uA/V
ccomp = 1 / (2 * math.pi * rcomp * fp)
cpole = 1 / (math.pi * fsw * 1e3 * rcomp)
print(f"compensation for a {fco / 1e3:.0f} kHz crossover: R {rcomp / 1e3:.1f} kOhm (fitted 4.7k), C {ccomp * 1e9:.0f} nF (22 nF), pole C {cpole * 1e12:.0f} pF (100 pF)")
assert 4.8 < vout < 5.2 and 8.0 < v_stop < v_start < 10.8 and IOUT + ripple / 2 < 3.0

print("\n== 6. The 3.3 V converter U102 (POW-08)")
v33 = 0.6 * (1 + 100e3 / 22e3)   # TLV62569 Vref 0.6 V, R108 over R109
print(f"output {v33:.3f} V")
assert abs(v33 - 3.3) < 0.1

print("\n== 7. Current budget (POW-09)")
LOADS_3V3 = {"ESP32-C6 peak, 802.11b transmit (datasheet p27)": 0.382, "W5500, 100M transmit (datasheet p60)": 0.132,
             "four sensors at 20 mA": 0.080, "spare I2C port": 0.100, "RS-485 driving two terminators": 0.055,
             "CAN transceiver dominant, logic, LEDs, pull-ups": 0.045}
i33 = sum(LOADS_3V3.values())
for k, v in LOADS_3V3.items():
    print(f"  {v * 1000:4.0f} mA  {k}")
VSYS = 5.0 - 0.45                # after D104 or D105
i_vsys = i33 * v33 / (0.90 * VSYS)
print(f"+3V3 peak {i33:.2f} A (budget 0.8 A); from VSYS at {VSYS:.2f} V and 90 % efficiency: {i_vsys:.2f} A through D104 or D105 (1 A parts)")
assert i33 <= 0.8 and i_vsys < 1.0
i5 = i_vsys + 0.200 + 0.200   # external driver ports (PTC), fan on 5 V
print(f"+5V peak {i5:.2f} A of 1.5 A: VSYS, external ports 0.2 A, fan 0.2 A")
assert i5 < 1.5
print(f"on USB alone: {i_vsys:.2f} A peak, above the 0.5 A a plain port gives; average is about {0.3 * v33 / (0.9 * VSYS):.2f} A. Firmware should hold radio power down on USB.")
R_MOTOR, I_MOTOR = 2.3, 1.5      # ohm per phase and A RMS, 17HE15-1504S
p_axis = 2 * I_MOTOR ** 2 * R_MOTOR + 1.7 + 0.22 * 7.85     # copper, driver loss (calc/thermal.py), shaft power at 0.22 Nm and 75 rpm
for vin in (12.0, 24.0):
    i_in = 4 * p_axis / vin + i5 * 5.0 / (0.85 * vin)
    print(f"input at {vin:.0f} V with all four axes at {I_MOTOR} A: {i_in:.1f} A (F101 is 7 A, J101 is rated 10 A)")
    assert i_in < 7.0

print("\n== 8. Small things")
i_home = (24 - 3.3 - 0.3) / 22e3
print(f"24 V on a home input (ENC-03): {i_home * 1e3:.2f} mA through R?06 into the clamp, {(24 - 3.3) ** 2 / 10e3 * 1e3:.0f} mW in the 10k pull-up (0402 is 62 mW)")
assert i_home < 1e-3
print(f"VM_SENSE at {VIN_MAX:.1f} V: {VIN_MAX / 11:.2f} V; at the TVS clamp {TVS_VCLAMP / 11:.2f} V, still inside the pin's 3.6 V limit, with 100k in series")
print(f"tally and record outputs (CAM-02): AO3422 below 0.2 ohm at 2.5 V gate drive, so 0.5 A drops under {0.5 * 0.2:.2f} V; gate drive here is 3.3 V")
