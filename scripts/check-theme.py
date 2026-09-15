#!/usr/bin/env python3
r"""Guard the theme's contract (Carrel spec 4).

This repo holds no application code, so there is nothing to unit-test in the
classic sense. What is worth guarding is that the stylesheet and the logo
keep the promises spec 4 makes about them -- and that this guard itself
cannot be silently bypassed. `--selftest` reintroduces every bypass class
against synthetic snippets and asserts refusal; `just check` and CI run it
before the real check, so the guard verifies itself on every push.

  1. Every colour anywhere is one of the pinned Dragon palette hexes from
     spec 4.2 plus spec 4.3's gold ramp. The allowlist is pinned HERE, not
     derived from the sheet's `:root`: deriving it was a proven bypass
     (declaring `--evil: #ff0000` in :root legalized #ff0000 everywhere,
     Phase 13), and a rule before `:root` used to poison the extraction.
  2. Every colour the sheet's RULES use rides a `var()` token: a raw hex
     outside `:root` fails outright. The earlier version only failed hexes
     NOT declared in `:root`, so a hand-picked hex already sitting in the
     palette could be hardcoded mid-file and pass (docstring said
     "nobody hand-picks a hex mid-file"; the code did not enforce it).
  3. `--serif` leads with "EB Garamond Absinthe" and, symmetrically,
     `--mono` leads with "JetBrains Mono". Plain "EB Garamond" resolves to
     Söhne on Brandon's machine, a sans, which quietly turns the reading
     room into a sans-serif one (spec 4.4). The same wrong-lead failure
     shape is one paste-away on the mono stack, so both stacks are pinned.
  4. No rule targets caliBlur. Phase 8 made the sheet standalone over stock
     templates and `config_theme` is 0; a caliBlur selector means someone is
     writing against a stylesheet that is not loaded (spec 4.1, 4.7).
  5. `logo.svg` is palette-closed. This one was added on 2026-08-09, after
     the logo was found carrying Wave's #658594 for a year: the check had
     only ever looked at the CSS, so the other colour-bearing asset in the
     repo was unguarded.
  6. Colours written in non-hex notations are refused: rgb()/rgba()/hsl()/
     hsla(), the modern painting functions hwb()/lab()/lch()/oklab()/
     oklch()/color()/color-mix()/light-dark()/device-cmyk(), and the FULL
     CSS named-colour set (148 names; a curated wordlist used to let
     whitesmoke, gainsboro or tomato sail through). rgb()/hsl() and named
     colours pass a narrow regex untouched; the generator era already fell
     into this trap once (spec 4.7), and Phase 13 proved it again against
     this script.
  7. When the sibling fork checkout exists, its `cps/static/icon.svg` is
     byte-identical to `logo.svg` (Phase 13: the derivatives kept rendering
     the pre-fix Wave artwork because nothing regenerated them; `just
     sync-logo` is the recipe). When the render tools exist too, the other
     two derivatives -- icon.png and favicon.ico, the exact files the
     incident lived in -- are re-rendered from logo.svg and byte-compared.
     The render check skips with a printed note when rsvg-convert/magick
     are absent (as on CI); the SVG byte-diff always runs.
  8. Structural sanity: braces balance; the `:root` block is extracted by
     brace-matching, not by stopping at the first `}` (a nested brace used
     to silently truncate the block); and every `var(--token)` the sheet
     references resolves to a token declared in `:root`. This is the
     "guard green, page unstyled" class of failure.

Boundary notes, so the next hardening does not re-derive them:
  - The hex regex requires 3+ hex digits and NO trailing identifier letter.
    That letter guard is why the id selector `#decription` (upstream's
    misspelling, live in three templates) is not read as the colour `#dec`,
    while over-long tokens like `#1816161816` still match whole and fail
    the palette closure. A `{3,8}\b` pattern refused to match a 9+-digit
    token at all, which is the escape this replaced.
  - The named-colour pattern is whole-token with `(?<![\w-])` / `(?![\w-])`,
    so `white-space`, `grayscale` and `--kngw-gray3` never fire.
  - `:root` declares the working subset of the pin: 24 tokens deployed of
    the 31 pinned here; the seven undeclared (samuraiRed, roninYellow,
    dragonGreen2, dragonAqua, dragonTeal, dragonPink, dragonViolet) have
    no use in the sheet yet. The pin does not follow the sheet; the sheet
    follows the pin.
  - The fork checkout for the derivative checks can be pointed anywhere
    with CARREL_FORK (CI uses this to check the fork out beside this repo).

Run it with `just check`; CI runs this same file (selftest first), so the
two cannot drift. Exits non-zero and prints one FAIL line per problem.
"""

