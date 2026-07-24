# CLAUDE.md (Carrel)

Per-project guidance. This file and `spec.md` are the contract for BOTH this
repo and the companion fork `~/.gitrepos/Carrel-calibre-web`; the fork's
own CLAUDE.md is a stub pointing here.

## What this is

Kanagawa Dragon theme + curated configuration + library-specific features for
calibre-web, serving Brandon's curated Calibre library
(`~/docs/Calibre Library/`). Read `spec.md` before changing semantics;
`roadmap.md` tracks phases.

## Hard rules

1. **Never write to `metadata.db`.** Not from code, not from tests, not
   "just to check something." The fork attaches it `mode=ro` (spec §7); keep
   that invariant. Anything that needs a library write goes through the
   library's own curation workflow (`~/docs/Calibre Library/CLAUDE.md`), not
   through this project.
2. **All fork work happens on the `smallscope` branch** (cut from tag
   `0.6.26`). Never commit to `master`; it tracks upstream. Rebases onto new
   upstream tags are deliberate events (spec §3), not routine pulls.
3. **The theme's canonical copy is `theme/kanagawa-dragon.css` in THIS repo.**
   The fork's `cps/static/css/kanagawa-dragon.css` is vendored via
   `just sync-theme`; never hand-edit the vendored copy.
4. **Palette comes from `~/.gitrepos/kanagawa-dragon-nvim-emacs`** (Brandon's
   Dragon port). Don't introduce colors outside spec §4.2; don't guess hexes.
5. **Tests run against the fixture DB, never the real library.** Read-only
   verification against the real library is fine (spec §10). Write-capable
   anything against `~/docs/Calibre Library/` is forbidden.
6. **Keep the fork diff small and rebase-friendly.** Disable routes rather
   than delete files; prefer one override stylesheet over edits inside
   caliBlur; isolate new code in new modules (`cps/wings.py`).
7. **Dependencies:** cquarry (editable, from `~/.gitrepos/CalibreQuarry`) is
   the one approved addition. Anything else: stop and ask first.
8. **License is GPL-3.0** in both repos. Don't add code with incompatible
   licensing.

## Layout and tooling

- `theme/` CSS source; `spec.md` contract; `roadmap.md` phases;
  `patchnotes.md` release notes (newest at top); `VERSION` single source of
  truth (this repo only; the fork keeps upstream's version).
- `justfile`: `sync-theme` (vendor CSS into the fork), `serve` (run the venv
  server).
- Deployment venv: `~/calibre-web-env/` (Python 3.14, holds the
  dependencies; the calibreweb wheel itself is uninstalled). The fork runs
  from source: `just serve`, which is
  `CALIBRE_DBPATH=~/.calibre-web <venv>/bin/python cps.py` in the fork.
  calibre-web's own `app.db` (users/settings, in `~/.calibre-web/`) is
  separate from the library and safe to touch.
- Fork tests: `Carrel-calibre-web/tests/`, unittest style, fixture
  metadata.db built in test setup.

## Working notes

- calibre-web internals research (file:line maps for the read-status bool
  assumptions, feature toggles, caliBlur structure) is recorded in spec
  §5.3/§6; trust it but re-verify line numbers after any rebase.
- The wing evaluator consumes cquarry's `search.py` engine. If that
  consumption deepens, raise the library-graduation question for
  CalibreQuarry per the global CLAUDE.md rule.
- Verification gates (spec §10) include checksumming `metadata.db` around a
  browse session and keeping `validate_library.py` at 0 errors. Run them at
  every phase boundary.
- The library itself is in maintenance mode; this project must never create
  pressure to restructure library metadata for the web app's convenience.
  The web app adapts to the library, not the reverse.
