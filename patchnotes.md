# Patchnotes

## 0.9.2 (2026-08-09)

Phase 11, a maintenance sweep. No new surface: a full read of the contract, the
stylesheet, the logo and the tooling, looking for drift and dead code. Nothing
in the running app changes.

- **The spec contradicted itself about the bind address.** §4.4 licensed the
  installed-font exception "only because §11 binds the server to localhost".
  §11.3 has said `0.0.0.0` since 2026-07-24 and already recorded that the
  exception survives on narrower ground, so §4.4 was asserting something false
  about its own spec. The reasoning is now stated once, in §4.4, and §11.3
  points at it instead of restating it. Two copies is how it drifted the first
  time.
- **`logo.svg` was carrying an off-palette colour.** The wave's receding second
  stroke was `#658594`, which is Wave-family and not in the §4.2 table. The
  only place the spec mentions that hex is §4.3's ΔE analysis, as half of a
  pair cited for *failing* the categorical check. It is now dragonBlue2 at low
  alpha, which reads the same and needs no new hex, because §4.2 has no blue
  darker than `#8ba4b0` and hand-picking one is the violation.
- **CI now guards the logo too, and can be run without pushing.** The palette
  check moved out of an inline heredoc into `scripts/check-theme.py`, which
  both CI and the new `just check` run, so they cannot disagree. It gained a
  fourth assertion covering `logo.svg`; the logo had been the one colour-
  bearing asset nothing looked at. `actions/checkout` went to v5.
- **`just check-theme`** diffs the fork's vendored stylesheet against the
  canonical one. `sync-theme` is a one-way copy with no verify, so a hand-edit
  in the fork, which CLAUDE.md forbids, was previously undetectable.
- **Stylesheet.** Dropped a dead `#description p` selector: the id is spelled
  `decription` upstream in all three templates that carry it, and the rule
  above already handles it. Merged the two `@media (max-width: 767px)` blocks
  that sat 260 lines apart. Scoped the detail-page `.publishing-date` and
  `.real_custom_columns` rules under `.book-meta`, which is the only place
  either class appears, and recorded in a comment that they overlap the
  ledger-row rule above and win on source order, so those two rows are
  uppercase at wider tracking while their siblings are not. That disagreement
  is left alone because changing it changes the page.
- **The roadmap's Phase 7 boxes** recorded a `127.0.0.1` bind with no note that
  it was reversed, two screens above an entry saying the opposite.
- Open and not actioned: `--kngw-black6` measures 2.92:1 on the page ground and
  2.65:1 on hover rows, at 10 to 11.5px, wherever it carries information rather
  than decoration. That covers the sidebar wing and category counts, the
  readout keys and the masthead. `roadmap.md` carries the numbers and the
  options; it needs a verdict, not a patch.

## 0.9.1 (2026-08-08)

Reader-theme fix, found during the Phase 5 sign-off read. Selecting any dark
reader theme (Kanagawa included) restyled the chrome but left the book page
white: the class themes style the epub.js iframe's root element, and a book
that ships its own stylesheet (Tor EPUBs declare body background and text
colors) paints right over them. The stock dark and black themes had the same
flaw. `selectTheme` in the fork's `read.html` now also applies
`themes.override()` for background and text color, the inline-important
mechanism font size already used, which epub.js re-applies to every newly
rendered section; the custom theme derives a readable text color from its
background's luminance. Fork suite still green (33 tests).

## 0.9.0 (2026-07-24)

Phase 10: statistics. The last planned phase.

- **`/statistics`**: hero counts, then ranked ledgers for publication decade,
  genre, weekday, format, author, series and publisher. Magnitude rides the
  single gold ramp; identity is position and a direct label. There is no
  categorical colour anywhere, because the Dragon accents fail the categorical
  checks outright (worst adjacent pair delta-E 6.7 for normal vision).
- **Degenerate axes are readouts, not charts.** Rated is 2.1%, status is 98%
  To Read, source is 96% Anna's Archive. Charted, each would be a single
  slice; stated as one line each, they are useful.
