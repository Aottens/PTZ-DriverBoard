"""Write KiCad 10 schematics from a circuit described in Python.

Every pin gets a short wire stub and a global label, so a net is its name and nothing depends on drawn wires.
UUIDs are derived from sheet and reference, so regenerating keeps the links to the board.

The circuit itself lives in circuit.py; this file only knows how to draw.
"""
import copy
import math
import os
import uuid

from sexp import Q, dump, find, find_all, parse

KICAD_SYMBOLS = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols"
NS = uuid.UUID("7d1c4c0e-5a39-4b7e-9d0f-70747a2d7265")
G = 2.54  # schematic grid, mm


def uid(*parts):
    return Q(str(uuid.uuid5(NS, "/".join(str(p) for p in parts))))


def font(size=1.27, justify=None, hide=False):
    e = ["effects", ["font", ["size", size, size]]]
    if justify:
        e.append(["justify"] + justify.split())
    if hide:
        e.append(["hide", "yes"])
    return e


# ---------------------------------------------------------------- symbols

class Symbol:
    """A library symbol: its node for lib_symbols and its pins as {number: (name, x, y, angle, etype)}."""

    def __init__(self, lib_id, node):
        self.lib_id, self.node = lib_id, node
        self.pins = {}
        for sub in find_all(node, "symbol"):
            for p in find_all(sub, "pin"):
                at = find(p, "at")
                self.pins[str(find(p, "number")[1])] = (
                    str(find(p, "name")[1]), float(at[1]), float(at[2]), float(at[3]) if len(at) > 3 else 0.0, p[1])
        xs = [v[1] for v in self.pins.values()] or [0]
        ys = [v[2] for v in self.pins.values()] or [0]
        self.box = (min(xs), min(ys), max(xs), max(ys))

    def numbers(self, name):
        return [n for n, v in self.pins.items() if v[0] == name]


_libs = {}


def kicad_symbol(lib_id):
    """Copy a symbol out of KiCad's own libraries, flattening `extends`."""
    lib, name = lib_id.split(":")
    if lib not in _libs:
        _libs[lib] = {s[1]: s for s in find_all(parse(open(f"{KICAD_SYMBOLS}/{lib}.kicad_sym").read()), "symbol")}
    node = copy.deepcopy(_libs[lib][name])
    ext = find(node, "extends")
    if ext:
        child, node = node, copy.deepcopy(_libs[lib][ext[1]])
        for sub in find_all(node, "symbol"):
            sub[1] = Q(sub[1].replace(ext[1], name, 1))
        for prop in find_all(child, "property"):
            old = [p for p in find_all(node, "property") if p[1] == prop[1]]
            if old:
                node[node.index(old[0])] = prop
            else:
                node.insert(2, prop)
    node[1] = Q(lib_id)
    return Symbol(lib_id, node)


