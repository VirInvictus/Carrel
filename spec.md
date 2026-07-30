# Carrel: Specification

The contract for the Kanagawa Dragon calibre-web theme and its companion fork.
Read this before changing semantics in either repo.

Last revised: 2026-07-24. Companion repo: `Carrel-calibre-web`
(fork of `janeczku/calibre-web`; all code changes live there on the
`smallscope` branch). This repo holds the theme source, the documentation
contract, and glue tooling.

---

## 1. Purpose

A personal web front-end for Brandon's curated Calibre library (7,200+ books,
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
| `Carrel` (this repo) | Theme source (`theme/`), spec, roadmap, patchnotes, glue (`justfile`). The documentation here is the contract for both repos. |
| `Carrel-calibre-web` | Fork of calibre-web. Branch `smallscope`, cut from tag `0.6.26` (the release installed in `~/.local/share/carrel/venv/`). All Python/template/CSS changes are commits on this branch. |

Division of labor: the theme is developed here in `theme/kanagawa-dragon.css`
and vendored into the fork at `cps/static/css/kanagawa-dragon.css` via
`just sync-theme`, so the fork remains self-contained and runnable on its own.
The canonical copy is always this repo; never hand-edit the vendored copy.

Deployment: the calibreweb wheel is uninstalled from the venv and the fork
runs from source (the git tree at tag 0.6.26 has no `src/` packaging layout,
so editable installs are not possible; `python cps.py` is upstream's
supported source-run mode):

```sh
CALIBRE_DBPATH=~/.calibre-web ~/.local/share/carrel/venv/bin/python \
    ~/.gitrepos/Carrel-calibre-web/cps.py
```

`CALIBRE_DBPATH` points at the existing settings directory
(`~/.calibre-web/`: `app.db`, `.key`, logs), so users and configuration
carry over from the wheel install. `app.db` is independent of the library
and safe to touch.

## 3. Base version and upstream policy

- Base: calibre-web `0.6.26` (tag), Python 3.14 venv at `~/.local/share/carrel/venv/`.
- The fork keeps upstream's version number; project identity lives in the
  `smallscope` branch and this repo's `VERSION`.
- Upstream rebases are deliberate, not automatic: fetch upstream, read the
  release notes, rebase `smallscope` onto the new tag, re-run the fork tests,
  re-verify the feature-removal list (section 6) against new UI surface.
- License: GPL-3.0 in both repos (calibre-web is GPL-3.0; the theme targets
  its templates, so everything stays aligned).

## 4. Theme

### 4.1 Mechanism

The theme is an **owned stylesheet over stock calibre-web templates**. caliBlur
is not used: `config_theme` is 0 (stock), `caliBlur.css` and
`caliBlur_override.css` are unlinked, and `theme/kanagawa-dragon.css` is the
single sheet the fork loads.

This is the same move the GTK side of the portfolio made when it dropped
libadwaita: stop overriding a vendor theme and own the surface instead. The
override era is documented in §4.7 for the record.

Consequences, all intended:

- The generated recolor block and `scripts/recolor_caliblur.py` retire. There
  is no vendor palette left to map, so the generator and its tests are removed
  rather than maintained.
- Layout is written against stock templates, which are plainer and far shorter
  than caliBlur's, so selectors get shorter and specificity fights disappear.
- caliBlur's raster backgrounds (`blur-light.png`, averaging `#3a4853`, a cool
  slate applied to `body` at `!important`) go with it. They were unreachable by
  any color-level override and were the single largest source of drift from the
  palette below.

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

### 4.3 The chart ramp (statistics surfaces)

The Dragon palette is deliberately muted, which makes it excellent for prose
and unusable for "color equals category". Measured against the categorical
checks (OKLab, dark surface `#12120f`):

- The six natural accents fail. Worst adjacent pair `#8ba4b0` / `#87a987` is
  ΔE 6.7 for **normal** vision, below the floor of 15, and five of six fall
  under the chroma floor (they read as gray).
- Even a best-case three-hue set chosen for maximum spread fails
  (`#c4746e` / `#658594`, ΔE 15.0 normal, 5.7 protan).

