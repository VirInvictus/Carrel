#!/usr/bin/env python3
"""Guard the theme's contract (Carrel spec 4).

This repo holds no application code, so there is nothing to unit-test. What is
worth guarding is that the stylesheet and the logo keep the promises spec 4
makes about them:

  1. Every colour the sheet uses is declared in `:root`, so the Dragon palette
     stays the single source and nobody hand-picks a hex mid-file (spec 4.2).
  2. `--serif` leads with "EB Garamond Absinthe". Plain "EB Garamond" resolves
     to Soehne on Brandon's machine, a sans, which quietly turns the reading
     room into a sans-serif one (spec 4.4).
  3. No rule targets caliBlur. Phase 8 made the sheet standalone over stock
     templates and `config_theme` is 0; a caliBlur selector means someone is
     writing against a stylesheet that is not loaded (spec 4.1, 4.7).
  4. `logo.svg` uses only colours the sheet declares. This one was added on
     2026-08-09, after the logo was found carrying Wave's #658594 for a year:
     the check had only ever looked at the CSS, so the other colour-bearing
     asset in the repo was unguarded.

Run it with `just check`; CI runs this same file, so the two cannot drift.
Exits non-zero and prints one FAIL line per problem.
"""

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SHEET = ROOT / "theme" / "kanagawa-dragon.css"
LOGO = ROOT / "logo.svg"

SERIF_LEAD = '"EB Garamond Absinthe"'
HEX = re.compile(r"#[0-9a-fA-F]{3,8}\b")


def main() -> int:
    raw = SHEET.read_text(encoding="utf-8")
    # Strip comments first: the header and several notes legitimately discuss
    # caliBlur in prose, and only real rules should be checked.
    css = re.sub(r"/\*.*?\*/", "", raw, flags=re.S)
    root = css.split("}", 1)[0]

    declared = {v.lower() for v in re.findall(r"#[0-9a-fA-F]{6}\b", root)}
    fails = []

    stray = sorted({h.lower() for h in HEX.findall(css)} - declared)
    if stray:
        fails.append("off-palette colours outside :root: %s" % ", ".join(stray))

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
    logo_stray = sorted({h.lower() for h in HEX.findall(logo)} - declared)
    if logo_stray:
        fails.append(
            "logo.svg uses colours the sheet does not declare: %s"
            % ", ".join(logo_stray)
        )

    for f in fails:
        print("FAIL:", f)
    if fails:
        return 1
    print(
        "OK: %d colours declared in :root, sheet and logo both closed over them"
        % len(declared)
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
