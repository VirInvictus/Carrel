# calibre-web-kanagawa: Specification

The contract for the Kanagawa Dragon calibre-web theme and its companion fork.
Read this before changing semantics in either repo.

Last revised: 2026-06-11. Companion repo: `calibre-web-smallscope`
(fork of `janeczku/calibre-web`; all code changes live there on the
`smallscope` branch). This repo holds the theme source, the documentation
contract, and glue tooling.

---

## 1. Purpose

A personal web front-end for Brandon's curated Calibre library (5,600+ books,
single-tag dot taxonomy, 31 virtual-library wings, validator-enforced metadata)
that:

1. Looks like the rest of his environment (Kanagawa Dragon), is warm and
   inviting, and puts the curated covers first.
2. Exposes only the features actually used: browse, search, read, download.
3. Understands the library's own metadata model: the `reading_status`
   enumeration column and the wing system, both of which stock calibre-web
   ignores.
4. Can never write to `metadata.db`. The library has exactly one writer
   (Calibre desktop plus the curation toolchain, always with Calibre closed);
   this project is a reader, enforced at the SQLite connection level.

## 2. Components

| Repo | Role |
| --- | --- |
| `calibre-web-kanagawa` (this repo) | Theme source (`theme/`), spec, roadmap, patchnotes, glue (`justfile`). The documentation here is the contract for both repos. |
| `calibre-web-smallscope` | Fork of calibre-web. Branch `smallscope`, cut from tag `0.6.26` (the release installed in `~/calibre-web-env/`). All Python/template/CSS changes are commits on this branch. |

Division of labor: the theme is developed here in `theme/kanagawa-dragon.css`
and vendored into the fork at `cps/static/css/kanagawa-dragon.css` via
`just sync-theme`, so the fork remains self-contained and runnable on its own.
The canonical copy is always this repo; never hand-edit the vendored copy.

Deployment: the calibreweb wheel is uninstalled from the venv and the fork
runs from source (the git tree at tag 0.6.26 has no `src/` packaging layout,
so editable installs are not possible; `python cps.py` is upstream's
supported source-run mode):

```sh
CALIBRE_DBPATH=~/.calibre-web ~/calibre-web-env/bin/python \
    ~/.gitrepos/calibre-web-smallscope/cps.py
```

`CALIBRE_DBPATH` points at the existing settings directory
(`~/.calibre-web/`: `app.db`, `.key`, logs), so users and configuration
carry over from the wheel install. `app.db` is independent of the library
and safe to touch.

## 3. Base version and upstream policy

- Base: calibre-web `0.6.26` (tag), Python 3.14 venv at `~/calibre-web-env/`.
- The fork keeps upstream's version number; project identity lives in the
  `smallscope` branch and this repo's `VERSION`.
- Upstream rebases are deliberate, not automatic: fetch upstream, read the
  release notes, rebase `smallscope` onto the new tag, re-run the fork tests,
  re-verify the feature-removal list (section 6) against new UI surface.
