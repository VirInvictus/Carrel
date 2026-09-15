#!/usr/bin/env python3
"""Report sheet selectors that match nothing in the fork's DOM (and the
house-shaped reverse), Carrel spec 4.

Both past catches of this class were hand-made and are mechanically
findable: the `#description` selector that matched nothing (upstream spells
the element `#decription`), and the Bootstrap `.dropdown-menu` surface no
sheet rule touched (the last stock-white surface, themed 2026-09-15). This
script walks both directions and REPORTS; it never gates (exit 0 always).
Tune the allowlists against its output before anyone wires it into `just
check`; the bar for gating is zero unexplained findings on the live tree.

Coverage limits, stated so nobody trusts it past them:
  - Direction A (sheet -> DOM) scans for class and id tokens; a token is a
    hit if it appears anywhere in the fork's templates or Python (a loose
    universe by design: dynamically built names only need their stem
    present, e.g. `kngw-status-`).
  - Direction B (DOM -> sheet) only inspects clearly house-shaped class
    prefixes, because everything else in the templates is Bootstrap or
    stock calibre-web and deliberately unstyled here. A template class
    without a house prefix (the statistics template's bare `n`, at the
    time of writing) is invisible to it.
"""

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SHEET = ROOT / "theme" / "kanagawa-dragon.css"
FORK = ROOT.parent / "Carrel-calibre-web"

# Sheet classes/ids with no DOM hit are reported unless exempted here.
# Everything exempted is styled-as-framework or built dynamically.
TOKEN_ALLOWLIST = {
    # Bootstrap's icon font classes: the sheet styles the font-family and
    # colours, the templates only ever emit glyphicon-* dynamically.
    "glyphicon",
    "glyphicon-star",
    "glyphicon-star-empty",
    # The ramp steps arrive as `s{{ step }}` from statistics.html.
    "s1", "s2", "s3", "s4", "s5",
}

# Dynamic stems: the sheet styles the full set, templates build the name.
DYNAMIC_PREFIXES = (
    "kngw-status",  # kngw-status-{{ label }} on the detail page
)

# House-shaped prefixes for direction B: template classes that are OURS,
# so a house-prefixed class with no sheet rule is a real finding.
HOUSE_PREFIXES = (
    "kngw-", "cat-", "stat-", "hero-", "shelf-", "hour-", "ro-", "ro-",
    "masthead", "series-held", "kn-sel", "syntax-", "search-error",
    "nav-head", "page-count", "reader-state",
)


def sheet_tokens():
    """Class and id tokens from the sheet's selector positions only."""
    css = re.sub(r"/\*.*?\*/", "", SHEET.read_text(encoding="utf-8"), flags=re.S)
    # Unwrap at-rules (@media ...) so their inner rules read as top-level.
    css = re.sub(r"@[a-zA-Z-]+[^{;]*\{", "", css)
    selectors = "".join(m.group(1) for m in re.finditer(r"([^{}]+)\{[^{}]*\}", css))
    classes = set(re.findall(r"\.([a-zA-Z][\w-]*)", selectors))
    ids = set(re.findall(r"#([a-zA-Z][\w-]*)", selectors))
    return classes, ids


def fork_universe():
    """Every identifier-ish token in the fork's templates, Python and JS."""
    words = set()
    class_attrs = {}
    token_shape = re.compile(r"^[a-zA-Z][\w-]*$")
    for base in (FORK / "cps" / "templates", FORK / "cps", FORK / "cps" / "static"):
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if p.suffix not in (".html", ".py", ".js") or not p.is_file():
                continue
            text = p.read_text(encoding="utf-8", errors="replace")
            words.update(re.findall(r"[a-zA-Z][\w-]*", text))
            if p.suffix == ".html":
                for m in re.findall(r'class="([^"]*)"', text):
                    class_attrs.setdefault(p.name, set()).update(
                        t for t in m.split() if token_shape.match(t)
                    )
    return words, class_attrs


def main() -> int:
    classes, ids = sheet_tokens()
    words, class_attrs = fork_universe()

    print("sheet classes: %d, sheet ids: %d; fork tokens: %d"
          % (len(classes), len(ids), len(words)))

    dead = sorted(
        t for t in classes | ids
        if t not in words
        and t not in TOKEN_ALLOWLIST
        and not t.startswith(DYNAMIC_PREFIXES)
    )
    for t in dead:
        print("REPORT: sheet selector token .%s has no hit in the fork tree" % t)

    styled = classes
    for name in sorted(class_attrs):
        house = {
            c for c in class_attrs[name]
            if c.startswith(HOUSE_PREFIXES)
        }
        unstyled = sorted(c for c in house if c not in styled and c not in words)
        # A house class that the sheet never touches and the fork never
        # mentions elsewhere is either new or renamed away.
        for c in unstyled:
            print("REPORT: template %s carries house class %s with no sheet rule" % (name, c))

    if not dead:
        print("no dead sheet selectors found")
    print("report-only: exit code is always 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
