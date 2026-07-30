# Carrel glue tasks

fork := env_var('HOME') / ".gitrepos/Carrel-calibre-web"
venv := env_var('HOME') / ".local/share/carrel/venv"

# Vendor the canonical theme into the fork's static css
sync-theme:
    cp theme/kanagawa-dragon.css {{fork}}/cps/static/css/kanagawa-dragon.css
    @echo "vendored theme/kanagawa-dragon.css -> fork"

# Run the fork from source with the existing settings dir
serve:
    cd {{fork}} && CALIBRE_DBPATH={{env_var('HOME')}}/.calibre-web {{venv}}/bin/python cps.py -i 0.0.0.0

# Run the fork's test suite
test:
    cd {{fork}} && {{venv}}/bin/python -m unittest discover -s tests -v