- License: GPL-3.0 in both repos (calibre-web is GPL-3.0; the theme targets
  its templates and caliBlur's selectors, so everything stays aligned).

## 4. Theme

### 4.1 Mechanism

caliBlur (calibre-web's built-in dark theme, `g.current_theme == 1`) stays
enabled as the base layer. The fork adds exactly one stylesheet link in
`cps/templates/layout.html`, after `caliBlur_override.css`:

```html
<link href="{{ url_for('static', filename='css/kanagawa-dragon.css') }}" rel="stylesheet" media="screen">
```

All visual change lives in that one override sheet. caliBlur defines a small
set of CSS custom properties (`caliBlur.css:74-79`) plus roughly 25 dominant
hardcoded colors; the override redefines the variables first, then restyles
the selectors that hardcode.

### 4.2 Palette

Source of truth: the Dragon palette as pinned in Brandon's
`kanagawa-dragon-nvim-emacs` port (which follows `rebelot/kanagawa.nvim`).

| Token | Hex | Role here |
| --- | --- | --- |
| dragonBlack0 | `#0d0c0c` | Deepest background (modals, wells) |
| dragonBlack1 | `#12120f` | Page background |
| dragonBlack2 | `#1D1C19` | Alternate surface |
| dragonBlack3 | `#181616` | Primary surface (cards, navbar) |
| dragonBlack4 | `#282727` | Raised surface, hover background |
| dragonBlack5 | `#393836` | Borders, dividers |
| dragonBlack6 | `#625e5a` | Muted/disabled text |
| dragonWhite | `#c5c9c5` | Body text |
| oldWhite | `#C8C093` | Headings, emphasized text (the "warm" anchor) |
| fujiWhite | `#DCD7BA` | High-emphasis text on hover/focus |
| dragonGray / 2 / 3 | `#a6a69c` / `#9e9b93` / `#7a8382` | Secondary text, metadata lines |
| dragonOrange | `#b6927b` | Primary accent (links, active nav, buttons) |
| dragonOrange2 | `#b98d7b` | Accent hover |
| dragonYellow | `#c4b28a` | Secondary accent (badges, ratings) |
| dragonRed | `#c4746e` | Destructive/error, DNF badge |
| dragonGreen | `#87a987` | Success, Read badge |
| dragonGreen2 | `#8a9a7b` | Subtle success |
| dragonBlue2 | `#8ba4b0` | Info accents, Reading badge |
| dragonAqua | `#8ea4a2` | Quiet accents |
| dragonTeal | `#949fb5` | Quiet accents |
| dragonPink | `#a292a3` | Sparingly, if at all |
| dragonViolet | `#8992a7` | Sparingly, if at all |
| dragonAsh | `#737c73` | To Read badge, placeholders |
| samuraiRed | `#E82424` | Hard errors only |
| roninYellow | `#FF9E3B` | Hard warnings only |

### 4.3 caliBlur variable mapping

| caliBlur | Value | Kanagawa replacement |
| --- | --- | --- |
| `--color-background` | `#474747` | dragonBlack1 `#12120f` |
| `--color-primary` | `#F9BE03` | dragonOrange `#b6927b` |
| `--color-secondary` | `#CC7B19` | dragonYellow `#c4b28a` |
| `--color-secondary-hover` | `#E59029` | dragonOrange2 `#b98d7b` |
| `--color-background-mobile` | `#1f1f1f` | dragonBlack0 `#0d0c0c` |

Hardcoded caliBlur colors map by role, not one-to-one: whites (`#fff`,
`#eee`) become dragonWhite/fujiWhite by emphasis; the gray ramp (`#222`,
`#282828`, `#323232`, `#3f4245`, `#474747`, `#555`) collapses onto the
dragonBlack ramp; reds (`#ce3d2a`, `#ac3323`) become dragonRed.

### 4.4 Design principles

1. **Covers carry the color.** Surfaces stay in the near-black dragonBlack
   range with low-saturation text; the curated covers are the most saturated
   objects on every page. No loud chrome accent (the stock golden `#F9BE03`
   is exactly what we are removing).
2. **Warm, not clinical.** oldWhite headings, dragonOrange/dragonYellow
   accents; the blue/violet side of the palette is for small informational
   touches only.
3. **Covers get presentation treatment**: comfortable grid spacing, rounded
   corners, soft shadow, gentle hover lift/scale. Badges and overlays stay
   subdued so they never compete with the artwork.
4. **Typography is the bundled Open Sans** (embedded in caliBlur as
   base64 WOFF). No reliance on system-installed fonts, ever.
5. **Readability beats density.** This is a reading room, not a dashboard.

### 4.5 Assets

Project `logo.svg` lives in this repo; the fork's `static/favicon.ico` and
`static/icon.svg`/`icon.png` are regenerated from it.

### 4.6 Reader theming (stretch, Phase 5)

The EPUB reader (`read.html`) has its own theme selector and isolated styles
(`epub_themes.css`); it does not inherit the app theme. A "Kanagawa" reading
theme (dragonBlack1 page, dragonWhite text) is planned as a stretch goal.
PDF/comic/DJVU readers keep their stock styling.

## 5. Read status: the `reading_status` enumeration

### 5.1 The problem

Stock calibre-web links read status only to **bool** custom columns
(`admin.py:282` and `:959` filter `datatype == 'bool'`); with no linked
column it tracks read state in its own `app.db` table (`ub.ReadBook`).
The library's status column is cc2 `reading_status`, an **enumeration**:
`To Read` (default), `Reading`, `Read`, `DNF`. It is Brandon-curated and
must never be machine-written.

### 5.2 The contract

- The fork accepts enumeration columns for `config_read_column` and the
  instance links cc2.
- Status is **read-only from the web**. The web UI displays it; changes
  happen in Calibre desktop only.
- Boolean projection where calibre-web needs a binary answer:
  `read == (value == 'Read')`. Everything else (`To Read`, `Reading`, `DNF`,
  no value) counts as unread for section/filter purposes. The 4-state badge
  on the detail page always shows the true value, so no nuance is lost.
- Badge colors: Read = dragonGreen, Reading = dragonBlue2, To Read =
  dragonAsh, DNF = dragonRed (muted treatments per section 4.4).

### 5.3 Code paths (researched against 0.6.26)

| File | Change |
| --- | --- |
| `cps/admin.py:282, 959` (incl. `check_valid_read_column`) | Accept `datatype.in_(['bool', 'enumeration'])`. |
| `cps/db.py:811` `generate_linked_query` | Enum branch: bool columns join the value table directly (`read_column.book == Books.id`); enumeration is normalized, so join `books_custom_column_N_link` then the value table, selecting the string value. Idiom precedent: restricted-column filter at `db.py:786-809`. |
| `cps/db.py:729` `get_book_read_archived` | Same enum branch; this is a SEPARATE query builder used by the detail view (and basic theme) with its own bool-only join. Found during verification: for enum classes the `.book` access raises AttributeError, silently swallowed by the surrounding except, yielding None. |
| `cps/web.py:1644` | Detail view: `entry.read_status = (value == 'Read')` for enum; also expose the raw label for the badge. |
| `cps/web.py:747-749` | Read/Unread sections: enum filter per 5.2. |
| `cps/search.py:145-147` | Advanced-search read filter: same projection. |
| `cps/helper.py:306-351` `edit_book_read_status` | Hard write-guard: if the linked column is an enumeration, refuse and return an error. `/ajax/toggleread` therefore never writes. |
| `cps/templates/detail.html:255-264` | Replace the read checkbox with the read-only 4-state badge. |

## 6. Feature surface

### 6.1 Removed by configuration (documented baseline, no code)

Applied in the admin UI and recorded here so the instance is reproducible:
uploads off, anonymous browsing off, public registration off, magic-link
remote login off, Kobo sync off, Goodreads off, embed-metadata-on-download
off. Sidebar sections (ratings, formats, publishers, hot books, etc.) are
per-user `sidebar_view` bitmask settings (`constants.py` `SIDEBAR_*`), set
per account rather than patched.

### 6.2 Removed by patch (config cannot hide these)

| Surface | Where |
| --- | --- |
| Tasks page and navbar link | `layout.html`, tasks routes disabled |
| Shelves UI (sidebar section, create/edit) | `layout.html:149+`, shelf routes disabled; Wings replace shelves as the grouping concept |
| Send-to-eReader / email machinery | `detail.html:54`, SMTP config UI |
| Kindle/Kobo per-user fields | `user_edit.html:28-29, 67-70` |
| Upload and web metadata editing entry points | navbar/detail edit buttons, editbooks routes disabled |
| Mass mark-read buttons | `book_table.html:34-37` |
| Registration/magic-link remnants, Goodreads settings | templates and admin panes |

Rule: routes are **disabled** (404/registration removed), not deleted, when
that keeps the diff small and rebase-friendly. Users: exactly two accounts
(Brandon, Rin), both see the whole library; no content restriction.

## 7. Read-only metadata.db guarantee

Stock calibre-web attaches `metadata.db` read-write
(`db.py:690-718`, SERIALIZABLE, no WAL). The fork attaches it read-only
(`file:...?mode=ro` URI). Combined with sections 5 and 6 this turns "the web
app should not write the library" into "the web app cannot write the
library." calibre-web's own `app.db` (users, settings) remains writable; it
is a separate SQLite file outside the library.

Implication to respect in all future work: any feature that would write
`metadata.db` is out of scope by construction. If one is ever wanted, it
goes through the library's curation workflow instead (Calibre closed,
backup, single transaction, validator to 0 errors).

## 8. Wings (virtual libraries)

### 8.1 The problem

The library's 31 wings live as Calibre search expressions in the
`virtual_libraries` key of `metadata.db`'s `preferences` table. Stock
calibre-web never reads that table (confirmed: zero references) and offers
only its own shelf system, which duplicates curation state.

### 8.2 The contract

- New module `cps/wings.py` in the fork reads the `virtual_libraries` JSON
  and evaluates each wing's expression to a set of book ids using
  **CalibreQuarry's search engine** (`cquarry`, v2.6+:
  `search(expr) -> set[int]`, a stdlib-faithful port of Calibre's expression
  grammar including `vl:` references, so the self-referential Unsorted wing
  parses correctly).
