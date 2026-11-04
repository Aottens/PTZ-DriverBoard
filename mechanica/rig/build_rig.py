"""Builds the one-axis test rig (specs/modules/rig.md) in the active, empty Fusion design.

Run inside Fusion: exec this file, then call build(). All sizes in mm, z up, output axis at the origin.
Shows the 30:1 set-up assembled; the 9:1 parts are in the model but hidden.
print_* components are printed, koop_* are bought parts, modelled only to check fit.
"""
import math

import adsk.core
import adsk.fusion

# --- Belt geometry, from mechanica/belts.py ---
C_A = 69.0  # motor to middle shaft, 240 mm belt
C_B = 79.9  # middle shaft to output, 280 mm belt
C_9 = 112.6  # 9:1 motor to output, 400 mm belt
MIDDLE = (-C_B, 0.0)
MOTOR_30 = (-C_B, -C_A)
MOTOR_9 = (0.0, -C_9)
TRAVEL = 4.0  # slot travel either way, for belt tension

# --- Height stack ---
PLATE_B = (0.0, 6.0)  # bottom plate
MOTOR_FACE = 3.0  # motor sits in a pocket from below
PLANE_A = 13.0  # belt plane A
PULLEY_H = 11.0
PLANE_B = 36.5  # belt plane B
PLATE_T = (45.0, 51.0)  # top plate
HEX_END = 7.5  # bottom of the output shaft
S_MID_END = 31.0  # top of the middle spacer, bottom of the 96T
SEAT_L = (51.0, 58.0)  # lower bearing
SEAT_U = (91.0, 98.0)  # upper bearing
FLANGE = (99.0, 105.0)
CAMERA_PLATE = (105.0, 117.0)
FOOT_H = 45.0

# --- Fits, adjust to the printer ---
BEARING_FIT = 0.15  # added to bearing seats
HEX_AF = 26.0
HEX_FIT = 0.3
M3_CLEAR = 3.4
INSERT = 4.0  # M3 heat-set insert hole
PIN_R = 8.0

# --- GT2 tooth, simplified for printing ---
PLD = 0.254
GROOVE_W = 0.66  # half width at the outer diameter
GROOVE_D = 0.76
FLANGE_T = 1.5
FLANGE_OVER = 1.75

X0, X1, Y0, Y1 = -122.0, 58.0, -145.0, 58.0  # bottom plate
Y0_T, Y1_T = -58.0, 58.0  # top plate
PILLARS = [(-107.0, 50.0), (50.0, 50.0), (50.0, -50.0), (-107.0, -50.0)]
FEET = [(-107.0, -137.0), (50.0, -137.0), (20.0, 50.0), (-60.0, 50.0)]
HOLDER_BOLT = 32.0
TRAY_BOLT = 25.0


def cm(v):
    return v / 10.0


class Part:
    def __init__(self, root, name):
        self.occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        self.comp = self.occ.component
        self.comp.name = name

    def _sketch(self, z):
        planes = self.comp.constructionPlanes
        pi = planes.createInput()
        pi.setByOffset(self.comp.xYConstructionPlane, adsk.core.ValueInput.createByReal(cm(z)))
        return self.comp.sketches.add(planes.add(pi))

    def _extrude(self, profiles, distance, op):
        ext = self.comp.features.extrudeFeatures
        inp = ext.createInput(profiles, op)
        inp.setDistanceExtent(False, adsk.core.ValueInput.createByReal(cm(distance)))
        if op != adsk.fusion.FeatureOperations.NewBodyFeatureOperation:
            # Without this a cut or join also reaches the other components' bodies.
            inp.participantBodies = list(self.comp.bRepBodies)
        return ext.add(inp)

    def ext(self, z0, z1, shapes, op="new"):
        """shapes draw on a sketch at z0; every profile is extruded up to z1."""
        sk = self._sketch(z0)
        sk.isComputeDeferred = True
        for shape in shapes:
            shape(sk)
        sk.isComputeDeferred = False
        col = adsk.core.ObjectCollection.create()
        for p in sk.profiles:
            col.add(p)
        ops = {"new": adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
               "join": adsk.fusion.FeatureOperations.JoinFeatureOperation,
               "cut": adsk.fusion.FeatureOperations.CutFeatureOperation}
        self._extrude(col, z1 - z0, ops[op])
        return self

    def radial_hole(self, z, d, length):
        sk = self.comp.sketches.add(self.comp.yZConstructionPlane)
        c = sk.modelToSketchSpace(adsk.core.Point3D.create(0, 0, cm(z)))
        sk.sketchCurves.sketchCircles.addByCenterRadius(c, cm(d / 2))
        col = adsk.core.ObjectCollection.create()
        col.add(sk.profiles.item(0))
        self._extrude(col, length, adsk.fusion.FeatureOperations.CutFeatureOperation)
        return self


