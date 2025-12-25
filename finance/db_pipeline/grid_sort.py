import re

_TENOR_RE = re.compile(r"^(\d+)([DWMY])$", re.I)

def sort_grids_naturally(grids):
    def key(g):
        s = str(g).upper()
        short = {"ON":1,"TN":2,"SN":3}
        if s in short:
            return (0, short[s])
        m = _TENOR_RE.match(s)
        if m:
            n, u = int(m.group(1)), m.group(2).upper()
            mult = {"D":1,"W":7,"M":30,"Y":365}[u]
            return (1, n*mult)
        return (2, s)
    return sorted(grids, key=key)
