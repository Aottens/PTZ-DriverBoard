"""Minimal S-expression reader and writer for KiCad files.

A node is a Python list; a quoted string is a Q (so it is written back with quotes); anything else is a bare atom (str).
"""


class Q(str):
    """A string that was, or must be, quoted in the file."""


def parse(text):
    pos, n = 0, len(text)
    stack, cur = [], []
    while pos < n:
        c = text[pos]
        if c in " \t\r\n":
            pos += 1
        elif c == "(":
            stack.append(cur)
            cur = []
            pos += 1
        elif c == ")":
            done, cur = cur, stack.pop()
            cur.append(done)
            pos += 1
        elif c == '"':
            end, out = pos + 1, []
            while text[end] != '"':
                if text[end] == "\\":
                    end += 1
                    out.append({"n": "\n", "t": "\t"}.get(text[end], text[end]))
                else:
                    out.append(text[end])
                end += 1
            cur.append(Q("".join(out)))
            pos = end + 1
        else:
            end = pos
            while end < n and text[end] not in " \t\r\n()":
                end += 1
            cur.append(text[pos:end])
            pos = end
    assert not stack, "unbalanced parentheses"
    return cur[0]


def _atom(a):
    if isinstance(a, Q):
        return '"' + a.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'
    if isinstance(a, float):
        return ("%.4f" % a).rstrip("0").rstrip(".")
    return str(a)


def dump(node, indent=0):
    """Write a node. Short leaf lists stay on one line."""
    if not isinstance(node, list):
        return _atom(node)
    if all(not isinstance(x, list) for x in node):
        return "(" + " ".join(_atom(x) for x in node) + ")"
    pad = "\t" * (indent + 1)
    head = [x for x in node if not isinstance(x, list)]
    out = "(" + " ".join(_atom(x) for x in head)
    for x in node:
        if isinstance(x, list):
            out += "\n" + pad + dump(x, indent + 1)
    return out + "\n" + "\t" * indent + ")"


def find(node, key):
    """First child list whose head is key, or None."""
    for x in node:
        if isinstance(x, list) and x and x[0] == key:
            return x
    return None


def find_all(node, key):
    return [x for x in node if isinstance(x, list) and x and x[0] == key]


if __name__ == "__main__":
    t = '(a "b c" (d 1.5 "q\\"x") (e))'
    p = parse(t)
    assert p == ["a", "b c", ["d", "1.5", 'q"x'], ["e"]] and isinstance(p[1], Q)
    assert parse(dump(p)) == p
    print("sexp ok")