def pt(x, y):
    return adsk.core.Point3D.create(cm(x), cm(y), 0)


def circle(x, y, d):
    return lambda sk: sk.sketchCurves.sketchCircles.addByCenterRadius(pt(x, y), cm(d / 2))


def rect(cx, cy, w, h):
    return lambda sk: sk.sketchCurves.sketchLines.addTwoPointRectangle(pt(cx - w / 2, cy - h / 2), pt(cx + w / 2, cy + h / 2))


def poly(points):
    def draw(sk):
        lines = sk.sketchCurves.sketchLines
        first = lines.addByTwoPoints(pt(*points[0]), pt(*points[1]))
        last = first
        for p in points[2:]:
            last = lines.addByTwoPoints(last.endSketchPoint, pt(*p))
        lines.addByTwoPoints(last.endSketchPoint, first.startSketchPoint)
    return draw


def hexagon(af):
    r = af / math.sqrt(3)
    return poly([(r * math.cos(math.radians(a)), r * math.sin(math.radians(a))) for a in range(0, 360, 60)])


def slot(x, y, d, along):
    """A hole that can move +-TRAVEL along 'x' or 'y'."""
    dx, dy = (TRAVEL, 0) if along == "x" else (0, TRAVEL)
    w, h = (2 * TRAVEL, d) if along == "x" else (d, 2 * TRAVEL)
    return [circle(x - dx, y - dy, d), circle(x + dx, y + dy, d), rect(x, y, w, h)]


def ring(radius, d, count, start=0.0):
    return [circle(radius * math.cos(math.radians(start + i * 360 / count)), radius * math.sin(math.radians(start + i * 360 / count)), d)
            for i in range(count)]


def pulley_outline(teeth):
    pitch_r = teeth * 2 / math.pi / 2
    outer = pitch_r - PLD
    pts = []
    for k in range(teeth):
        centre = 2 * math.pi * k / teeth
        for t in (-1.0, -0.7, -0.35, 0.0, 0.35, 0.7, 1.0):
            depth = GROOVE_D * math.sqrt(max(0.0, 1 - t * t))
            r, a = outer - depth, centre + GROOVE_W * t / outer
            pts.append((r * math.cos(a), r * math.sin(a)))
    return poly(pts), outer


def pulley(root, name, teeth, centre_z, bore):
    bottom = centre_z - PULLEY_H / 2
    outline, outer = pulley_outline(teeth)
    p = Part(root, name)
    p.ext(bottom + FLANGE_T, bottom + PULLEY_H, [outline])
    p.ext(bottom, bottom + FLANGE_T, [circle(0, 0, 2 * (outer + FLANGE_OVER))], "join")
    return p, bottom


