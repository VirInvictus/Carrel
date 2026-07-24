<p align="center"><img src="logo.svg" width="120" alt="Carrel logo"></p>

# Carrel

A Kanagawa Dragon theme and a curated, library-first configuration for
[calibre-web](https://github.com/janeczku/calibre-web).

The premise: a personal Calibre library deserves a web front-end that feels
like a reading room, not a dashboard. Surfaces stay near-black and muted so
the book covers are the most saturated thing on every page; text runs warm
(oldWhite headings, dragonOrange accents); everything you don't use is gone.

## What lives where

This repo is the project home: the canonical theme stylesheet
(`theme/kanagawa-dragon.css`), the specification (`spec.md`), the roadmap,
and glue tooling. The code changes live in a companion fork,
[Carrel-calibre-web](https://github.com/VirInvictus/Carrel-calibre-web),
as commits on the `smallscope` branch (cut from calibre-web `0.6.26`).

Beyond the theme, the fork adapts calibre-web to a curated library:

- **Read status from the library, read-only.** Stock calibre-web only links
  read state to boolean custom columns and otherwise keeps its own tracking
  table. The fork understands an enumeration column (To Read / Reading /
  Read / DNF) and displays it as a four-state badge. It never writes it;
  status changes belong to the curation workflow.
- **Wings.** Calibre virtual libraries, which stock calibre-web ignores
  entirely, appear as a sidebar section. Expressions are evaluated by
  [CalibreQuarry](../CalibreQuarry)'s stdlib port of Calibre's search grammar.
- **Read-only guarantee.** The fork attaches `metadata.db` with
  `mode=ro`. The web app cannot corrupt the library, by construction.
- **Trimmed surface.** Uploads, web metadata editing, shelves, tasks,
  email/Kindle, Kobo, Goodreads, and registration are removed or disabled.
  What remains: browse, search, read, download.

## Install (this instance)

```sh
# theme changes: edit theme/kanagawa-dragon.css here, then
just sync-theme        # vendors it into the fork's static/css/

# the fork replaces the calibreweb wheel in the venv (run-from-source;
# the 0.6.26 git tree has no src/ layout, so editable install isn't possible)
~/calibre-web-env/bin/pip uninstall calibreweb

# run (settings carry over from the wheel install via CALIBRE_DBPATH)
just serve
```

## Status

Scaffolding (v0.1.0). See `roadmap.md` for phases and `patchnotes.md` for
history.

## License

GPL-3.0, matching calibre-web. See `LICENSE`.

## Support

If this theme's useful to you and you'd like to chip in:

```
bc1qkge6zr45tzqfwfmvma2ylumt6mg7wlwmhr05yv
```