This is a property of Kanagawa, not a tuning problem, so §12 encodes magnitude
with **one sequential ramp** and encodes identity with position and labels:

| Step | Hex | OKLab L | Contrast on `#12120f` |
| --- | --- | --- | --- |
| gold 1 | `#3a3222` | 0.321 | 1.48:1 |
| gold 2 | `#5d5039` | 0.438 | 2.39:1 |
| gold 3 | `#8a7853` | 0.580 | 4.37:1 |
| gold 4 | `#a89571` | 0.678 | 6.44:1 |
| gold 5 | `#c4b28a` | 0.769 | 9.01:1 |

Monotonic in lightness by construction. Steps 3 to 5 clear 4.5:1 and are the
only ones permitted to carry a label directly on the fill.

**Rule: no categorical color anywhere.** Where a chart shows more than one
category, identity comes from position, a direct text label, and a hairline
gap. Color may reinforce; it may never be the sole encoding.

### 4.4 Design principles

The register is **a dark reading room wired into a terminal**: library-forward
prose, instrumentation in a mono voice. The structure is adapted from Brandon's
Athenaeum static site so the two read as one property. Nothing is named after
it, nothing links to it; the borrowing is structural only.

1. **Covers carry the color.** Surfaces stay in the near-black dragonBlack
   range with low-saturation text; the curated covers are the most saturated
   objects on every page. No loud chrome accent (the stock golden `#F9BE03`
   is exactly what we are removing).
2. **Warm, not clinical.** oldWhite headings, dragonOrange/dragonYellow
   accents; the blue/violet side of the palette is for small informational
   touches only.
3. **Ledgers, not cards.** Rows share hairline borders (dragonBlack5) and
   align to a common grid. No filled floating tiles, no drop shadows, no hover
   lift. `--radius` is 3px everywhere. A cover is presented by spacing and
   alignment, not by a raised surface. *(This reverses the Phase 1 cover
   treatment, deliberately.)*
4. **Two type registers.** Prose, titles, and book metadata are set in
   `--serif`; all chrome, labels, counts, nav, and table headers are `--mono`,
   uppercase and tracked. The split is what makes the instrumentation read as
   instrumentation.
5. **Readability beats density.** Still a reading room. §12 is the one
   dashboard surface, and it is built from readout rows rather than gauges.

**Font policy (a documented exception).** Principle 4 names installed families:
`--serif` leads with `"EB Garamond Absinthe"` and `--mono` with
`"JetBrains Mono"`. This is an explicit, bounded exception to the global "never
assume an installed font" rule, permitted only because §11 binds the server to
localhost, making this a single-machine surface exactly like Athenaeum. Both
stacks still end in generic families (`serif`, `ui-monospace`) so the app
degrades rather than breaks. Note that plain `"EB Garamond"` must **not** lead
the stack: on this machine it resolves to Söhne, a sans.

### 4.5 Assets

Project `logo.svg` lives in this repo; the fork's `static/favicon.ico` and
`static/icon.svg`/`icon.png` are regenerated from it.

### 4.6 Reader theming (stretch, Phase 5)

The EPUB reader (`read.html`) has its own theme selector and isolated styles
(`epub_themes.css`); it does not inherit the app theme. A "Kanagawa" reading
theme (dragonBlack1 page, dragonWhite text) is planned as a stretch goal.
PDF/comic/DJVU readers keep their stock styling.

### 4.7 The override era (historical)

Through v0.6.x the theme was an override layer on top of caliBlur, generated by
`scripts/recolor_caliblur.py`: roughly 178 rules whose caliBlur colors were
mapped to Dragon equivalents by role, plus a hand-curated polish layer. It is
recorded here because the approach was sound for its constraints and because
its failure modes are the argument for §4.1:

- **Rasters are unreachable.** caliBlur's page background is a PNG, so no
  color-level generator could ever retheme it.
- **Specificity outranks source order.** caliBlur's selectors are long
  (`.container-fluid .book .meta .title`, 0-4-0), so hand-written polish rules
  were silently losing to generated ones despite loading later.
