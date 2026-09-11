#!/usr/bin/env python3
"""Guard the theme's contract (Carrel spec 4).

This repo holds no application code, so there is nothing to unit-test. What is
worth guarding is that the stylesheet and the logo keep the promises spec 4
makes about them:

  1. Every colour anywhere is one of the pinned Dragon palette hexes from
     spec 4.2 plus spec 4.3's gold ramp. The allowlist is pinned HERE, not
     derived from the sheet's `:root`: deriving it was a proven bypass
     (declaring `--evil: #ff0000` in :root legalized #ff0000 everywhere,
     Phase 13), and a rule before `:root` used to poison the extraction.
  2. Every colour the sheet's rules use is declared in `:root`, so the
     palette stays the single source and nobody hand-picks a hex mid-file
     (spec 4.2).
  3. `--serif` leads with "EB Garamond Absinthe". Plain "EB Garamond" resolves
     to Soehne on Brandon's machine, a sans, which quietly turns the reading
     room into a sans-serif one (spec 4.4).
  4. No rule targets caliBlur. Phase 8 made the sheet standalone over stock
     templates and `config_theme` is 0; a caliBlur selector means someone is
     writing against a stylesheet that is not loaded (spec 4.1, 4.7).
  5. `logo.svg` is palette-closed. This one was added on 2026-08-09, after
     the logo was found carrying Wave's #658594 for a year: the check had
     only ever looked at the CSS, so the other colour-bearing asset in the
     repo was unguarded.
  6. Colours written in non-hex notations are refused. rgb()/hsl() and the
     CSS named colours pass a hex-only regex untouched; the generator era
     already fell into this trap once (spec 4.7), and Phase 13 proved it
     again against this script.
  7. When the sibling fork checkout exists, its `cps/static/icon.svg` is
     byte-identical to `logo.svg` (Phase 13: the derivatives kept rendering
     the pre-fix Wave artwork because nothing regenerated them; `just
     sync-logo` is the recipe).

Run it with `just check`; CI runs this same file, so the two cannot drift.
Exits non-zero and prints one FAIL line per problem.
"""

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SHEET = ROOT / "theme" / "kanagawa-dragon.css"
LOGO = ROOT / "logo.svg"
FORK_ICON = ROOT.parent / "Carrel-calibre-web" / "cps" / "static" / "icon.svg"

SERIF_LEAD = '"EB Garamond Absinthe"'
HEX = re.compile(r"#[0-9a-fA-F]{3,8}\b")
FUNC_COLOR = re.compile(r"\b(?:rgba?|hsla?)\(", re.IGNORECASE)
# Whole tokens only: the lookalikes must not fire inside --kngw-black3,
# white-space, or grayscale. `transparent` and `currentColor` are legal.
NAMED_COLOR = re.compile(
    r"(?<![\w-])(white|black|red|green|blue|gray|grey|orange|yellow|pink|"
    r"purple|violet|aqua|teal|cyan|magenta|silver|gold|lime|maroon|navy|"
    r"olive|brown|beige|ivory|khaki|salmon|coral|crimson|indigo|plum|"
    r"tan|wheat|turquoise|orchid)(?![\w-])",
    re.IGNORECASE,
)

# Spec 4.2's table plus spec 4.3's gold ramp (gold 5 is dragonYellow). The
# spelling is pinned from the spec, not scraped from the sheet.
PALETTE = frozenset(
    h.lower()
    for h in (
        "#0d0c0c", "#12120f", "#1d1c19", "#181616", "#282727", "#393836",
        "#625e5a", "#c5c9c5", "#c8c093", "#dcd7ba",
        "#a6a69c", "#9e9b93", "#7a8382",
        "#b6927b", "#b98d7b", "#c4b28a", "#c4746e", "#87a987", "#8a9a7b",
        "#8ba4b0", "#8ea4a2", "#949fb5", "#a292a3", "#8992a7", "#737c73",
        "#e82424", "#ff9e3b",
        "#3a3222", "#5d5039", "#8a7853", "#a89571",
    )
)


def color_problems(label, text_without_comments):
    """Off-palette or non-hex notation in one asset's comment-free text."""
    problems = []
    stray = sorted({h.lower() for h in HEX.findall(text_without_comments)} - PALETTE)
    if stray:
        problems.append("%s uses off-palette colours: %s" % (label, ", ".join(stray)))
    funcs = sorted({m.group(0) for m in FUNC_COLOR.finditer(text_without_comments)})
    if funcs:
        problems.append("%s uses non-hex functional colour: %s" % (label, ", ".join(funcs)))
    named = sorted({m.group(0) for m in NAMED_COLOR.finditer(text_without_comments)})
    if named:
        problems.append(
            "%s uses CSS named colours (hex only): %s" % (label, ", ".join(named))
        )
    return problems


def main() -> int:
    raw = SHEET.read_text(encoding="utf-8")
    # Strip comments first: the header and several notes legitimately discuss
    # caliBlur, rgb(), and retired hexes in prose; only real rules are checked.
    css = re.sub(r"/\*.*?\*/", "", raw, flags=re.S)

    fails = []

    # The :root block, wherever it sits (a rule before it used to poison the
    # split-based extraction and hide whatever followed).
    root = re.search(r":root\s*\{(.*?)\}", css, re.S)
    if not root:
        fails.append("no :root block found")
        root_hexes = set()
    else:
        root_hexes = {h.lower() for h in re.findall(r"#[0-9a-fA-F]{6}\b", root.group(1))}

    unknown_in_root = sorted(root_hexes - PALETTE)
    if unknown_in_root:
        fails.append(
            ":root declares colours outside the spec palette: %s"
            % ", ".join(unknown_in_root)
        )

    # Every colour the sheet's rules use must be declared in :root...
    rules = css[: root.start()] + css[root.end() :] if root else css
    undeclared = sorted(
        {h.lower() for h in re.findall(r"#[0-9a-fA-F]{6}\b", rules)} - root_hexes
    )
    if undeclared:
        fails.append("off-palette colours outside :root: %s" % ", ".join(undeclared))

    # ...and the sheet as a whole (rules and :root together) stays inside the
    # pinned spec palette.
    fails.extend(color_problems("the sheet", css))

    serif = re.search(r"--serif:\s*([^;]+);", css)
    if not serif:
        fails.append("no --serif stack declared")
    elif not serif.group(1).strip().startswith(SERIF_LEAD):
        fails.append("--serif must lead with %s" % SERIF_LEAD)

    if "caliBlur" in css:
        fails.append(
            "a rule still targets caliBlur; the sheet is meant to be standalone"
        )

    logo = re.sub(r"<!--.*?-->", "", LOGO.read_text(encoding="utf-8"), flags=re.S)
    fails.extend(color_problems("logo.svg", logo))

    if FORK_ICON.exists():
        icon = FORK_ICON.read_bytes()
        if icon != LOGO.read_bytes():
            fails.append(
                "the fork's icon.svg differs from logo.svg; run just sync-logo"
            )
    else:
        print("note: no sibling fork checkout; icon.svg not checked")

    for f in fails:
        print("FAIL:", f)
    if fails:
        return 1
    print(
        "OK: %d palette hexes pinned, sheet and logo closed over them%s"
        % (len(PALETTE), ", fork icon.svg identical" if FORK_ICON.exists() else "")
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
