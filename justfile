# calibre-web-kanagawa glue tasks

fork := env_var('HOME') / ".gitrepos/calibre-web-smallscope"
venv := env_var('HOME') / "calibre-web-env"

# Regenerate the mechanical recolor block from the fork's caliBlur.css
regen:
    python3 scripts/recolor_caliblur.py

# Run this repo's own tests (generator script)
test-theme:
    python3 -m unittest discover -s tests -v

# Vendor the canonical theme into the fork's static css
sync-theme:
    cp theme/kanagawa-dragon.css {{fork}}/cps/static/css/kanagawa-dragon.css
    @echo "vendored theme/kanagawa-dragon.css -> fork"

# Run the fork from source with the existing settings dir
serve:
    cd {{fork}} && CALIBRE_DBPATH={{env_var('HOME')}}/.calibre-web {{venv}}/bin/python cps.py -i 127.0.0.1

# Run the fork's test suite
test:
    cd {{fork}} && {{venv}}/bin/python -m unittest discover -s tests -v
