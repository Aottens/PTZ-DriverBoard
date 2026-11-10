"""Builds the one-axis test rig (specs/modules/rig.md) in the active, empty Fusion design.

Run inside Fusion: exec this file, then call build(). All sizes in mm, z up, output axis at the origin.
Shows the 7.5:1 set-up with idlers assembled; the 100T for 6.25:1 is in the model but hidden.
The layout keeps to the base limit of 165 mm: the motor sits under the pulley, as in the real head.
print_* components are printed, koop_* are bought parts, modelled only to check fit.
"""
import math

import adsk.core
import adsk.fusion

# --- Belt geometry, from mechanica/belts.py ---
C_625 = 55.6  # 16T-100T, 240 mm belt, no idlers
C_75 = 55.7  # 16T-120T, 270 mm belt, with idlers
IDLERS = [(-12.2, -48.6), (12.2, -48.6)]  # on the belt's back, 7.5:1 only
TENSION = 2.0  # slot travel either way, for belt tension
MOTOR_Y = -(C_625 + C_75) / 2
MOTOR_TRAVEL = TENSION

# --- Height stack ---
PLATE_B = (0.0, 6.0)  # bottom plate
MOTOR_FACE = 3.0  # motor sits in a pocket from below
PLANE = 13.0  # belt plane
PULLEY_H = 11.0
IDLER_Z = (9.0, 17.5)  # two F623 back to back with a 0.5 mm shim between the inner rings, so the 6 mm belt runs free
PLATE_T = (28.0, 34.0)  # top plate, above the motor shaft's tip
STACK_BOTTOM = 7.5  # bottom of the pulley and spacer stack
HEX_END = 8.5  # bottom of the shaft: 1 mm short of the stack, so the bolts can load the bearings despite print errors
SEAT_L = (34.0, 41.0)  # lower bearing
SEAT_U = (74.0, 81.0)  # upper bearing
FLANGE = (82.0, 88.0)
CAMERA_PLATE = (88.0, 100.0)
FOOT_H = 45.0
WEB_D = 39.0  # housing web and top plate hole: touch the bearing's outer ring, not its seal

# --- Fits, adjust to the printer ---
BEARING_FIT = 0.15  # added to bearing seats
HEX_AF = 25.0  # corners must pass through the bearings
SHAFT_D = 29.9  # slides through a 30 mm bearing bore
HEX_FIT = 0.3
M3_CLEAR = 3.4
INSERT = 4.0  # M3 heat-set insert hole

# --- GT2 tooth, simplified for printing ---
PLD = 0.254
GROOVE_W = 0.66  # half width at the outer diameter
GROOVE_D = 0.76

X0, X1, Y0, Y1 = -68.0, 68.0, -88.0, 68.0  # bottom plate
Y0_T, Y1_T = -68.0, 68.0  # top plate
PILLARS = [(-56.0, 56.0), (56.0, 56.0), (56.0, -56.0), (-56.0, -56.0)]  # clear of the pulley and belt
FEET = [(-60.0, -80.0), (60.0, -80.0), (40.0, 60.0), (-40.0, 60.0)]  # clear of the pillar bolts and motor
TRAY_BOLT = 25.0
CAMERA_BOLTS = [(-27.7, -16.0), (27.7, -16.0), (-27.7, 16.0), (27.7, 16.0)]  # from below, heads clear of the housing
SEAT_MARGIN = 0.3  # lower seat deeper than the bearing, for droop of the bridged ring above it


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


def hexagon(af, x=0.0, y=0.0):
    r = af / math.sqrt(3)
    return poly([(x + r * math.cos(math.radians(a)), y + r * math.sin(math.radians(a))) for a in range(0, 360, 60)])


def slot(x, y, d, travel):
    """A hole that can move +-travel along y."""
    return [circle(x, y - travel, d), circle(x, y + travel, d), rect(x, y, d, 2 * travel)]


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


def pulley(root, name, teeth, centre_z):
    # No flange: the 16T and the idlers keep the belt in line, and a smaller radius leaves room for them.
    bottom = centre_z - PULLEY_H / 2
    outline, _ = pulley_outline(teeth)
    p = Part(root, name)
    p.ext(bottom, bottom + PULLEY_H, [outline])
    return p, bottom


def motor_cuts(p, x, y):
    p.ext(PLATE_B[0], MOTOR_FACE, [rect(x, y, 43, 42 + 2 * MOTOR_TRAVEL + 1)], "cut")
    p.ext(MOTOR_FACE, PLATE_B[1], slot(x, y, 23, MOTOR_TRAVEL), "cut")
    for sx in (-15.5, 15.5):
        for sy in (-15.5, 15.5):
            p.ext(MOTOR_FACE, PLATE_B[1], slot(x + sx, y + sy, M3_CLEAR, MOTOR_TRAVEL), "cut")


