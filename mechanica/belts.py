#!/usr/bin/env python3
"""GT2 belt geometry for the rig and the head (specs/modules/rig.md). Run: python3 mechanica/belts.py"""
import math

# Tooth counts at the 16T. 6 is the usual aim; the base limit of 165 mm leaves less without idlers,
# so the rig accepts 5 at its low load and tests it.
MIN_MESH = 5.0
BASE_D = 165.0  # owner's limit for the base
WALL = 3.0
MOTOR_HALF = 21.0  # NEMA 17
PULLEY_FLANGE_R = 7.0  # 16T flange, estimated until measured
IDLER_FLANGE_R = 5.75  # F623, flange 11.5 mm
IDLER_PITCH_R = 5.35  # bearing radius 5 plus about the belt's back to pitch line


def pitch_d(teeth):
    return teeth * 2 / math.pi  # GT2: 2 mm per tooth


def belt_length(c, z1, z2):
    d1, d2 = pitch_d(z1), pitch_d(z2)
    return 2 * c + math.pi * (d1 + d2) / 2 + (d2 - d1) ** 2 / (4 * c)


def center_distance(length, z1, z2):
    lo, hi = (pitch_d(z2) - pitch_d(z1)) / 2 + 1, length
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if belt_length(mid, z1, z2) < length else (lo, mid)
    return mid


def teeth_in_mesh(c, z1, z2):
    return (180 - math.degrees((pitch_d(z2) - pitch_d(z1)) / c)) / 360 * z1


def _tangent(c1, rho1, c2, rho2):
    """Direction and length of the belt span from circle 1 to 2. rho > 0 runs counter-clockwise."""
    dx, dy = c2[0] - c1[0], c2[1] - c1[1]
    dist = math.hypot(dx, dy)
    tilt = math.asin((rho2 - rho1) / dist)
    return math.atan2(dy, dx) - tilt, dist * math.cos(tilt)


def belt_with_idlers(z1, z2, c, ix, iy, idler_r=IDLER_PITCH_R):
    """Length and small-pulley wrap (degrees) with the large pulley at the origin, the small one at
    (0, -c) and idlers on the belt's back at (+-ix, iy)."""
    circles = [((0, 0), pitch_d(z2) / 2, 1), ((-ix, iy), idler_r, -1), ((0, -c), pitch_d(z1) / 2, 1), ((ix, iy), idler_r, -1)]
    spans = [_tangent(circles[i][0], circles[i][1] * circles[i][2], circles[(i + 1) % 4][0], circles[(i + 1) % 4][1] * circles[(i + 1) % 4][2]) for i in range(4)]
    total = sum(s[1] for s in spans)
    wraps = []
    for i in range(4):
        angle = (circles[i][2] * (spans[i][0] - spans[i - 1][0])) % (2 * math.pi)
        wraps.append(angle)
        total += circles[i][1] * angle
    return total, math.degrees(wraps[2])


def base_diameter(c, z2):
    """Round base around the pan axis, with the motor under the pulley."""
    return 2 * (max(pitch_d(z2) / 2 + 2, math.hypot(c + MOTOR_HALF, MOTOR_HALF)) + WALL)


if __name__ == "__main__":
    # Known cases: equal pulleys are two spans plus one circumference, and a vanishing idler on the
    # straight span changes nothing.
    assert abs(belt_length(50, 20, 20) - (100 + 40)) < 1e-9
    assert abs(center_distance(belt_length(70, 16, 80), 16, 80) - 70) < 1e-6
    r = pitch_d(20) / 2
    assert abs(belt_with_idlers(20, 20, 50, r, -25, 1e-6)[0] - belt_length(50, 20, 20)) < 1e-3

    c = center_distance(240, 16, 100)
    mesh = teeth_in_mesh(c, 16, 100)
    print(f"6.25:1, no idlers: 16T-100T, belt 240 mm, C = {c:.1f} mm, {mesh:.1f} teeth in mesh, base {base_diameter(c, 100):.0f} mm")
    assert mesh >= MIN_MESH and base_diameter(c, 100) <= BASE_D + 0.5

    c, ix, iy = 55.7, 12.2, -48.6
    length, wrap = belt_with_idlers(16, 120, c, ix, iy)
    print(f"7.5:1, idlers at +-{ix}, {iy}: 16T-120T, belt {length:.1f} mm, C = {c} mm, {wrap / 360 * 16:.1f} teeth in mesh, base {base_diameter(c, 120):.0f} mm")
    print(f"  clearance: idler to 120T {math.hypot(ix, iy) - pitch_d(120) / 2 - IDLER_FLANGE_R:.1f} mm, to 16T flange {math.hypot(ix, iy + c) - PULLEY_FLANGE_R - IDLER_FLANGE_R:.1f} mm")
    assert wrap / 360 * 16 >= 6 and base_diameter(c, 120) <= BASE_D + 0.5