- **Notation coverage is a trap.** The generator matched `#hex` only, so
  colors written as `rgba()` passed through un-themed and rules containing no
  hex at all were never emitted for review.

None of these are fixable in an override; all of them disappear when the sheet
is owned.

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
that keeps the diff small and rebase-friendly. Users: exactly one, the owner.
Multi-account operation was dropped in favour of §11; there is no content
restriction because there is nobody to restrict.

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

- Fork tests live in `Carrel-calibre-web/tests/` (upstream keeps its
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

1. Server up via `just serve` (or the `cps` alias); browse, search, open a book,
   read an EPUB.
2. Read status: badge matches known books (cross-check with
   `cquarry --search 'tags:... and #reading_status:...'`); Read/Unread section
   counts correct; toggle endpoint returns the refusal error.
3. Wings: web counts match `cquarry --wings` exactly.
4. Integrity: `metadata.db` checksum identical before/after a full browse
   session; `validate_library.py` stays at 0 errors.

## 11. Single-user operation

This instance has exactly one reader. Authentication is therefore removed as a
concept, not merely bypassed.

### 11.1 The contract

- No credential is ever requested. `/login`, `/logout`, and registration
  answer 404 through the same route-disable pattern as §6.2.
- Every request runs as the owning admin account.
- The `user` table and `flask-login` stay in the tree. All 154
  `@login_required` decorators stay exactly where upstream put them.

### 11.2 Mechanism

`cps/single_user.py` registers a `before_request` that authenticates the owner
whenever `current_user` is anonymous. The decorators then pass trivially,
because the request is always authenticated.

This is chosen over deleting the auth layer for one reason: §3 requires the
fork to stay rebase-friendly onto upstream tags, and touching 154 call sites
across 10 modules would make every future rebase a merge conflict. Deleting
`single_user.py` restores stock behaviour exactly.

### 11.3 Exposure

The server binds **`0.0.0.0`**, so the instance is reachable from any device
on the local network (`192.168.2.41:8083`). Since §11.1 removes
authentication entirely, this means **anything on the network can read and
download the whole library and reach the admin configuration pane**.

That is a deliberate decision, recorded here so it is never mistaken for an
oversight. The control is not the bind address: it is that the server is run
only in environments Brandon trusts, and is not left running otherwise. The
threat model is a home network under his control, not a shared or hostile one.

Revision history, because this clause has flipped once already: Phase 7 bound
`127.0.0.1` on exactly the reasoning above. It was rebound on 2026-07-24 for
phone access, with the exposure understood and accepted. If the instance ever
needs to run somewhere untrusted, the honest fixes are reinstating
authentication (delete `cps/single_user.py`) or fronting it with an
authenticating reverse proxy. Do not simply hope the network is friendly.

Note that §4.4's font exception was originally licensed by the localhost
binding. It survives on the narrower ground that this is still a
single-machine surface in practice: the fonts are named for Brandon's own
browser, and every stack ends in a generic family, so any other device
degrades to a system serif and mono rather than breaking.

## 12. Statistics

Two surfaces, both computed live from `metadata.db` under the §7 read-only
guarantee: a compact readout strip on the front page, and a full `/statistics`
page.

### 12.1 What is worth showing

Measured against the real library (7,257 books) rather than assumed. Axes with
a real distribution get a chart; degenerate axes get a one-line readout, because
a chart of a 98%/2% split is a chart that looks broken:

| Charted | Readout only (and why) |
| --- | --- |
| Publication by decade (2453 / 1596 / 1182 / 702 / 439 / 256) | Ratings: 149 of 7,257 rated (2%) |
| Genre spine: Fic 3440, NonFic 3004, Gaming 813, over 426 tags | Reading status: 98% To Read |
| Top authors (5,700), series (804), publishers (1,456) | Source: 96% Anna's Archive |
| Formats: EPUB 4845, PDF 2302, DJVU 99, MOBI 10, AZW3 4 | Date Read: 39 books populated |
| Acquisition strip, 161 days | |
| Hour-of-day acquisition (peak 02:00, 664 books) | |
| Wing composition, reusing §8 | |

These counts are a snapshot taken 2026-07-24 and will drift; they are recorded
to justify the charted/readout split, not as fixtures.

### 12.2 Rendering

Hand-rolled CSS bars and inline SVG. No charting dependency, matching the
"stdlib-lean, no framework" posture of the rest of the portfolio. Every chart
obeys the §4.3 ramp rule: sequential gold for magnitude, position and direct
labels for identity, never color alone.

### 12.3 Boundary

`cps/stats.py` holds headless metric functions returning plain dicts; templates
render them. No metric function prints, formats, or knows about HTML.

cquarry's `modes/stats.py` is **not** reused: it prints ANSI to stdout and is
presentation-coupled. The queries here are written fresh and credit that
lineage. If a fourth consumer of library metrics appears, extracting a headless
metrics layer becomes the right call; three is the point at which it gets
raised, not acted on.

## 13. Search parity

### 13.1 The problem

calibre-web's simple search has no expression grammar. `search_query` in
`cps/db.py` lowercases the term and hands it to FTS5 as a phrase, so every
Calibre-style query is matched as literal text and returns nothing. Measured
against the live library:

| Query | calibre-web | cquarry |
| --- | --- | --- |
| `King` | 61 | 3180 |
| `author:"King"` | **0** | 55 |
| `title:Dune` | **0** | 11 |
| `tags:Fic.Fantasy` | **0** | 1368 |
| `rating:>=4` | **0** | 130 |
| `author:King AND title:Tower` | **0** | 1 |

Verified after the change: every row inverted and now matches cquarry
exactly. `King` 3180, `author:"King"` 55, `title:Dune` 11,
`tags:Fic.Fantasy` 1368, `rating:>=4` 130, `author:King AND title:Tower` 1,
and `#audience:Rin` 244.

### 13.2 The contract

The search bar evaluates through cquarry's `SearchEngine`, the same engine §8
already uses for wing expressions. Field prefixes, boolean logic, grouping,
hierarchical tags, and `vl:` references all behave as they do in Calibre and in
cquarry, including cquarry's documented deviations (stdlib `re`, `unicodedata`
rather than ICU, anchored `tags:`).