def bottom_plate(root):
    p = Part(root, "print_bottom_plate")
    p.ext(*PLATE_B, [rect((X0 + X1) / 2, (Y0 + Y1) / 2, X1 - X0, Y1 - Y0)])
    p.ext(*PLATE_B, [circle(0, 0, 44)], "cut")
    motor_cuts(p, 0.0, MOTOR_Y)
    p.ext(*PLATE_B, [circle(x, y, M3_CLEAR) for x, y in PILLARS + FEET], "cut")
    p.ext(PLATE_B[0], 5.0, [circle(sx, sy, INSERT) for sx in (-TRAY_BOLT, TRAY_BOLT) for sy in (-TRAY_BOLT, TRAY_BOLT)], "cut")
    p.ext(MOTOR_FACE, PLATE_B[1], [circle(x, y, M3_CLEAR) for x, y in IDLERS], "cut")  # room for the idler bolts' tips
    return p


def top_plate(root):
    p = Part(root, "print_top_plate")
    p.ext(*PLATE_T, [rect((X0 + X1) / 2, (Y0_T + Y1_T) / 2, X1 - X0, Y1_T - Y0_T)])
    p.ext(*PLATE_T, [circle(0, 0, WEB_D)], "cut")
    p.ext(*PLATE_T, [circle(x, y, M3_CLEAR) for x, y in PILLARS + IDLERS] + ring(36, M3_CLEAR, 4, 45), "cut")
    p.ext(*PLATE_T, slot(0.0, MOTOR_Y, 20, MOTOR_TRAVEL), "cut")  # lets a belt rise over the motor shaft's tip
    for sx in (-15.5, 15.5):
        p.ext(*PLATE_T, slot(sx, MOTOR_Y + 15.5, 7, MOTOR_TRAVEL), "cut")  # hex key to the motor's inner bolts
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


def housing(root):
    p = Part(root, "print_bearing_housing")
    p.ext(SEAT_L[0], SEAT_U[1], [circle(0, 0, 56)])
    p.ext(SEAT_L[0], SEAT_L[0] + 6, [circle(0, 0, 80)], "join")  # small enough to leave the motor's inner bolts reachable
    # End stop (RIG-04): the shaft's tab hits this rib, for about +-171 degrees.
    p.ext(SEAT_L[0] + 6, 78.0, [rect(0, 30.5, 4, 9)], "join")
    p.ext(SEAT_L[0], SEAT_U[1], [circle(0, 0, WEB_D)], "cut")
    p.ext(SEAT_L[0], SEAT_L[1] + SEAT_MARGIN, [circle(0, 0, 42 + BEARING_FIT)], "cut")
    p.ext(SEAT_L[0], SEAT_L[0] + 0.3, [circle(0, 0, 42.75)], "cut")  # entry step against elephant foot
    p.ext(*SEAT_U, [circle(0, 0, 42 + BEARING_FIT)], "cut")
    p.ext(SEAT_L[0], SEAT_L[0] + 5, ring(36, INSERT, 4, 45), "cut")
    return p


def shaft(root):
    p = Part(root, "print_output_shaft")
    p.ext(HEX_END, SEAT_L[0], [hexagon(HEX_AF)])
    p.ext(SEAT_L[0], SEAT_U[1], [circle(0, 0, SHAFT_D)], "join")
    p.ext(SEAT_U[1], FLANGE[0], [circle(0, 0, 33)], "join")
    p.ext(*FLANGE, [circle(0, 0, 76)], "join")
    p.ext(74.0, FLANGE[0], [rect(0, -33, 6, 4)], "join")  # end-stop tab, above the rib's top at its bolt heads
    p.ext(*FLANGE, [circle(x, y, M3_CLEAR) for x, y in CAMERA_BOLTS], "cut")
    p.ext(HEX_END, HEX_END + 6, ring(10, INSERT, 3), "cut")
    return p


def magnet_holder(root):
    p = Part(root, "print_magnet_holder")
    p.ext(3.5, STACK_BOTTOM, [circle(0, 0, 40)])
    p.ext(3.5, 6.0, [circle(0, 0, 6.1)], "cut")
    p.ext(3.5, STACK_BOTTOM, ring(10, M3_CLEAR, 3), "cut")
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
    p.ext(CAMERA_PLATE[0], CAMERA_PLATE[0] + 7, [rect(0, 0, 120, 14)], "cut")  # room for the camera bolt's head
    # Bolts from below, so the camera can stay on the plate: tighten it first, then fit the plate.
    p.ext(CAMERA_PLATE[0], CAMERA_PLATE[0] + 6, [circle(x, y, INSERT) for x, y in CAMERA_BOLTS], "cut")
    return p


def sensor_tray(root):
    p = Part(root, "print_sensor_tray")
    p.ext(-8, -5, [rect(0, 0, 60, 60)])
    p.ext(-5, -1, [circle(0, 0, 30)], "join")
    corners = [(sx, sy) for sx in (-TRAY_BOLT, TRAY_BOLT) for sy in (-TRAY_BOLT, TRAY_BOLT)]
    p.ext(-5, 0, [circle(x, y, 8) for x, y in corners], "join")  # legs up to the plate; shims under them set the magnet gap
    p.ext(-8, 0, [circle(x, y, M3_CLEAR) for x, y in corners], "cut")
    return p


