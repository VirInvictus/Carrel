#!/usr/bin/env python3
"""Regenerate the recolor block of theme/kanagawa-dragon.css from caliBlur.

caliBlur.css hardcodes its palette across ~8000 lines. This script parses it
(plus caliBlur_override.css), maps every hardcoded color to its Kanagawa
Dragon equivalent by role (spec.md section 4.3), and rewrites the region
between the BEGIN/END GENERATED markers in the theme stylesheet. Re-run after
any upstream change to caliBlur, then `just sync-theme`.

Stdlib only. Usage:
    python3 scripts/recolor_caliblur.py [--fork PATH] [--theme PATH]
"""

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DEFAULT_FORK = Path.home() / ".gitrepos" / "calibre-web-smallscope"
DEFAULT_THEME = REPO / "theme" / "kanagawa-dragon.css"

BEGIN = "/* BEGIN GENERATED RECOLOR (scripts/recolor_caliblur.py) */"
END = "/* END GENERATED RECOLOR */"

# caliBlur hex -> Dragon hex, by role (spec.md section 4.3). Keys lowercase.
COLOR_MAP = {
    # text
    "#fff": "#c5c9c5",
    "#ffffff": "#c5c9c5",
    "#eee": "#c5c9c5",
    "#eeeeee": "#c5c9c5",
    "#ccc": "#a6a69c",
    "#cccccc": "#a6a69c",
    "#999": "#9e9b93",
    "#999999": "#9e9b93",
    "#add": "#8ba4b0",
    "#bac": "#949fb5",
    # gray ramp -> dragonBlack ramp (ordering preserved, compressed darker)
    "#555": "#393836",
    "#555555": "#393836",
    "#4f4f4f": "#393836",
    "#474747": "#181616",
    "#3f4245": "#282727",
    "#3c444a": "#282727",
    "#323232": "#1d1c19",
    "#282828": "#12120f",
    "#222": "#12120f",
    "#222222": "#12120f",
    "#202020": "#0d0c0c",
    "#1f1f1f": "#0d0c0c",
    "#191a1c": "#0d0c0c",
    "#000": "#0d0c0c",
    "#000000": "#0d0c0c",
    # accents: golden/orange chrome -> warm muted Dragon accents
    "#f9be03": "#b6927b",
    "#cc7b19": "#c4b28a",
    "#e59029": "#b98d7b",
    # reds
    "#ce3d2a": "#c4746e",
    "#ac3323": "#c4746e",
    "#641e14": "#393836",
    "#ff5533": "#c4746e",  # .alert-danger, only ever written as rgba()
}

HEX_RE = re.compile(r"#[0-9a-fA-F]{3,8}\b")
RGB_RE = re.compile(
    r"\brgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*(,\s*[^)]+?\s*)?\)"
)


def map_value(value):
    """Replace every mapped color in a declaration value. Returns (new, changed).

    Handles both #hex and rgb()/rgba() notation. caliBlur writes some of its
    palette as rgba (the .alert-danger orange, the cover-placeholder gradient),
    and a hex-only pass leaves those un-themed. Pure black is left alone: every
    rgba(0,0,0,x) in caliBlur is a drop shadow, where black is already correct
    and remapping would only churn ~90 rules for an invisible difference.
    """
    changed = False

    def hex_repl(m):
        nonlocal changed
        new = COLOR_MAP.get(m.group(0).lower())
        if new is None:
            return m.group(0)
        changed = True
        return new

    def rgb_repl(m):
        nonlocal changed
        r, g, b = (int(m.group(i)) for i in (1, 2, 3))
        if max(r, g, b) > 255:
            return m.group(0)
        if (r, g, b) == (0, 0, 0):
            return m.group(0)  # shadow; see docstring
        new = COLOR_MAP.get("#%02x%02x%02x" % (r, g, b))
        if new is None:
            return m.group(0)
        changed = True
        nr, ng, nb = (int(new[i : i + 2], 16) for i in (1, 3, 5))
        alpha = m.group(4) or ""
        return f"rgba({nr}, {ng}, {nb}{alpha})" if alpha else f"rgb({nr}, {ng}, {nb})"

    return RGB_RE.sub(rgb_repl, HEX_RE.sub(hex_repl, value)), changed