- cquarry opens the DB strictly read-only by its own contract, consistent
  with section 7.
- Caching: wing name -> id set, keyed on `metadata.db` mtime; any library
  change invalidates on the next request.
- UI: a "Wings" sidebar section listing wings with counts; `/wings/<name>`
  renders the standard book grid filtered by `Books.id.in_(ids)`.
- Wings are read-only views. Creating/editing wings happens in the library
  workflow (Calibre preferences / curation SQL), never from the web.
- Dependency note: cquarry is installed editable from
  `~/.gitrepos/CalibreQuarry`. This is the first cross-project consumption
  of cquarry's search engine; it is a standing candidate for the
  library-graduation conversation if it grows.

## 9. Testing

- Fork tests live in `calibre-web-smallscope/tests/` (upstream keeps its
  test suite in a separate repo, so this directory is ours), `unittest`
  style, mirroring CalibreQuarry's conventions.
- Fixture: a generated `metadata.db` whose table schema is dumped from a
  real Calibre library (`tests/calibre_schema.sql`; tables only, no
  triggers so inserts need no `title_sort`, FTS and custom_column tables
  excluded), plus hand-written cc2 (enumeration) and cc5 (bool) columns
  and a `preferences` row with wing expressions including a `vl:`
  cross-reference. Regenerate the dump if a future Calibre migration
  changes the schema.