A bare term keeps Calibre's semantics: substring across title, authors,
author_sort, series, publisher, tags, and comments. This is why `King` returns
3180 rather than 61; it matches "sorcerer-**king**" and equally "ma**king**"
and "as**king**" inside comments. That breadth is Calibre-faithful and is
accepted as the cost of parity.

Custom columns use Calibre's `#label` syntax and the label is
case-insensitive, so `#audience:Rin`, `#Audience:Rin` and `#audience:"Rin"`
are equivalent. Single quotes are **not** Calibre syntax: its tokenizer
recognises only `"` (`search_query_parser.py:158`), so `#Audience:'Rin'`
searches for those literal characters and finds nothing. That is parity, not
a defect.

A malformed query is a user error, not a 500: the parse failure is caught and
the grammar's own message is shown in place of results.

### 13.2a Advanced search is removed

`/advsearch` answers 404 and its navbar link and palette entry are gone. Its
form built SQLAlchemy filters directly, with `ilike` substring semantics that
disagree with the engine above, most visibly on tags where the engine anchors
the hierarchy. Two grammars answering the same question differently is worse
than one, and the bar subsumes the form: nothing it could express is lost,
while `tags:Fic.Fantasy AND rating:>=4 AND #audience:Rin` was never
expressible in it.

### 13.3 Consequence for the cquarry dependency

This makes the search bar, not just wing evaluation, depend on cquarry. Per the
project rule, that deepening is recorded here rather than passed over: cquarry
is now load-bearing for the primary user-facing interaction. It remains a
single editable install and the only approved dependency.

## 14. Non-goals

- No writes to `metadata.db`, ever (section 7).
- No Kobo/KOReader sync, no email/send-to-device, no uploads, no web
  metadata editing, no shelves, no public registration.
- No multi-library support; this is purpose-built for one library.
- No upstreaming pressure: patches are shaped for this instance first.
  Anything genuinely general (enum read-column support) may be offered
  upstream later, but that is opportunistic, not a goal.