- **The 2 a.m. shelf** gets its own hour strip, with the peak named in words
  so the shape is never the only encoding: 02:00, 664 books.
- **Front-page strip**: books, authors, series, rated share, busiest hour, and
  a link through. Only on the whole-library view; beside a filtered wing grid
  a library-wide total would mislead.
- Decades before 1900 bucket into one labelled row. Charted individually they
  were forty rows of one- and two-book decades that flattened the real
  distribution.
- `metadata.db` md5 is identical before and after a full render, so the
  read-only guarantee in spec 7 holds on the new surfaces too.

## 0.8.0 (2026-07-24)

Phase 9: the search bar gains Calibre's grammar. Plus a category browser.

- **Search parity.** The bar evaluates through cquarry's engine instead of
  upstream's FTS5 phrase match, which had no grammar at all and matched every
  field-prefixed query as literal text. Measured against the live library,
  every row inverted: `author:"King"` 0 to 55, `title:Dune` 0 to 11,
  `tags:Fic.Fantasy` 0 to 1368, `rating:>=4` 0 to 130,
  `author:King AND title:Tower` 0 to 1, and `#audience:Rin` 0 to 244. Field
  prefixes, boolean logic, grouping, hierarchical tags, custom columns and
  `vl:` references now behave as they do in Calibre.
- A malformed query reports the grammar's own message instead of silently
  returning nothing. It is a user error, not a 500.
- **Advanced search removed.** Its form built SQLAlchemy filters with `ilike`
  substring semantics that disagreed with the engine, most visibly on tags.
  One grammar or none, and the bar subsumes the form.
- **Category browser**: the dot taxonomy as a collapsible sidebar ledger above
  Wings. Only leaf tags are assigned in this library, so every prefix is
  synthesised as a node and accumulates its descendants, matching the engine's
  hierarchical rule exactly (Fic 3440, Fic.Fantasy 1368, NonFic 3004, all
  equal to cquarry). Ancestors of the active category auto-expand; anything
  else you open persists across page changes.
- Fixed spec subsection numbering left stale by the Carrel rename.

## 0.7.0 (2026-07-24)

Phases 7 and 8: the instance becomes single-user, and the theme stops being
an override.

- **No login.** `cps/single_user.py` authenticates the owner on every
  request, so upstream's 154 `@login_required` decorators pass untouched and
  every future rebase stays clean. `/login`, `/logout`, `/register`,
  `/admin/user/new` and `/admin/usertable` answer 404, and the dead navbar
  links are gone. The server binds `127.0.0.1` only; with no auth, binding
  anything else would hand the library and the admin pane to the network.
- **caliBlur is gone.** `theme/kanagawa-dragon.css` is now a standalone sheet
  over stock templates rather than an override layer, the same move the GTK
  projects made dropping libadwaita. The recolor generator and its 24 tests
  retire with it; CI now guards the stylesheet's own invariants instead.
- **A ledger, not cards.** Hairline rules, 3px radius, and two type
  registers: serif for prose, titles and book metadata, mono for every label,
  count, nav item and table header. Covers lose the shadow, hover lift and
  5px radius; they are presented by alignment and space.
- **Ctrl-K command palette** over 6,975 destinations (authors, series,
  categories, wings, pages), ported from the Athenaeum static site and cached
  on the library's mtime.
- **Trimmed:** Discover, Hot Books and Top Rated 404 and leave the sidebar,
  which is now Wings alone.
- Fixed the last off-palette colour: stock painted the brand teal at
  `!important`.

Both widths now render exactly dragonBlack1. Under caliBlur desktop rendered
a cool `#3d464f` slate while mobile rendered warm, so the two looked like
different themes; that is what began this phase.

## 0.6.1 (2026-07-24)

Theme fixes found by rendering the app and measuring it, rather than
reading the stylesheet.

