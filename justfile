# Carrel glue tasks

home := env_var('HOME')
fork := home / ".gitrepos/Carrel-calibre-web"
venv := home / ".local/share/carrel/venv"

# Default target: list the recipes. This must stay the FIRST recipe so a
# bare `just` is inert; the mutating sync recipes below must never run as a
# side effect of an accidental bare `just`.
default:
    @just --list

# Vendor the canonical theme into the fork's static css. ONE-WAY, at the
# write path: theme/kanagawa-dragon.css in THIS repo is the only copy that
# is ever edited; the fork's copy is a build artifact and a hand-edit there
# is drift that `just check-theme` catches (CLAUDE.md rule 3).
sync-theme:
    cp theme/kanagawa-dragon.css {{fork}}/cps/static/css/kanagawa-dragon.css
    @echo "vendored theme/kanagawa-dragon.css -> fork"

# The fork's derived logo assets are cut from logo.svg here, the single
# source: icon.svg is a byte copy, icon.png and favicon.ico are renders.
# check-theme diffs the fork's icon.svg against logo.svg and, when
# rsvg-convert/magick are present, re-renders and byte-compares the other
# two, so a stale derivative (the icon.png/favicon.ico pair once kept the
# pre-fix Wave artwork for a month) is catchable before pushing.
sync-logo:
    cp logo.svg {{fork}}/cps/static/icon.svg
    rsvg-convert -w 256 -h 256 logo.svg -o {{fork}}/cps/static/icon.png
    magick -background none -define icon:auto-resize=16,32,48 logo.svg {{fork}}/cps/static/favicon.ico
    @echo "logo.svg -> fork icon.svg / icon.png / favicon.ico"

# Vendor both assets, then run both guards. The compound recipe exists
# because the loose half-run (sync without check) is exactly how the
# month-long stale-artifact incident happened.
sync: sync-theme sync-logo check check-theme

# CI runs this same script (selftest first), so the two cannot drift.
# The name advertises the boring guards; the surprising ones it also runs:
# modern notation + full named-colour refusal, raw-hex-outside-:root,
# the --mono lead, var() resolution, brace balance, and the fork's rendered
# logo derivatives when the tools exist. --selftest reintroduces every
# bypass class and asserts refusal.
check:
    python3 scripts/check-theme.py --selftest
    python3 scripts/check-theme.py

# sync-theme is a one-way copy with no verify, so a hand-edit over there
# (CLAUDE.md rule 3) is otherwise undetectable. CI cannot run this: the fork
# is a separate repo.
# Check the fork's vendored copy still matches the canonical sheet
check-theme:
    @diff -u theme/kanagawa-dragon.css {{fork}}/cps/static/css/kanagawa-dragon.css \
        && echo "vendored copy matches theme/kanagawa-dragon.css" \
        || { echo "DRIFT: the fork's copy differs. Never hand-edit it there; run just sync-theme"; exit 1; }

# Report-only: sheet selectors vs the fork's DOM. Prints sheet classes with
# no template/python hit and house-prefixed template classes no sheet rule
# touches. Never gates (exit 0); tune its allowlists before trusting it.
lint-selectors:
    python3 scripts/lint-selectors.py

# Run the fork from source with the existing settings dir
serve:
    cd {{fork}} && CALIBRE_DBPATH={{home}}/.calibre-web {{venv}}/bin/python cps.py -i 0.0.0.0

# Run the fork's test suite
test:
    cd {{fork}} && {{venv}}/bin/python -m unittest discover -s tests -v
