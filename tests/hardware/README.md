# Hardware checklists

Only the owner can run these (the hardware is on the owner's desk). A task that touches hardware is done when its
checklist is ticked and committed with the PR. Copy the relevant file to `tests/hardware/runs/<date>-<task>.md` and tick it
there, so the template stays clean. Every run file ends with `## Open points`: `- none`, or one line per point not fixed in
the run, ending in `→` where it went (a BACKLOG id, an IDEA id, or a checklist file in backticks).
`scripts/check-tracking.py` checks this in CI.