- The page background was caliBlur's `blur-light.png`, a raster averaging
  `#3a4853` (cool slate) applied to `body` at `!important`. Desktop
  rendered `#3d464f` while the mobile breakpoint correctly rendered
  dragonBlack0, so the two widths looked like different themes. The noise
  grain is kept, the slate plate dropped, and dragonBlack1 shows through.
  The detail page's blurred-cover backdrop lives on `.blur-wrapper` and is
  deliberately untouched.
- `recolor_caliblur.py` matched `#hex` only, so every `rgb()`/`rgba()`
  value passed through un-themed and any rule whose colors were all rgba
  was never emitted for review at all. It now normalizes rgb to hex and
  reuses the existing role map, preserving the alpha channel verbatim.
  Pure black is skipped deliberately: every `rgba(0,0,0,x)` in caliBlur is
  a drop shadow, where black is already correct. 8 new tests, 24 total.
- `.alert-danger` kept caliBlur's orange `#ff5533` at 30% (its background
  was written as rgba, so the generator never saw it). Now dragonRed.
- The cover-placeholder gradients kept a neutral `rgba(50,50,50,.5)` while
  their hex half had become dragonBlack2, blending cool into warm on the
  most cover-forward surface in the theme. Now dragonBlack2 throughout.
- `.btn-danger` was light text on dragonRed at 2.06:1. Near-black on the
  same fill gives 5.65:1 and keeps the destructive signal.
- Book titles rendered dragonWhite instead of the intended fujiWhite: the
  generated `.container-fluid .book .meta .title` (0-4-0) outranks a plain
  `.book .meta .title` (0-3-0) regardless of source order, so the polish
  layer was silently losing. Matched the selector.

The generated block is now free of off-palette color: zero stray hex, zero
stray rgb.

## 0.6.0 (2026-06-11)

Phases 5 and 6: the EPUB reader theme and the test suite.

- EPUB reader gains a "Kanagawa" theme (dragonBlack3 page, dragonWhite
  text, oldWhite chrome) in `epub_themes.css` and the `read.html`
  selector, wired identically to the five stock themes.
- Fork test suite (`tests/`, unittest, 11 tests, ~0.4s): boots the real
  app via `create_app` against a sandboxed fixture library whose schema is
  dumped from a real Calibre metadata.db (`tests/calibre_schema.sql`).
  Covers enum-column detection, all four status badges (including DNF,
  which the live library cannot exercise), exact Read/Unread membership,
  toggle refusal with checksum proof, the bool path failing safely under
  mode=ro, a direct SQL write rejected as readonly, trimmed routes, wings
  names/counts/filtering (including the vl: cross-reference and the empty
  wing), and mtime cache invalidation.
- Harness lessons recorded: create_app's updater/APScheduler threads must
  be stopped in tearDownModule or the interpreter hangs at exit; cli arg
  parsing requires a scrubbed sys.argv; cc_classes needs one forced
  connect before the first request.
- The shell alias pair was updated for run-from-source (`enter-cps`
  absolute path; `cps` now runs the fork with CALIBRE_DBPATH).

## 0.5.0 (2026-06-11)

Phase 4: Wings. The library's 31 virtual libraries (plus Unsorted) are now
first-class browse sections in the web UI.

- New `cps/wings.py`: reads `virtual_libraries` from metadata.db's
  preferences table and evaluates each wing's Calibre search expression
  with CalibreQuarry's engine (`CalibreDB.resolve_vl`, which handles `vl:`
  cross-references, so Unsorted parses). Results cached keyed on
  metadata.db mtime; any library change invalidates on the next request.
- Sidebar "Wings" section (in the slot shelves vacated) with live counts;
  `/wings/<name>` renders the standard cover grid, title-sorted, with
  working pagination; unknown wings 404. The index sort header is gated
  off for wings (it builds section URLs that cannot exist for a wing and
  500d; found in verification).
- cquarry (v2.6+, editable from ~/.gitrepos/CalibreQuarry) becomes the
  fork's one extra dependency. First cross-project consumption of its
  search engine.
- Verified on a scratch instance: all 32 sidebar counts match
  `cquarry --wings` exactly; spot-checked wings hold exactly their books;
  empty wing renders; library checksum unchanged.

## 0.4.0 (2026-06-11)