def motor_cuts(p, x, y):
    p.ext(PLATE_B[0], MOTOR_FACE, [rect(x, y, 43, 42 + 2 * TRAVEL + 1)], "cut")
    p.ext(MOTOR_FACE, PLATE_B[1], slot(x, y, 23, "y"), "cut")
    for sx in (-15.5, 15.5):
        for sy in (-15.5, 15.5):
            p.ext(MOTOR_FACE, PLATE_B[1], slot(x + sx, y + sy, M3_CLEAR, "y"), "cut")


def middle_cuts(p, z0, z1, bolts):
    x, y = MIDDLE
    p.ext(z0, z1, slot(x, y, 12, "x"), "cut")
    for dx, dy in bolts:
        p.ext(z0, z1, slot(x + dx, y + dy, M3_CLEAR, "x"), "cut")


def bottom_plate(root):
    p = Part(root, "print_bottom_plate")
    p.ext(*PLATE_B, [rect((X0 + X1) / 2, (Y0 + Y1) / 2, X1 - X0, Y1 - Y0)])
    p.ext(*PLATE_B, [circle(0, 0, 44)], "cut")
    motor_cuts(p, *MOTOR_30)
    motor_cuts(p, *MOTOR_9)
    middle_cuts(p, *PLATE_B, [(-HOLDER_BOLT, 0), (HOLDER_BOLT, 0)])
    p.ext(*PLATE_B, [circle(x, y, M3_CLEAR) for x, y in PILLARS + FEET], "cut")
    p.ext(PLATE_B[0], 5.0, [circle(sx, sy, INSERT) for sx in (-TRAY_BOLT, TRAY_BOLT) for sy in (-TRAY_BOLT, TRAY_BOLT)], "cut")
    return p


def top_plate(root):
    p = Part(root, "print_top_plate")
    p.ext(*PLATE_T, [rect((X0 + X1) / 2, (Y0_T + Y1_T) / 2, X1 - X0, Y1_T - Y0_T)])
    p.ext(*PLATE_T, [circle(0, 0, 38)], "cut")
    # Holder turned a quarter here, along y: along x it would hit the housing flange.
    middle_cuts(p, *PLATE_T, [(0, -HOLDER_BOLT), (0, HOLDER_BOLT)])
    p.ext(*PLATE_T, [circle(x, y, M3_CLEAR) for x, y in PILLARS] + ring(36, M3_CLEAR, 4, 45), "cut")
    return p


def copies(root, part, first, others):
    for x, y in others:
        m = adsk.core.Matrix3D.create()
        m.translation = adsk.core.Vector3D.create(cm(x - first[0]), cm(y - first[1]), 0)
        root.occurrences.addExistingComponent(part.comp, m)


def tube(root, name, x, y, z0, z1, ends):
    p = Part(root, name)
    p.ext(z0, z1, [circle(x, y, 16)])
    if "bottom" in ends:
        p.ext(z0, z0 + 6, [circle(x, y, INSERT)], "cut")
    if "top" in ends:
        p.ext(z1 - 6, z1, [circle(x, y, INSERT)], "cut")
    return p


def holder(root):
    x, y = MIDDLE
    p = Part(root, "print_bearing_holder")
    p.ext(-9, 0, [rect(x, y, 2 * HOLDER_BOLT + 12, 24)])
    p.ext(-7, 0, [circle(x, y, 22 + BEARING_FIT)], "cut")
    p.ext(-9, -7, [circle(x, y, 12)], "cut")
    p.ext(-6, 0, [circle(x - HOLDER_BOLT, y, INSERT), circle(x + HOLDER_BOLT, y, INSERT)], "cut")
    m = adsk.core.Matrix3D.create()
    # Second holder on top of the top plate, flipped: z -> PLATE_T[1] - z
    m.setToRotation(math.pi, adsk.core.Vector3D.create(1, 0, 0), adsk.core.Point3D.create(0, 0, cm(PLATE_T[1] / 2)))
    quarter = adsk.core.Matrix3D.create()
    quarter.setToRotation(math.pi / 2, adsk.core.Vector3D.create(0, 0, 1), adsk.core.Point3D.create(cm(x), cm(y), 0))
    m.transformBy(quarter)
    root.occurrences.addExistingComponent(p.comp, m)
    return p