import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
SHEET = ROOT / "theme" / "kanagawa-dragon.css"
LOGO = ROOT / "logo.svg"
FORK = pathlib.Path(os.environ.get("CARREL_FORK") or ROOT.parent / "Carrel-calibre-web")
FORK_ICON = FORK / "cps" / "static" / "icon.svg"
FORK_PNG = FORK / "cps" / "static" / "icon.png"
FORK_ICO = FORK / "cps" / "static" / "favicon.ico"

SERIF_LEAD = '"EB Garamond Absinthe"'
MONO_LEAD = '"JetBrains Mono"'

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

# The complete CSS Color Module Level 4 named-colour set: 148 keywords,
# gray/grey pairs included, rebeccapurple included.
CSS_NAMED_COLORS = (
    "aliceblue", "antiquewhite", "aqua", "aquamarine", "azure", "beige",
    "bisque", "black", "blanchedalmond", "blue", "blueviolet", "brown",
    "burlywood", "cadetblue", "chartreuse", "chocolate", "coral",
    "cornflowerblue", "cornsilk", "crimson", "cyan", "darkblue", "darkcyan",
    "darkgoldenrod", "darkgray", "darkgreen", "darkgrey", "darkkhaki",
    "darkmagenta", "darkolivegreen", "darkorange", "darkorchid", "darkred",
    "darksalmon", "darkseagreen", "darkslateblue", "darkslategray",
    "darkslategrey", "darkturquoise", "darkviolet", "deeppink",
    "deepskyblue", "dimgray", "dimgrey", "dodgerblue", "firebrick",
    "floralwhite", "forestgreen", "fuchsia", "gainsboro", "ghostwhite",
    "gold", "goldenrod", "gray", "green", "greenyellow", "grey",
    "honeydew", "hotpink", "indianred", "indigo", "ivory", "khaki",
    "lavender", "lavenderblush", "lawngreen", "lemonchiffon", "lightblue",
    "lightcoral", "lightcyan", "lightgoldenrodyellow", "lightgray",
    "lightgreen", "lightgrey", "lightpink", "lightsalmon", "lightseagreen",
    "lightskyblue", "lightslategray", "lightslategrey", "lightsteelblue",
    "lightyellow", "lime", "limegreen", "linen", "magenta", "maroon",
    "mediumaquamarine", "mediumblue", "mediumorchid", "mediumpurple",
    "mediumseagreen", "mediumslateblue", "mediumspringgreen",
    "mediumturquoise", "mediumvioletred", "midnightblue", "mintcream",
    "mistyrose", "moccasin", "navajowhite", "navy", "oldlace", "olive",
    "olivedrab", "orange", "orangered", "orchid", "palegoldenrod",
    "palegreen", "paleturquoise", "palevioletred", "papayawhip",
    "peachpuff", "peru", "pink", "plum", "powderblue", "purple",
    "rebeccapurple", "red", "rosybrown", "royalblue", "saddlebrown",
    "salmon", "sandybrown", "seagreen", "seashell", "sienna", "silver",
    "skyblue", "slateblue", "slategray", "slategrey", "snow",
    "springgreen", "steelblue", "tan", "teal", "thistle", "tomato",
    "turquoise", "violet", "wheat", "white", "whitesmoke", "yellow",
    "yellowgreen",
)

# A colour token: '#' + 3 or more hex digits, and no identifier letter
# after the hex run ends. See the boundary notes in the docstring.
HEX = re.compile(r"#[0-9a-fA-F]{3,}(?![0-9a-fA-Za-z])")