Phase 3: the library's reading_status, read-only, plus the hard read-only
guarantee.

- The fork now accepts enumeration custom columns as the linked read column
  and the instance links cc2 (`reading_status`). Enum branches added to both
  query builders (`generate_linked_query` AND `get_book_read_archived`; the
  second one was missed by the research map and found when the badge showed
  To Read on a Read book), joining through the normalized link table.
- Detail page shows a read-only 4-state badge (Read / Reading / To Read /
  DNF in Dragon colors) instead of the toggle checkbox; grid read-ticks
  accept the enum value; Read/Unread sections and advanced search project
  Read == 'Read'.
- Write-guard: the toggle endpoint refuses with "Read status is managed in
  Calibre and is read-only here" (HTTP 400).
- metadata.db is now attached `mode=ro` at both attach sites; the web app
  cannot write the library by construction.
- Verified on a scratch instance: badges exact for all three live statuses,
  read section paginates to exactly 149 books (matches SQL), checksum
  identical across a full browse session, validator at 0 errors.

## 0.3.0 (2026-06-11)

Phase 2: the feature surface trimmed to browse / search / read / download.

- New `cps/smallscope.py` in the fork: `trim()` installs before_request 404
  guards on unused blueprints ahead of registration, so `url_for` keeps
  resolving and the diff stays rebase-friendly. Disabled: tasks, shelf,
  editbook, remotelogin.
- Template removals: Tasks navbar item; the entire shelves sidebar section
  and detail-page shelf toolbar (the slot is reserved for Wings);
  send-to-eReader buttons and the per-user eReader email field; the Edit
  Metadata button; mass mark-read radios in the list view.
- Config baseline (spec §6.1) applied; only `config_embed_metadata` needed
  flipping, the rest were already off. Kobo per-user UI stays config-gated.
- Verified: trimmed routes 404, login renders themed, auth redirects
  intact, Jinja syntax pass on all edited templates.

## 0.2.0 (2026-06-11)

Phase 1: the Kanagawa Dragon theme, live on the instance.

- `scripts/recolor_caliblur.py`: stdlib generator that parses caliBlur.css
  (+ caliBlur_override.css) and rewrites the marked recolor block in the
  theme sheet, mapping every hardcoded caliBlur color to its Dragon
  equivalent by role (spec §4.3). ~176 rules; media-query nesting and
  !important flags preserved; @keyframes recolored whole. 16 unit tests
  (`just test-theme`); regenerate with `just regen` after upstream caliBlur
  changes.
- Hand polish layer in `theme/kanagawa-dragon.css`: warm oldWhite headings,
  cover-forward grid treatment (radius, shadow, hover lift), quiet
  author/series text, subdued read badge, dragonYellow rating stars, warm
  links/buttons/focus ring, and `.kngw-status-*` badge classes ready for
  the Phase 3 reading-status display.
- Fork wiring: `kanagawa-dragon.css` linked after `caliBlur_override.css`
  in `layout.html` (vendored via `just sync-theme`); favicon/icon assets
  regenerated from `logo.svg`; instance flipped to the caliBlur base theme
  (`config_theme = 1`).
- justfile: new `regen` and `test-theme` tasks.

## 0.1.0 (2026-06-11)

Project scaffold.

- Repos established: `Carrel` (project home) and
  `Carrel-calibre-web` (fork of janeczku/calibre-web; branch
  `smallscope` cut from tag 0.6.26, upstream remote wired).
- Documentation framework: README, spec.md (full contract: palette and
  caliBlur mapping, feature-removal lists, read-only reading_status
  semantics, metadata.db mode=ro guarantee, Wings design, testing
  contract), roadmap.md (Phases 0-6), CLAUDE.md, .gitignore, GPL-3.0
  LICENSE, logo.svg, VERSION, justfile.
- Theme stub: `theme/kanagawa-dragon.css` with the pinned Dragon palette
  as CSS custom properties (palette sourced from kanagawa-dragon-nvim-emacs).
- No fork code changes yet; baseline is stock 0.6.26.
