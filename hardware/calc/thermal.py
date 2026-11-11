#!/usr/bin/env python3
"""Driver temperature by calculation (DRV-05). Nothing here is measured.  Run: python3 hardware/calc/thermal.py

Model: the board is one lump that loses heat to the air on both faces; each driver sits a further step above it.
  T_board    = T_air + P_total * R_board
  T_junction = T_board + P_driver * THETA_LOCAL
Inputs, with where each comes from:
"""
BOARD_W, BOARD_H = 0.085, 0.065      # m, the board
H_STILL = 10.0       # W/m2K, natural convection plus radiation from a small plate in still air: an assumption
H_FAN = 25.0         # W/m2K with a small fan moving air over it: an assumption
T_AIR = 35.0         # degC inside the closed base: an assumption
RON_25 = 0.23        # ohm, high side + low side at 25 degC (TMC5240 datasheet p1, p47)
RON_TC = 0.005       # per K: "about 100 degC more gives roughly 50 % more" (p166)
P_IDLE = 0.22        # W per driver: 5 mA at 24 V (p11) plus 0.1 W switching loss, the latter an estimate
P_LOGIC = 1.5        # W: 3.3 V at 0.3 A average plus converter losses (calc/power.py)
THETA_JA = 29.0      # K/W, TQFN on a JEDEC four-layer board (p10)
JEDEC_AREA = 0.0762 * 0.1143         # m2, the JESD51-7 board
T_J_MAX = 125.0      # degC operating limit (p10); the chip shuts down at 165 (p12)
T_BOARD_MAX = 80.0   # degC: PETG softens around there, and the board hangs in a printed base (MEC-06)

# what is left of theta_JA once the JEDEC board's own rise is taken out: the step from board to junction
THETA_LOCAL = THETA_JA - 1 / (H_STILL * 2 * JEDEC_AREA)


def solve(currents, h, sink=0.0):
    """Steady state for RMS phase currents per axis. sink = extra W/K carried off by a heat spreader."""
    r_board = 1 / (h * 2 * BOARD_W * BOARD_H + sink)
    tj = [60.0] * len(currents)
    for _ in range(200):
        p = [2 * i * i * RON_25 * (1 + RON_TC * (t - 25)) + P_IDLE for i, t in zip(currents, tj)]
        t_board = T_AIR + (sum(p) + P_LOGIC) * r_board
        new = [t_board + pi * THETA_LOCAL for pi in p]
        if max(abs(a - b) for a, b in zip(new, tj)) < 0.01:
            break
        tj = [min(n, 400.0) for n in new]
    return t_board, max(tj), sum(p) + P_LOGIC


def limit(n_axes, h, sink=0.0):
    """Largest equal current on n axes (the others at 0.3 A) that keeps junction and board inside their limits."""
    best = 0.0
    for step in range(1, 211):
        i = step / 100
        tb, tj, _ = solve([i] * n_axes + [0.3] * (4 - n_axes), h, sink)
        if tj <= T_J_MAX and tb <= T_BOARD_MAX:
            best = i
    return best


if __name__ == "__main__":
    print(f"step from board to junction: {THETA_LOCAL:.1f} K/W; board to air in still air: {1 / (H_STILL * 2 * BOARD_W * BOARD_H):.1f} K/W")
    print(f"air in the base assumed {T_AIR:.0f} degC\n")
    print(f"{'case':46s} {'board':>7s} {'junction':>9s} {'heat':>6s}")
    cases = [("all four at 1.5 A, still air", [1.5] * 4, H_STILL, 0),
             ("all four at 1.0 A, still air", [1.0] * 4, H_STILL, 0),
             ("pan and tilt 1.5 A, zoom and focus 0.4 A", [1.5, 1.5, 0.4, 0.4], H_STILL, 0),
             ("pan and tilt 1.2 A, zoom and focus 0.4 A", [1.2, 1.2, 0.4, 0.4], H_STILL, 0),
             ("pan and tilt 0.6 A hold, zoom and focus 0.2 A", [0.6, 0.6, 0.2, 0.2], H_STILL, 0),
             ("all four at 1.5 A, fan", [1.5] * 4, H_FAN, 0),
             ("all four at 1.5 A, still air, spreader 0.3 W/K", [1.5] * 4, H_STILL, 0.3)]
    for name, cur, h, sink in cases:
        tb, tj, p = solve(cur, h, sink)
        flag = "" if tj <= T_J_MAX and tb <= T_BOARD_MAX else "  over: " + ("junction " if tj > T_J_MAX else "") + ("board" if tb > T_BOARD_MAX else "")
        print(f"{name:46s} {tb:6.0f}C {tj:8.0f}C {p:5.1f}W{flag}")
    print()
    for n in (4, 2):
        print(f"continuous limit, {n} axes equal, still air: {limit(n, H_STILL):.2f} A RMS; with a fan: {limit(n, H_FAN):.2f} A; "
              f"with a 0.3 W/K spreader: {limit(n, H_STILL, 0.3):.2f} A")
    print("\nThe board limit is reached before the junction limit in every still-air case: the housing sets the current, not the chip.")