# Functional notations. hwb()/lab()/lch()/oklab()/oklch()/color()/
# color-mix()/light-dark() paint in every current browser and all passed a
# rgb/hsl-only regex untouched.
FUNC_COLOR = re.compile(
    r"\b(?:rgba?|hsla?|hwb|lab|lch|oklab|oklch|color(?:-mix)?|"
    r"device-cmyk|light-dark)\s*\(",
    re.IGNORECASE,
)

# Whole tokens only: the lookalikes must not fire inside --kngw-black3,
# white-space, or grayscale. `transparent` and `currentColor` are legal.
NAMED_COLOR = re.compile(
    r"(?<![\w-])(" + "|".join(CSS_NAMED_COLORS) + r")(?![\w-])",
    re.IGNORECASE,
)


def strip_css_comments(text):
    return re.sub(r"/\*.*?\*/", "", text, flags=re.S)


def strip_xml_comments(text):
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def color_problems(label, text_without_comments):
    """Off-palette or non-hex notation in one asset's comment-free text."""
    problems = []
    stray = sorted({h.lower() for h in HEX.findall(text_without_comments)} - PALETTE)
    if stray:
        problems.append("%s uses off-palette colours: %s" % (label, ", ".join(stray)))
    funcs = sorted({m.group(0).strip() for m in FUNC_COLOR.finditer(text_without_comments)})
    if funcs:
        problems.append("%s uses non-hex functional colour: %s" % (label, ", ".join(funcs)))
    named = sorted({m.group(0) for m in NAMED_COLOR.finditer(text_without_comments)})
    if named:
        problems.append(
            "%s uses CSS named colours (hex only): %s" % (label, ", ".join(named))
        )
    return problems


def split_root(css):
    """Split the sheet into (:root body, everything else).

    The old `:root\\s*\\{(.*?)\\}` stopped at the first `}` and never
    noticed a truncated block; this walks to the matching brace. The third
    value says whether the block closed at all.
    """
    m = re.search(r":root\s*\{", css)
    if not m:
        return None, css, False
    depth = 0
    for i in range(m.end() - 1, len(css)):
        if css[i] == "{":
            depth += 1
        elif css[i] == "}":
            depth -= 1
            if depth == 0:
                return css[m.end() : i], css[: m.start()] + css[i + 1 :], True
    return None, css, False


def brace_problems(css):
    if css.count("{") != css.count("}"):
        return [
            "unbalanced braces (%d open, %d close); the sheet may be malformed"
            % (css.count("{"), css.count("}"))
        ]
    return []


def stack_problems(css):
    """Both font stacks must lead with the exact installed family."""
    problems = []
    for token, lead in (("--serif", SERIF_LEAD), ("--mono", MONO_LEAD)):
        m = re.search(re.escape(token) + r":\s*([^;]+);", css)
        if not m:
            problems.append("no %s stack declared" % token)
        elif not m.group(1).strip().startswith(lead):
            problems.append("%s must lead with %s" % (token, lead))
    return problems


def var_problems(root_body, whole_css):
    """Every var(--token) referenced must be declared in :root."""
    declared = set(re.findall(r"(--[\w-]+)\s*:", root_body or ""))
    used = set(re.findall(r"var\((--[\w-]+)", whole_css))
    undefined = sorted(used - declared)
    if undefined:
        return ["var() references undeclared tokens: %s" % ", ".join(undefined)]
    return []


def raw_hex_problems(rules):
    """Guarantee 2: no raw hex anywhere outside :root, declared or not."""
    found = sorted({h.lower() for h in HEX.findall(rules)})
    if found:
        return ["raw hex outside :root (use a var() token): %s" % ", ".join(found)]
    return []


