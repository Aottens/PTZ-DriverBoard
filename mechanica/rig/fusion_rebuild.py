#!/usr/bin/env python3
"""Rebuilds, checks and exports the rig through Fusion's local MCP endpoint. Fusion must be running.

  python3 mechanica/rig/fusion_rebuild.py build    # wipes the active unsaved design, then runs build_rig.py
  python3 mechanica/rig/fusion_rebuild.py check    # health and overlaps, both set-ups
  python3 mechanica/rig/fusion_rebuild.py export   # STL files and rig.f3d into export/

Each step can take minutes. Follow with `python3 mechanica/rig/check_print.py`.
"""
import json
import os
import sys
import urllib.error
import urllib.request

URL = "http://127.0.0.1:27182/mcp"
HERE = os.path.dirname(os.path.abspath(__file__))
HEAD = "import adsk.core, adsk.fusion, os\n\ndef run(_context: str):\n    app = adsk.core.Application.get()\n    d = adsk.fusion.Design.cast(app.activeProduct)\n    root = d.rootComponent\n"

BUILD = HEAD + f"""
    assert not app.activeDocument.isSaved, 'refusing to wipe a saved document: open a new one'
    d.timeline.markerPosition = 0
    d.timeline.deleteAllAfterMarker()
    path = {os.path.join(HERE, 'build_rig.py')!r}
    g = {{'__name__': 'build_rig'}}
    exec(compile(open(path).read(), path, 'exec'), g)
    g['build']()
    app.activeViewport.fit()
"""

CHECK = HEAD + """
    tl = d.timeline
    print('unhealthy', [tl.item(i).name for i in range(tl.count) if tl.item(i).healthState != adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState])
    other = {'print_fit_seat', 'print_fit_shaft'}
    for label, skip in (('7.5:1', {'print_pulley_100T'}), ('6.25:1', {'print_pulley_120T', 'print_idler_spacer_top', 'print_idler_spacer_low', 'koop_idler_2xF623'})):
        col = adsk.core.ObjectCollection.create()
        for o in root.allOccurrences:
            if o.component.name not in skip | other:
                for b in o.bRepBodies:
                    col.add(b)
        res = d.analyzeInterference(d.createInterferenceInput(col))
        print(label, 'overlaps', res.count)
        for r in res:
            print('  ', r.entityOne.parentComponent.name, '<>', r.entityTwo.parentComponent.name, round(r.interferenceBody.volume * 1000, 2), 'mm3')
"""

EXPORT = HEAD + f"""
    out = {os.path.join(HERE, 'export')!r}
    os.makedirs(out, exist_ok=True)
    em = d.exportManager
    done = set()
    for o in root.allOccurrences:
        c = o.component
        if c.name.startswith('print_') and c.name not in done:
            done.add(c.name)
            was = o.isLightBulbOn
            o.isLightBulbOn = True  # hidden parts are skipped otherwise
            opt = em.createSTLExportOptions(c, os.path.join(out, c.name.replace('print_', '') + '.stl'))
            opt.isBinaryFormat = True
            opt.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
            opt.sendToPrintUtility = False
            em.execute(opt)
            o.isLightBulbOn = was
    em.execute(em.createFusionArchiveExportOptions(os.path.join(out, 'rig.f3d')))
    print(sorted(os.listdir(out)))
"""

session = None


def call(method, params=None, id_=None):
    global session
    msg = {"jsonrpc": "2.0", "method": method}
    if params is not None:
        msg["params"] = params
    if id_ is not None:
        msg["id"] = id_
    headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
    if session:
        headers["Mcp-Session-Id"] = session
    with urllib.request.urlopen(urllib.request.Request(URL, json.dumps(msg).encode(), headers), timeout=590) as r:
        session = r.headers.get("Mcp-Session-Id") or session
        return r.read().decode()


def run_script(script):
    call("initialize", {"protocolVersion": "2025-03-26", "capabilities": {}, "clientInfo": {"name": "fusion_rebuild", "version": "1"}}, 1)
    call("notifications/initialized")
    reply = json.loads(call("tools/call", {"name": "fusion_mcp_execute", "arguments": {"featureType": "script", "object": {"script": script}}}, 2))
    for part in reply["result"]["content"]:
        body = json.loads(part["text"])
        print(body.get("message") or body.get("error"))
        if not body.get("success"):
            sys.exit(1)


if __name__ == "__main__":
    step = sys.argv[1] if len(sys.argv) > 1 else ""
    if step not in ("build", "check", "export"):
        sys.exit(__doc__)
    run_script({"build": BUILD, "check": CHECK, "export": EXPORT}[step])