def housing(root):
    p = Part(root, "print_bearing_housing")
    p.ext(SEAT_L[0], SEAT_U[1], [circle(0, 0, 56)])
    p.ext(SEAT_L[0], SEAT_L[0] + 6, [circle(0, 0, 90)], "join")
    p.ext(SEAT_L[0], SEAT_U[1], [circle(0, 0, 38)], "cut")
    p.ext(*SEAT_L, [circle(0, 0, 42 + BEARING_FIT)], "cut")
    p.ext(*SEAT_U, [circle(0, 0, 42 + BEARING_FIT)], "cut")
    p.ext(SEAT_L[0], SEAT_L[0] + 5, ring(36, INSERT, 4, 45), "cut")
    return p


def shaft(root):
    p = Part(root, "print_output_shaft")
    p.ext(HEX_END, SEAT_L[0], [hexagon(HEX_AF)])
    p.ext(SEAT_L[0], SEAT_U[1], [circle(0, 0, 30)], "join")
    p.ext(SEAT_U[1], FLANGE[0], [circle(0, 0, 33)], "join")
    p.ext(*FLANGE, [circle(0, 0, 70)], "join")
    p.ext(*FLANGE, ring(27, M3_CLEAR, 6, 30), "cut")
    p.ext(HEX_END, HEX_END + 6, ring(10, INSERT, 3), "cut")
    return p


def magnet_holder(root):
    p = Part(root, "print_magnet_holder")
    p.ext(3.5, HEX_END, [circle(0, 0, 40)])
    p.ext(3.5, 6.0, [circle(0, 0, 6.1)], "cut")
    p.ext(3.5, HEX_END, ring(10, M3_CLEAR, 3), "cut")
    p.ext(3.5, 5.5, ring(10, 6, 3), "cut")
    return p


def spacer(root, name, z0, z1):
    p = Part(root, name)
    p.ext(z0, z1, [circle(0, 0, 33)])
    p.ext(z0, z1, [hexagon(HEX_AF + HEX_FIT)], "cut")
    return p


def camera_plate(root):
    p = Part(root, "print_camera_plate")
    p.ext(*CAMERA_PLATE, [rect(0, 0, 120, 70)])
    p.ext(*CAMERA_PLATE, [circle(-30, 0, 6.8), circle(30, 0, 6.8), rect(0, 0, 60, 6.8)], "cut")
    p.ext(CAMERA_PLATE[0], CAMERA_PLATE[0] + 5, [rect(0, 0, 120, 14)], "cut")
    p.ext(CAMERA_PLATE[0], CAMERA_PLATE[0] + 6, ring(27, INSERT, 6, 30), "cut")
    return p


def sensor_tray(root):
    p = Part(root, "print_sensor_tray")
    p.ext(-8, -5, [rect(0, 0, 60, 60)])
    p.ext(-5, -1, [circle(0, 0, 30)], "join")
    p.ext(-8, -5, [circle(sx, sy, M3_CLEAR) for sx in (-TRAY_BOLT, TRAY_BOLT) for sy in (-TRAY_BOLT, TRAY_BOLT)], "cut")
    return p