def derivative_problems():
    """Fork-side logo derivatives vs logo.svg (guarantee 7).

    Returns (problems, notes, rendered_checked): rendered_checked is True
    only when the re-render actually ran and the files matched.
    """
    problems, notes = [], []
    if not FORK.exists():
        notes.append("no sibling fork checkout; the icon checks did not run")
        return problems, notes, False

    if FORK_ICON.exists():
        if FORK_ICON.read_bytes() != LOGO.read_bytes():
            problems.append(
                "the fork's icon.svg differs from logo.svg; run just sync-logo"
            )
    else:
        problems.append("the fork checkout exists but cps/static/icon.svg is missing")

    rsvg = shutil.which("rsvg-convert")
    magick = shutil.which("magick")
    if not (rsvg and magick):
        notes.append(
            "rsvg-convert/magick not found; icon.png/favicon.ico renders not verified"
        )
        return problems, notes, False

    rendered_checked = True
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(td)
        png, ico = td / "icon.png", td / "favicon.ico"
        try:
            subprocess.run(
                [rsvg, "-w", "256", "-h", "256", str(LOGO), "-o", str(png)],
                check=True, capture_output=True,
            )
            subprocess.run(
                [magick, "-background", "none", "-define",
                 "icon:auto-resize=16,32,48", str(LOGO), str(ico)],
                check=True, capture_output=True,
            )
        except subprocess.CalledProcessError as exc:
            problems.append(
                "re-rendering the logo derivatives failed: %s" % exc.stderr.decode(errors="replace").strip()
            )
            return problems, notes, False
        for rendered, live, name in ((png, FORK_PNG, "icon.png"), (ico, FORK_ICO, "favicon.ico")):
            if not live.exists():
                problems.append("the fork checkout exists but %s is missing; run just sync-logo" % name)
                rendered_checked = False
            elif live.read_bytes() != rendered.read_bytes():
                problems.append(
                    "the fork's %s differs from a fresh render of logo.svg; run just sync-logo" % name
                )
                rendered_checked = False
    return problems, notes, rendered_checked


def selftest():
    """Reintroduce every bypass class; assert the guard refuses each."""
    checks = []

    def expect(name, got, want_substr):
        checks.append(
            (name, any(want_substr in line for line in got), "; ".join(got))
        )

    def expect_clean(name, got):
        checks.append((name, got == [], "; ".join(got)))

    # Named colours: the old wordlist let these through.
    expect("whitesmoke refused", color_problems("x", "a { color: whitesmoke; }"), "named")
    expect("fuchsia refused", color_problems("x", "a { color: fuchsia; }"), "named")
    expect("gainsboro refused", color_problems("x", "a { color: gainsboro; }"), "named")
    expect("rebeccapurple refused", color_problems("x", "a { color: rebeccapurple; }"), "named")
    # Functional notations: the old regex matched rgb/hsl only.
    expect("oklch refused", color_problems("x", "a { background: oklch(55% 0.1 30); }"), "functional")
    expect("lab refused", color_problems("x", "a { background: lab(50% 20 30); }"), "functional")
    expect("hwb refused", color_problems("x", "a { background: hwb(30 50% 50%); }"), "functional")
    expect("color-mix refused", color_problems("x", "a { color: color-mix(in srgb, red, blue); }"), "functional")
    expect("rgba still refused", color_problems("x", "a { color: rgba(1,2,3,0.5); }"), "functional")
    # Long hex tokens: a {3,8}\\b pattern refused to match these at all.
    expect(
        "over-long hex refused",
        color_problems("x", "a { color: #1816161816; }"),
        "off-palette",
    )
    # The id selector must NOT read as the colour #dec.
    got = color_problems("x", "#decription { color: whitesmoke; }")
    checks.append(
        ("#decription not read as hex", not any("#dec" in line for line in got), "; ".join(got))
    )
    expect("#decription's whitesmoke still caught", got, "named")
    # Legal notations stay legal.
    expect_clean(
        "transparent/currentColor legal",
        color_problems("x", "a { color: transparent; border-color: currentColor; }"),
    )
    expect_clean(
        "pinned palette hex legal",
        color_problems("x", "a { color: #c5c9c5; background: #12120F; }"),
    )
    expect_clean(
        "identifier lookalikes legal",
        color_problems("x", "a { white-space: nowrap; font: grayscale; }"),
    )

    # Raw hex outside :root, even a palette hex, even one :root declares.
    root, rules, closed = split_root(":root { --a: #12120f; } p { color: #181616; }")
    checks.append(("simple :root closes", closed and root is not None, ""))
    got = raw_hex_problems(rules)
    checks.append(
        (
            "raw hex outside :root caught, :root's own hex excluded",
            got == ["raw hex outside :root (use a var() token): #181616"],
            "; ".join(got),
        )
    )

    # Nested-brace :root extraction: the old regex truncated at the first }.
    root, _, closed = split_root(":root { --a: #181616; } /* } */")
    checks.append(("root split survives trailing brace text", closed and "#181616" in root, root or ""))

    # var() resolution.
    got = var_problems(" --kngw-white: #c5c9c5;", "p { color: var(--kngw-nonexistent); }")
    checks.append(("undeclared var caught", got != [], "; ".join(got)))
    got = var_problems(" --kngw-white: #c5c9c5;", "p { color: var(--kngw-white); }")
    checks.append(("declared var clean", got == [], "; ".join(got)))

    # Stack leads, both of them.
    got = stack_problems(':root { --serif: "EB Garamond", serif; --mono: "Courier New", monospace; }')
    checks.append(("both wrong leads caught", len(got) == 2, "; ".join(got)))
    got = stack_problems(
        ':root { --serif: "EB Garamond Absinthe", serif; --mono: "JetBrains Mono", monospace; }'
    )
    checks.append(("right leads clean", got == [], "; ".join(got)))

    # Braces.
    checks.append(("unbalanced braces caught", brace_problems("p { color: red;") != [], ""))
    checks.append(("balanced braces clean", brace_problems("p { color: red; }") == [], ""))

    failed = [name for name, ok, detail in checks if not ok]
    for name, ok, detail in checks:
        if not ok:
            print("SELFTEST FAIL: %s%s" % (name, (" [" + detail + "]") if detail else ""))
    if failed:
        print("selftest: %d of %d reintroductions NOT refused" % (len(failed), len(checks)))
        return 1
    print("selftest: %d reintroductions refused, guards verified" % len(checks))
    return 0


