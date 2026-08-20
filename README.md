<p align="center"><img src="logo.svg" width="120" alt="Carrel logo"></p>

# Carrel

A single-user reading room for one curated Calibre library, built on
[calibre-web](https://github.com/janeczku/calibre-web).

A carrel is a private desk in a library. That is the design brief: no accounts,
no sharing, no dashboard. One reader, 7,000 books, and an interface that gets
out of the way.

The register is a dark reading room wired into a terminal. Prose, titles and
book metadata are set in a serif; every label, count, nav item and table header
is mono. Surfaces stay in near-black so the covers are the most saturated thing
on any page, and rows share hairline rules instead of floating as cards.

## What lives where

**This repo is the contract and the theme.** `spec.md` is authoritative:
read it before changing semantics. `theme/kanagawa-dragon.css` is the canonical
stylesheet, vendored into the fork by `just sync-theme`.

**The code lives in the fork,**
[Carrel-calibre-web](https://github.com/VirInvictus/Carrel-calibre-web), on the
`smallscope` branch cut from calibre-web `0.6.26`. Its README has the
screenshots and the feature tour.

## What it does that calibre-web does not

- **No login.** The owner is authenticated on every request, so upstream's 154
  `@login_required` decorators pass untouched and rebases stay clean.
- **Calibre's search grammar.** Upstream has none; it matches the query as
  literal FTS text, so `author:"King"` returned nothing. Carrel evaluates
  through [CalibreQuarry](https://github.com/VirInvictus/CalibreQuarry)'s
  stdlib port of Calibre's parser: field prefixes, boolean logic, grouping,
  hierarchical tags, custom columns (`#audience:Rin`) and `vl:` references.
- **Wings.** Calibre virtual libraries as browse sections, evaluated through
  that same engine, so the sidebar and a `vl:` search agree by construction.
- **A category browser** over the library's dot taxonomy, where intermediate
  nodes are synthesised from path prefixes because only leaves are assigned.
- **Ctrl-K** over every wing, author, series, category and page, falling
  through to a search when what you typed is not a destination.
- **Statistics** computed live, where axes with a real distribution get charts
  and degenerate ones get a readout line.
- **Read status from the library, read-only.** An enumeration column (To Read /
  Reading / Read / DNF) rendered as a badge and never written back; status
  belongs to the curation workflow, not the web app.
- **A read-only guarantee.** `metadata.db` is attached `mode=ro`. The web app
  cannot corrupt the library, by construction, and the tests prove it by
  checksum.

## Design

The palette is Kanagawa Dragon, from Brandon's
[Emacs port](https://github.com/VirInvictus/kanagawa-dragon-nvim-emacs), which
is the source of truth for the hexes. The structure is adapted from his
Athenaeum static site so the two read as one property.

One constraint shaped the statistics surfaces more than any taste decision:
**Kanagawa fails as a categorical chart palette.** Measured in OKLab against
the dark surface, the worst adjacent accent pair sits at ΔE 6.7 for normal
vision, before colour blindness is considered, and five of six accents fall
below the chroma floor. So magnitude rides a single sequential gold ramp and
identity is carried by position and a direct label. There is no categorical
colour anywhere. See spec §4.3.

## Working on it

```sh
just check        # the theme contract: palette closure, serif stack, no caliBlur
just check-theme  # is the fork's vendored copy still the canonical one?
just sync-theme   # vendor theme/kanagawa-dragon.css into the fork
just serve        # run the fork from source
just test         # the fork's suite (33 tests)
```

The deployment venv is `~/.local/share/carrel/venv/`; the `calibreweb` wheel is
uninstalled and the fork runs from source, because the 0.6.26 tree has no
`src/` layout and cannot be installed editable.

> There is no authentication. The bind address is the only thing standing
> between the library and the network, and it is currently `0.0.0.0`
> deliberately. See spec §11.3 before changing where this runs.

CI guards the theme's contract rather than running tests: every colour in the
stylesheet and the logo must be declared in `:root`, the serif stack must lead
with the exact installed family, and no rule may target caliBlur. It runs
`scripts/check-theme.py`, the same file `just check` runs, so pushing is not
the only way to find out.

## Status

v0.9.2. Phases 0 through 11 are complete. `roadmap.md` tracks what remains
before 1.0, which is sign-off rather than code, plus one open contrast
question. `patchnotes.md` has the history, newest first.

## Licence

GPL-3.0, matching calibre-web. See `LICENSE`.

## Support

If this is useful to you and you would like to chip in:

- liberapay · [liberapay.com/bdkl](https://liberapay.com/bdkl/)
- bitcoin
  ```
  bc1qkge6zr45tzqfwfmvma2ylumt6mg7wlwmhr05yv
  ```