- Harness: boots the real app (`create_app`) in a sandbox `CALIBRE_DBPATH`,
  mirrors `main()`'s blueprint registration (keep in sync on rebases), and
  must stop the updater/APScheduler threads in `tearDownModule` (they are
  non-daemon and otherwise hang the interpreter at exit).
- Coverage contract: enum linked-query projection (5.2/5.3), Read/Unread
  filters, the write-guard (toggle endpoint refuses), wing evaluation and
  mtime cache invalidation, and Flask test-client smoke checks (detail page
  renders the badge; `/wings/<name>` renders; disabled routes 404).
- Never test against the real library with anything write-capable. Read-only
  verification against the real library is allowed and expected (section 10).

## 10. Verification (per phase, against the real library)

1. Server up via `~/calibre-web-env/bin/cps`; browse, search, open a book,
   read an EPUB.
2. Read status: badge matches known books (cross-check with
   `cquarry --search 'tags:... and #reading_status:...'`); Read/Unread section
   counts correct; toggle endpoint returns the refusal error.
3. Wings: web counts match `cquarry --wings` exactly.
4. Integrity: `metadata.db` checksum identical before/after a full browse
   session; `validate_library.py` stays at 0 errors.

## 11. Non-goals

- No writes to `metadata.db`, ever (section 7).
- No Kobo/KOReader sync, no email/send-to-device, no uploads, no web
  metadata editing, no shelves, no public registration.
- No multi-library support; this is purpose-built for one library.
- No upstreaming pressure: patches are shaped for this instance first.
  Anything genuinely general (enum read-column support) may be offered
  upstream later, but that is opportunistic, not a goal.