def main() -> int:
    raw = SHEET.read_text(encoding="utf-8")
    # Strip comments first: the header and several notes legitimately discuss
    # caliBlur, rgb(), and retired hexes in prose; only real rules are checked.
    css = strip_css_comments(raw)

    fails = []

    fails.extend(brace_problems(css))

    root_body, rules, closed = split_root(css)
    if root_body is None:
        if closed:
            fails.append("no :root block found")
        else:
            fails.append("the :root block does not close; extraction refused to guess")

    if root_body is not None:
        root_hexes = {h.lower() for h in HEX.findall(root_body)}
        unknown_in_root = sorted(root_hexes - PALETTE)
        if unknown_in_root:
            fails.append(
                ":root declares colours outside the spec palette: %s"
                % ", ".join(unknown_in_root)
            )
        fails.extend(raw_hex_problems(rules))
        fails.extend(var_problems(root_body, css))

    # The sheet as a whole (rules and :root together) stays inside the
    # pinned spec palette, in hex notation only.
    fails.extend(color_problems("the sheet", css))

    fails.extend(stack_problems(css))

    if "caliBlur" in css:
        fails.append(
            "a rule still targets caliBlur; the sheet is meant to be standalone"
        )

    logo = strip_xml_comments(LOGO.read_text(encoding="utf-8"))
    fails.extend(color_problems("logo.svg", logo))

    deriv_problems, notes, rendered_ok = derivative_problems()
    fails.extend(deriv_problems)

    for f in fails:
        print("FAIL:", f)
    for n in notes:
        print("note:", n)
    if fails:
        return 1
    parts = ["%d palette hexes pinned" % len(PALETTE), "sheet and logo closed over them"]
    if FORK_ICON.exists():
        parts.append("fork icon.svg identical")
    if rendered_ok:
        parts.append("rendered derivatives identical")
    print("OK: " + ", ".join(parts))
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv[1:]:
        sys.exit(selftest())
    sys.exit(main())
