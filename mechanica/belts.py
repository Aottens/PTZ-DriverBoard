#!/usr/bin/env python3
"""GT2 belt geometry for the rig (specs/modules/rig.md). Run: python3 mechanica/belts.py"""
import math


# 6 teeth is the usual aim. A 16T on a 200T only reaches it with a 550 mm belt, which no longer fits
# the printer's bed, so the rig accepts a little less at its low load and tests it.
MIN_MESH = 5.5


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


if __name__ == "__main__":
    # Known case: equal pulleys, the belt is two spans plus one pulley circumference.
    assert abs(belt_length(50, 20, 20) - (100 + 40)) < 1e-9
    assert abs(center_distance(belt_length(70, 16, 80), 16, 80) - 70) < 1e-6
    for name, z1, z2, length in (("9:1", 16, 144, 400), ("12.5:1", 16, 200, 500)):
        c = center_distance(length, z1, z2)
        mesh = teeth_in_mesh(c, z1, z2)
        assert mesh >= MIN_MESH, f"{name}: only {mesh:.1f} teeth in mesh"
        print(f"{name}: {z1}T-{z2}T, belt {length} mm, C = {c:.1f} mm, {mesh:.1f} teeth in mesh")