def parse_rules(css):
    """Yield (context, selector, body) for every rule, tracking @media nesting.

    context is the @media prelude or None. @font-face is skipped. @keyframes
    blocks are yielded whole as ('@keyframes', prelude, full_body) so they can
    be replaced atomically (a partial keyframes override would clobber the
    animation).
    """
    # strip comments
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    i, n = 0, len(css)
    media = None
    while i < n:
        brace = css.find("{", i)
        if brace == -1:
            break
        prelude = css[i:brace].strip()
        if prelude.startswith("@media"):
            media = prelude
            i = brace + 1
            continue
        if prelude.startswith(("@keyframes", "@-webkit-keyframes")):
            depth, j = 1, brace + 1
            while j < n and depth:
                if css[j] == "{":
                    depth += 1
                elif css[j] == "}":
                    depth -= 1
                j += 1
            yield ("@keyframes", prelude, css[brace + 1 : j - 1])
            i = j
            continue
        if prelude.startswith("@"):  # @font-face, @charset, @import...
            depth, j = 1, brace + 1
            while j < n and depth:
                if css[j] == "{":
                    depth += 1
                elif css[j] == "}":
                    depth -= 1
                j += 1
            i = j
            continue
        close = css.find("}", brace)
        if close == -1:
            break
        yield (media, prelude, css[brace + 1 : close])
        i = close + 1
        # detect leaving a media block: a '}' directly follows
        rest = css[i:]
        stripped = rest.lstrip()
        if media and stripped.startswith("}"):
            media = None
            i += len(rest) - len(stripped) + 1


def recolor_rule(selector, body):
    """Return recolored declarations for one rule, or None."""
    if selector == ":root":
        return None  # variables are overridden by hand in the theme header
    out = []
    for decl in body.split(";"):
        if ":" not in decl:
            continue
        prop, _, value = decl.partition(":")
        new_value, changed = map_value(value.strip())
        if changed:
            out.append(f"    {prop.strip()}: {new_value};")
    return out or None


def generate(sources):
    blocks = {}  # media-context -> list of rule strings (insertion-ordered)
    keyframes = []
    for src in sources:
        css = src.read_text(encoding="utf-8")
        for context, selector, body in parse_rules(css):
            if context == "@keyframes":
                new_body, changed = map_value(body)
                if changed:
                    keyframes.append(f"{selector} {{{new_body}}}")
                continue
            decls = recolor_rule(selector, body)
            if decls:
                rule = "%s {\n%s\n}" % (selector, "\n".join(decls))
                blocks.setdefault(context, []).append(rule)
    parts = []
    for context, rules in blocks.items():
        if context is None:
            parts.extend(rules)
        else:
            inner = "\n".join("    " + line for r in rules for line in r.splitlines())
            parts.append(f"{context} {{\n{inner}\n}}")
    parts.extend(keyframes)
    return "\n".join(parts)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--fork", type=Path, default=DEFAULT_FORK)
    ap.add_argument("--theme", type=Path, default=DEFAULT_THEME)
    args = ap.parse_args()

    css_dir = args.fork / "cps" / "static" / "css"
    sources = [css_dir / "caliBlur.css", css_dir / "caliBlur_override.css"]
    for s in sources:
        if not s.is_file():
            sys.exit(f"missing source: {s}")

    generated = generate(sources)
    theme = args.theme.read_text(encoding="utf-8")
    if BEGIN not in theme or END not in theme:
        sys.exit(f"markers not found in {args.theme}")
    head, _, rest = theme.partition(BEGIN)
    _, _, tail = rest.partition(END)
    args.theme.write_text(f"{head}{BEGIN}\n{generated}\n{END}{tail}", encoding="utf-8")
    rules = generated.count("{") - generated.count("@media")
    print(f"recolored ~{rules} rules into {args.theme}")


if __name__ == "__main__":
    main()
