# Carrel glue tasks

home := env_var('HOME')
fork := home / ".gitrepos/Carrel-calibre-web"
venv := home / ".local/share/carrel/venv"

# Vendor the canonical theme into the fork's static css
sync-theme:
    cp theme/kanagawa-dragon.css {{fork}}/cps/static/css/kanagawa-dragon.css
    @echo "vendored theme/kanagawa-dragon.css -> fork"

# CI runs this same script, so the two cannot drift.
# Guard the theme contract: palette closure, serif stack, no caliBlur
check:
    python3 scripts/check-theme.py

# sync-theme is a one-way copy with no verify, so a hand-edit over there
# (CLAUDE.md rule 3) is otherwise undetectable. CI cannot run this: the fork
# is a separate repo.
# Check the fork's vendored copy still matches the canonical sheet
check-theme:
    @diff -u theme/kanagawa-dragon.css {{fork}}/cps/static/css/kanagawa-dragon.css \
        && echo "vendored copy matches theme/kanagawa-dragon.css" \
        || { echo "DRIFT: the fork's copy differs. Never hand-edit it there; run just sync-theme"; exit 1; }

# Run the fork from source with the existing settings dir
serve:
    cd {{fork}} && CALIBRE_DBPATH={{home}}/.calibre-web {{venv}}/bin/python cps.py -i 0.0.0.0

# Run the fork's test suite
test:
    cd {{fork}} && {{venv}}/bin/python -m unittest discover -s tests -v
