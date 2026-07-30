# CLAUDE.md (Carrel)

Per-project guidance. This file and `spec.md` are the contract for BOTH this
repo and the companion fork `~/.gitrepos/Carrel-calibre-web`; the fork's own
CLAUDE.md covers the code-side hazards.

## What this is

A single-user reading room for Brandon's curated Calibre library
(`~/docs/Calibre Library/`), built on calibre-web. No login, read-only,
Calibre-parity search, wings, a category browser, and a statistics surface,
under an owned Kanagawa Dragon stylesheet.

This repo holds the contract (`spec.md`), the phases (`roadmap.md`), the
release history (`patchnotes.md`), the canonical theme (`theme/`), and the glue
(`justfile`). It holds no Python. All code lives in the fork.

## Hard rules

1. **Never write to `metadata.db`.** Not from code, not from tests, not "just
   to check something". The fork attaches it `mode=ro` (spec §7); keep that
   invariant. Library writes go through the curation workflow
   (`~/docs/Calibre Library/CLAUDE.md`), never through this project.
2. **All fork work happens on the `smallscope` branch** (cut from tag
   `0.6.26`). Never commit to `master`; it tracks upstream. Rebases onto new
   upstream tags are deliberate events (spec §3), not routine pulls.
3. **The theme's canonical copy is `theme/kanagawa-dragon.css` in THIS repo.**
   The fork's `cps/static/css/` copy is vendored via `just sync-theme`; never
   hand-edit it there.
4. **Palette comes from `~/.gitrepos/kanagawa-dragon-nvim-emacs`.** Don't
   introduce colours outside spec §4.2, and don't guess hexes. CI enforces
   this: every colour in the sheet must be declared in `:root`.
5. **Tests run against the fixture DB, never the real library.** Read-only
   verification against the real library is fine (spec §10). Anything
   write-capable against `~/docs/Calibre Library/` is forbidden.
6. **Keep the fork diff small and rebase-friendly.** Disable routes rather than
   delete files; isolate new code in new modules.
7. **Dependencies:** cquarry (editable, from `~/.gitrepos/CalibreQuarry`) is the
   one approved addition. Anything else: stop and ask.
8. **License is GPL-3.0** in both repos.

## Design constraints worth knowing before you touch the theme

- **The sheet is owned, not an override.** caliBlur is not loaded and
  `config_theme` is 0. There is no recolor generator any more; it retired with
  Phase 8, and spec §4.7 records why the override approach failed (rasters are
  unreachable by a colour generator, vendor selectors outrank hand-written
  polish, and a generator that knows one colour notation silently skips the
  others).
- **Ledgers, not cards.** Shared hairline rules, 3px radius, no drop shadows,
  no hover lift. Covers are presented by alignment and space.
- **Two type registers.** Serif for prose, titles and book metadata; mono for
  every label, count, nav item and table header. That split is what makes the
  chrome read as instrumentation.
- **No categorical colour, anywhere.** Kanagawa fails the categorical checks
  outright (spec §4.3). Magnitude rides the single gold ramp; identity is
  position plus a direct label.
- **Fonts are named for Brandon's machine**, a documented exception to the
  global rule (spec §4.4). `--serif` must lead with `"EB Garamond Absinthe"`:
  plain `"EB Garamond"` resolves to Söhne, a sans. Every stack ends in a
  generic family, which is what makes the phone degrade rather than break.
  CI asserts the lead.
- **Specificity beats source order**, and stock plus Bootstrap both carry
  selectors longer than the obvious override. This has bitten three times; when
  a rule does not apply, check that first.

## Layout and tooling

- `justfile`: `sync-theme` (vendor the CSS into the fork), `serve` (run the
  fork), `test` (the fork's suite).
- Deployment venv `~/.local/share/carrel/venv/` (Python 3.14) holds the dependencies;
  the calibreweb wheel is uninstalled and the fork runs from source, because
  the 0.6.26 tree has no `src/` layout. calibre-web's own `app.db` in
  `~/.calibre-web/` is separate from the library and safe to touch.
- CI runs no tests here (there is no Python). It guards the stylesheet's
  contract: palette closure, the serif stack, and the absence of caliBlur.

## Working notes

- **There is no authentication and the server binds `0.0.0.0`.** The control is
  that it runs only in trusted environments, not the bind address. Read spec
  §11.3 before moving where this runs; that clause has already flipped once.
- Verification gates (spec §10) include checksumming `metadata.db` around a
  browse session and keeping `validate_library.py` at 0 errors. Run them at
  every phase boundary.
- The search bar and wings both depend on cquarry's engine, so consumption is
  genuinely deep now. The library-graduation question is recorded as triggered
  in `roadmap.md`; revisit if a fourth consumer of library metrics appears.
- The library is in maintenance mode. This project must never create pressure
  to restructure library metadata for the web app's convenience. The web app
  adapts to the library, not the reverse.