def bought_parts(root):
    x, y = MOTOR_30
    m = Part(root, "koop_motor_17HE08")
    m.ext(MOTOR_FACE - 23, MOTOR_FACE, [rect(x, y, 42, 42)])
    m.ext(MOTOR_FACE, MOTOR_FACE + 2, [circle(x, y, 22)], "join")
    m.ext(MOTOR_FACE + 2, MOTOR_FACE + 20, [circle(x, y, 5)], "join")
    pm = Part(root, "koop_pulley_16T_5mm")
    pm.ext(PLANE_A - 4.5, PLANE_A + 11.5, [circle(x, y, 12)])
    pm.ext(PLANE_A - 4.5, PLANE_A + 11.5, [circle(x, y, 5)], "cut")
    mx, my = MIDDLE
    s = Part(root, "koop_shaft_8mm")
    s.ext(-8, 59, [circle(mx, my, 8)])
    pb = Part(root, "koop_pulley_16T_8mm")
    pb.ext(PLANE_B - 11.5, PLANE_B + 4.5, [circle(mx, my, 13)])
    pb.ext(PLANE_B - 11.5, PLANE_B + 4.5, [circle(mx, my, 8)], "cut")
    for name, z0 in (("koop_6806_lower", SEAT_L[0]), ("koop_6806_upper", SEAT_U[0])):
        b = Part(root, name)
        b.ext(z0, z0 + 7, [circle(0, 0, 42)])
        b.ext(z0, z0 + 7, [circle(0, 0, 30)], "cut")
    for name, z0 in (("koop_608_lower", -7.0), ("koop_608_upper", PLATE_T[1])):
        b = Part(root, name)
        b.ext(z0, z0 + 7, [circle(mx, my, 22)])
        b.ext(z0, z0 + 7, [circle(mx, my, 8)], "cut")
    g = Part(root, "koop_magnet_D6x2.5")
    g.ext(3.5, 6.0, [circle(0, 0, 6)])


def build():
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    root = design.rootComponent
    assert root.occurrences.count == 0 and root.bRepBodies.count == 0, "needs an empty design"
    design.designIntent = adsk.fusion.DesignIntentTypes.HybridDesignIntentType  # a Part design allows one component

    bottom_plate(root)
    top_plate(root)
    pillar = tube(root, "print_pillar", *PILLARS[0], PLATE_B[1], PLATE_T[0], ("bottom", "top"))
    copies(root, pillar, PILLARS[0], PILLARS[1:])
    foot = tube(root, "print_foot", *FEET[0], -FOOT_H, 0.0, ("top",))
    copies(root, foot, FEET[0], FEET[1:])
    holder(root)
    housing(root)
    shaft(root)
    magnet_holder(root)
    camera_plate(root)
    sensor_tray(root)

    # Spacers: the 9:1 set-up swaps 11 mm spacer and 96T for 144T and the same spacer one level up.
    spacer(root, "print_spacer_11", HEX_END, HEX_END + PULLEY_H)
    spacer(root, "print_spacer_12_5", HEX_END + PULLEY_H, S_MID_END)
    spacer(root, "print_spacer_9", S_MID_END + PULLEY_H, SEAT_L[0])

    p96, b96 = pulley(root, "print_pulley_96T", 96, PLANE_B, "hex")
    p96.ext(b96, b96 + PULLEY_H, [hexagon(HEX_AF + HEX_FIT)], "cut")
    p144, b144 = pulley(root, "print_pulley_144T", 144, PLANE_A, "hex")
    p144.ext(b144, b144 + PULLEY_H, [hexagon(HEX_AF + HEX_FIT)], "cut")
    p144.occ.isLightBulbOn = False

    p80, b80 = pulley(root, "print_pulley_80T", 80, PLANE_A, "round")
    p80.ext(b80 + PULLEY_H, b80 + PULLEY_H + 6, [circle(0, 0, 20)], "join")
    p80.ext(b80, b80 + PULLEY_H + 6, [circle(0, 0, 8.2)], "cut")
    p80.radial_hole(b80 + PULLEY_H + 3, INSERT, 15)
    m = adsk.core.Matrix3D.create()
    m.translation = adsk.core.Vector3D.create(cm(MIDDLE[0]), cm(MIDDLE[1]), 0)
    p80.occ.transform = m
    design.snapshots.add()

    bought_parts(root)
    print("occurrences", root.allOccurrences.count, "timeline", design.timeline.count)