def idler_parts(root):
    x, y = IDLERS[0]
    # Each spacer touches the bearing's inner ring only, through a small boss, or the idler would not turn.
    top = Part(root, "print_idler_spacer_top")
    top.ext(IDLER_Z[1] + 0.4, PLATE_T[0], [circle(x, y, 8)])
    top.ext(IDLER_Z[1], IDLER_Z[1] + 0.4, [circle(x, y, 4.8)], "join")
    top.ext(IDLER_Z[1], PLATE_T[0], [circle(x, y, M3_CLEAR)], "cut")
    low = Part(root, "print_idler_spacer_low")
    low.ext(PLATE_B[1], IDLER_Z[0] - 0.4, [circle(x, y, 8.5)])
    low.ext(IDLER_Z[0] - 0.4, IDLER_Z[0], [circle(x, y, 4.8)], "join")
    low.ext(PLATE_B[1], IDLER_Z[0], [circle(x, y, M3_CLEAR)], "cut")
    low.ext(PLATE_B[1], PLATE_B[1] + 1.9, [hexagon(5.7, x, y)], "cut")  # thin M3 nut (DIN 439), held by the plate under it
    bearing = Part(root, "koop_idler_2xF623")
    bearing.ext(*IDLER_Z, [circle(x, y, 10)])
    bearing.ext(*IDLER_Z, [circle(x, y, 3)], "cut")
    for part in (top, low, bearing):
        copies(root, part, IDLERS[0], IDLERS[1:])


def fit_test(root):
    """Small prints to try the bearing seat and the shaft before printing the large parts. Not in the assembly."""
    x = 150.0
    seat = Part(root, "print_fit_seat")
    # Same as the housing's lower seat: opens onto the bed, with the bridged ring above it.
    seat.ext(0, 9, [circle(x, 0, 48)])
    seat.ext(0, 9, [circle(x, 0, WEB_D)], "cut")
    seat.ext(0, 7 + SEAT_MARGIN, [circle(x, 0, 42 + BEARING_FIT)], "cut")
    seat.ext(0, 0.3, [circle(x, 0, 42.75)], "cut")
    stub = Part(root, "print_fit_shaft")
    stub.ext(0, 8, [circle(x, 60, SHAFT_D)])
    stub.ext(8, 16, [hexagon(HEX_AF, x, 60)], "join")
    for part in (seat, stub):
        part.occ.isLightBulbOn = False


def bought_parts(root):
    y = -C_75
    m = Part(root, "koop_motor_17HE15")
    m.ext(MOTOR_FACE - 38, MOTOR_FACE, [rect(0, y, 42, 42)])
    m.ext(MOTOR_FACE, MOTOR_FACE + 2, [circle(0, y, 22)], "join")
    m.ext(MOTOR_FACE + 2, MOTOR_FACE + 23.5, [circle(0, y, 5)], "join")
    pm = Part(root, "koop_pulley_16T_5mm")
    pm.ext(PLANE - 4.5, PLANE + 11.5, [circle(0, y, 12)])
    pm.ext(PLANE - 4.5, PLANE + 11.5, [circle(0, y, 5)], "cut")
    for name, z0 in (("koop_6806_lower", SEAT_L[0]), ("koop_6806_upper", SEAT_U[0])):
        b = Part(root, name)
        b.ext(z0, z0 + 7, [circle(0, 0, 42)])
        b.ext(z0, z0 + 7, [circle(0, 0, 30)], "cut")
    g = Part(root, "koop_magnet_D6x2.5")
    g.ext(3.5, 6.0, [circle(0, 0, 6)])


def build():
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    root = design.rootComponent
    assert root.occurrences.count == 0 and root.bRepBodies.count == 0, "needs an empty design"
    assert HEX_AF * 2 / math.sqrt(3) < SHAFT_D - 0.5, "the hexagon's corners must pass through the bearings"
    design.designIntent = adsk.fusion.DesignIntentTypes.HybridDesignIntentType  # a Part design allows one component

    bottom_plate(root)
    top_plate(root)
    pillar = tube(root, "print_pillar", *PILLARS[0], PLATE_B[1], PLATE_T[0], ("bottom", "top"))
    copies(root, pillar, PILLARS[0], PILLARS[1:])
    foot = tube(root, "print_foot", *FEET[0], -FOOT_H, 0.0, ("top",))
    copies(root, foot, FEET[0], FEET[1:])
    housing(root)
    shaft(root)
    magnet_holder(root)
    camera_plate(root)
    sensor_tray(root)
    spacer(root, "print_spacer", STACK_BOTTOM + PULLEY_H, SEAT_L[0])

    for teeth, shown in ((120, True), (100, False)):
        p, bottom = pulley(root, f"print_pulley_{teeth}T", teeth, PLANE)
        p.ext(bottom, bottom + PULLEY_H, [hexagon(HEX_AF + HEX_FIT)], "cut")
        p.occ.isLightBulbOn = shown

    idler_parts(root)
    fit_test(root)
    bought_parts(root)
    print("occurrences", root.allOccurrences.count, "timeline", design.timeline.count)
