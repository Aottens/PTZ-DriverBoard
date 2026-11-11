"""Export the netlist with kicad-cli and read it back. Shared by check_netlist.py and the board tools."""
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sexp import find, find_all, parse  # noqa: E402

CLI = "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"


def export(sch):
    out = os.path.join(tempfile.mkdtemp(), "x.net")
    subprocess.run([CLI, "sch", "export", "netlist", "-o", out, sch], check=True, capture_output=True)
    return parse(open(out).read())


def pin_nets(tree):
    """{(ref, pin): net name}. Global labels give plain names; a leading slash is dropped."""
    out = {}
    for net in find_all(find(tree, "nets"), "net"):
        name = str(find(net, "name")[1]).lstrip("/")
        for node in find_all(net, "node"):
            out[(str(find(node, "ref")[1]), str(find(node, "pin")[1]))] = name
    return out


def components(tree):
    """{ref: dict(value, footprint, fields{}, path, uuid)}."""
    out = {}
    for comp in find_all(find(tree, "components"), "comp"):
        fields = {str(f[1][1]): str(f[2]) if len(f) > 2 else "" for f in find_all(find(comp, "fields") or [], "field")}
        sheetpath = find(comp, "sheetpath")
        out[str(find(comp, "ref")[1])] = dict(
            value=str(find(comp, "value")[1]), footprint=str((find(comp, "footprint") or ["", ""])[1]), fields=fields,
            path=str(find(sheetpath, "tstamps")[1]), uuid=str(find(comp, "tstamps")[1]))
    return out