def make_symbol(lib_id, left, right, ref="U", width=None):
    """A rectangle with pins left and right. Each pin: (number, name, etype) or None for a gap.

    etype is KiCad's: input output bidirectional tri_state passive power_in power_out open_collector no_connect.
    """
    name = lib_id.split(":")[1]
    rows = max(len(left), len(right))
    longest = max([len(p[1]) for p in left + right if p] + [4])
    w = width or G * max(4, 2 * math.ceil((longest * 2 * 1.0 + 6) / (2 * G)))
    h = G * (rows + 1)
    top = G * ((rows - 1) // 2)  # pins sit on the 2.54 grid
    body = ["symbol", Q(f"{name}_0_1"),
            ["rectangle", ["start", -w / 2, top + G], ["end", w / 2, top - G * rows],
             ["stroke", ["width", 0.254], ["type", "default"]], ["fill", ["type", "background"]]]]
    pins = ["symbol", Q(f"{name}_1_1")]
    for side, plist in ((-1, left), (1, right)):
        for i, p in enumerate(plist):
            if not p:
                continue
            num, pname, etype = p
            pins.append(["pin", etype, "line", ["at", side * (w / 2 + G), top - G * i, 0 if side < 0 else 180],
                         ["length", G], ["name", Q(pname), font()], ["number", Q(str(num)), font()]])
    node = ["symbol", Q(lib_id), ["exclude_from_sim", "no"], ["in_bom", "yes"], ["on_board", "yes"],
            ["property", Q("Reference"), Q(ref), ["at", -w / 2, top + G + 1.27, 0], font(justify="left")],
            ["property", Q("Value"), Q(name), ["at", -w / 2, top - G * rows - 1.27, 0], font(justify="left")],
            ["property", Q("Footprint"), Q(""), ["at", 0, 0, 0], font(hide=True)],
            ["property", Q("Datasheet"), Q(""), ["at", 0, 0, 0], font(hide=True)],
            ["property", Q("Description"), Q(""), ["at", 0, 0, 0], font(hide=True)],
            body, pins]
    return Symbol(lib_id, node)


# ---------------------------------------------------------------- circuit

class Part:
    def __init__(self, ref, value, symbol, footprint, sheet, lcsc="", mpn="", bom=True, fields=None):
        self.ref, self.value, self.symbol, self.footprint, self.sheet = ref, value, symbol, footprint, sheet
        self.lcsc, self.mpn, self.bom, self.fields = lcsc, mpn, bom, dict(fields or {})
        self.nets = {}   # pin number -> net name, or None for a deliberate no-connect
        self.at = None   # (x, y, rot) on the sheet, in mm

    def net(self, pin, net):
        """Connect a pin by number or by name (all pins with that name)."""
        nums = [str(pin)] if str(pin) in self.symbol.pins else self.symbol.numbers(str(pin))
        assert nums, f"{self.ref}: no pin {pin}"
        for n in nums:
            assert n not in self.nets, f"{self.ref}.{n} connected twice"
            self.nets[n] = net
        return self

    def nc(self, *pins):
        for p in pins:
            self.net(p, None)
        return self

    def connect(self, **pins):
        for p, n in pins.items():
            self.net(p.lstrip("_"), n)
        return self


class Circuit:
    def __init__(self, project):
        self.project, self.parts, self.sheets, self.notes = project, {}, [], []
        self.title, self.rev, self.date = project, "A", ""

    def sheet(self, name, title):
        self.sheets.append((name, title))
        return name

    def add(self, part):
        assert part.ref not in self.parts, f"duplicate {part.ref}"
        self.parts[part.ref] = part
        return part

    def note(self, sheet, x, y, text, size=2.0):
        self.notes.append((sheet, x, y, text, size))

    def netlist(self):
        """{net: sorted [(ref, pin)]} as designed, for comparing with what KiCad reads back."""
        out = {}
        for p in self.parts.values():
            missing = set(p.symbol.pins) - set(p.nets)
            assert not missing, f"{p.ref}: pins not decided: {sorted(missing)}"
            for pin, net in p.nets.items():
                if net is not None:
                    out.setdefault(net, []).append((p.ref, pin))
        return {k: sorted(v) for k, v in out.items()}


# ---------------------------------------------------------------- drawing

def _rot(x, y, deg):
    c, s = round(math.cos(math.radians(deg))), round(math.sin(math.radians(deg)))
    return x * c - y * s, x * s + y * c


def pin_end(part, num):
    """Sheet position of a pin's connection point and the direction pointing away from the body."""
    _, px, py, ang, _ = part.symbol.pins[num]
    x, y, rot = part.at
    rx, ry = _rot(px, py, rot)
    out = (ang + 180 + rot) % 360
    return round(x + rx, 4), round(y - ry, 4), out


LABEL = {0: (0, "left"), 180: (180, "right"), 90: (90, "left"), 270: (270, "right")}


def _symbol_node(circ, part, path):
    x, y, rot = part.at
    box = part.symbol.box
    props = [("Reference", part.ref, False), ("Value", part.value, False), ("Footprint", part.footprint, True),
             ("Datasheet", part.fields.get("Datasheet", ""), True), ("Description", part.fields.get("Description", ""), True),
             ("LCSC", part.lcsc, True), ("MPN", part.mpn, True)]
    props += [(k, v, True) for k, v in part.fields.items() if k not in ("Datasheet", "Description")]
    two_pin = len(part.symbol.pins) <= 2
    node = ["symbol", ["lib_id", Q(part.symbol.lib_id)], ["at", x, y, rot], ["unit", 1], ["body_style", 1],
            ["exclude_from_sim", "no"], ["in_bom", "yes" if part.bom else "no"], ["on_board", "yes"],
            ["in_pos_files", "yes"], ["dnp", "no"], ["uuid", uid(part.sheet, part.ref)]]
    for i, (k, v, hide) in enumerate(props):
        if k == "Reference":
            at = [x, y - 2.3, 0] if two_pin else [x + box[0] + G, y - box[3] - G - 1.6, 0]
        elif k == "Value":
            at = [x, y + 2.3, 0] if two_pin else [x + box[0] + G, y - box[1] + G + 1.6, 0]
        else:
            at = [x, y, 0]
        size = 1.0 if two_pin else 1.27
        node.append(["property", Q(k), Q(v), ["at"] + at, ["show_name", "no"], ["do_not_autoplace", "no"],
                     font(size, justify=None if two_pin else "left", hide=hide)])
    for num in sorted(part.symbol.pins):
        node.append(["pin", Q(num), ["uuid", uid(part.sheet, part.ref, "pin", num)]])
    node.append(["instances", ["project", Q(circ.project), ["path", Q(path), ["reference", Q(part.ref)], ["unit", 1]]]])
    return node


def _sheet_items(circ, sheet, path):
    items, libs = [], {}
    for part in circ.parts.values():
        if part.sheet != sheet:
            continue
        assert part.at, f"{part.ref} has no position"
        libs[part.symbol.lib_id] = part.symbol.node
        items.append(_symbol_node(circ, part, path))
        stub = 0 if len(part.symbol.pins) <= 2 or part.ref.startswith("#") else G
        for num in sorted(part.symbol.pins):
            x, y, out = pin_end(part, num)
            net = part.nets[num]
            if net is None:
                items.append(["no_connect", ["at", x, y], ["uuid", uid(sheet, part.ref, "nc", num)]])
                continue
            dx, dy = _rot(stub, 0, out)
            ex, ey = round(x + dx, 4), round(y - dy, 4)
            if stub:
                items.append(["wire", ["pts", ["xy", x, y], ["xy", ex, ey]], ["stroke", ["width", 0], ["type", "default"]],
                              ["uuid", uid(sheet, part.ref, "w", num)]])
            ang, just = LABEL[out]
            items.append(["global_label", Q(net), ["shape", "passive"], ["at", ex, ey, ang], ["fields_autoplaced", "yes"],
                          font(1.0, justify=just), ["uuid", uid(sheet, part.ref, "l", num)],
                          ["property", Q("Intersheetrefs"), Q("${INTERSHEET_REFS}"), ["at", ex, ey, 0], font(1.0, hide=True)]])
    for i, (s, x, y, text, size) in enumerate(circ.notes):
        if s == sheet:
            items.append(["text", Q(text), ["exclude_from_sim", "no"], ["at", x, y, 0], font(size, justify="left bottom"),
                          ["uuid", uid(sheet, "note", i)]])
    return items, libs


def _file(circ, name, title, page, items, libs, root):
    node = ["kicad_sch", ["version", 20260101], ["generator", Q("eeschema")], ["generator_version", Q("10.0")],
            ["uuid", uid("sheetfile", name)], ["paper", Q("A2" if not root else "A4")],
            ["title_block", ["title", Q(title)], ["rev", Q(circ.rev)], ["date", Q(circ.date)], ["company", Q(circ.project)]],
            ["lib_symbols"] + [libs[k] for k in sorted(libs)]] + items
    if root:
        node.append(["sheet_instances", ["path", Q("/"), ["page", Q("1")]]])
    node.append(["embedded_fonts", "no"])
    return dump(node) + "\n"


def write(circ, outdir):
    """Write the root sheet and one file per sheet. Returns the root file name."""
    root_uuid = uid("sheetfile", circ.project)
    root_items = []
    for i, (name, title) in enumerate(circ.sheets):
        su = uid("sheet", name)
        items, libs = _sheet_items(circ, name, f"/{root_uuid}/{su}")
        open(os.path.join(outdir, f"{name}.kicad_sch"), "w").write(_file(circ, name, title, i + 2, items, libs, False))
        x, y = 25.4 + (i % 4) * 63.5, 38.1 + (i // 4) * 38.1
        root_items.append(
            ["sheet", ["at", x, y], ["size", 50.8, 25.4], ["exclude_from_sim", "no"], ["in_bom", "yes"], ["on_board", "yes"],
             ["dnp", "no"], ["fields_autoplaced", "yes"], ["stroke", ["width", 0.1524], ["type", "solid"]],
             ["fill", ["color", 0, 0, 0, 0.0]], ["uuid", su],
             ["property", Q("Sheetname"), Q(title), ["at", x, y - 0.7, 0], font(justify="left bottom")],
             ["property", Q("Sheetfile"), Q(f"{name}.kicad_sch"), ["at", x, y + 26.0, 0], font(justify="left top")],
             ["instances", ["project", Q(circ.project), ["path", Q(f"/{root_uuid}"), ["page", Q(str(i + 2))]]]]])
    node_text = _file(circ, circ.project, circ.title, 1, root_items, {}, True)
    open(os.path.join(outdir, f"{circ.project}.kicad_sch"), "w").write(node_text)
    return f"{circ.project}.kicad_sch"


def write_symbol_lib(symbols, path):
    """Write the project's own symbols as a library, so ERC can compare them."""
    nodes = []
    for s in symbols:
        n = copy.deepcopy(s.node)
        n[1] = Q(s.lib_id.split(":")[1])
        nodes.append(n)
    open(path, "w").write(dump(["kicad_symbol_lib", ["version", 20251024], ["generator", Q("kicad_symbol_editor")],
                                ["generator_version", Q("10.0")]] + nodes) + "\n")
