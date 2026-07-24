# Roadmap

Phases for Carrel and the `smallscope` fork branch. Tick boxes
when shipping; details and rationale live in `spec.md`.

## Phase 0: Scaffold (in flight)

- [x] Clone `Carrel` and `Carrel-calibre-web` into `~/.gitrepos/`
- [x] Fork: add `upstream` remote (janeczku/calibre-web), fetch tags, branch
      `smallscope` from tag `0.6.26` (matches the installed release)
- [x] Project framework: README, spec.md, roadmap.md, patchnotes.md, CLAUDE.md,
      .gitignore, LICENSE (GPL-3.0), logo.svg, VERSION, justfile, theme/ stub
- [x] Fork CLAUDE.md (brief; points here for the contract)
- [x] Add both repos to `~/.gitrepos/CLAUDE.md` inventory
- [x] Venv swap: `pip uninstall calibreweb`; fork runs from source
      (`just serve`; the 0.6.26 tree has no src/ layout, editable install is
      not possible). Settings carry over via `CALIBRE_DBPATH=~/.calibre-web`
- [x] Baseline: unmodified fork serves on :8083 with existing settings
      (login page 200, Tornado start clean)
- [ ] Manual baseline pass by Brandon (browse, detail, search, EPUB read)
- [ ] Initial commits in both repos (messages reviewed before committing)

## Phase 1: Kanagawa Dragon theme

- [x] caliBlur color inventory + role mapping (spec §4.3); implemented as a
      regenerable mechanical pass: `scripts/recolor_caliblur.py` parses
      caliBlur.css + caliBlur_override.css and rewrites the marked block in
      the theme sheet (~176 rules; media-query context and !important
      preserved, @keyframes replaced whole). 16 unit tests
- [x] `theme/kanagawa-dragon.css`: `:root` palette + caliBlur variable
      overrides + generated recolor block + hand polish layer
- [x] Cover-forward polish: warm headings (oldWhite), cover radius/shadow/
      hover lift, quiet authors/series, subdued read badge, dragonYellow
      stars, warm links/buttons/focus ring, status-badge classes for Phase 3
- [x] `layout.html`: stylesheet link added after `caliBlur_override.css`
- [x] `just sync-theme` vendoring works; vendored copy in the fork
- [x] logo.svg first draft; `favicon.ico` / `icon.svg` / `icon.png`
      regenerated from it; `config_theme` flipped to caliBlur base
- [ ] Brandon's visual pass (desktop + mobile widths), logo verdict, and
      per-page touch-ups that fall out of it (the generated recolor is
      mechanical; expect a polish iteration)

## Phase 2: Trim the feature surface

- [x] Config baseline applied (spec §6.1): everything was already off except
      `config_embed_metadata`, now 0
- [x] Patch: tasks navbar item removed; tasks blueprint answers 404
- [x] Patch: shelves UI removed (sidebar section, create-shelf, detail-page
      add/remove toolbar); shelf blueprint answers 404. Sidebar slot reserved
      for Wings (Phase 4)
- [x] Patch: send-to-eReader buttons removed from detail page; per-user
      eReader email field removed from user_edit (SMTP admin pane left in
      place: admin-only, inert without recipients; revisit if it grates)
- [x] Kobo per-user fields stay config-gated (invisible with sync off);
      no patch needed
- [x] Patch: Edit Metadata button removed from detail page; editbook
      blueprint (edit/upload/convert ajax) answers 404; uploads also off in
      config
- [x] Patch: mass mark-read buttons removed from book_table
- [x] Registration / magic-link / Goodreads: config-off, and the remotelogin
      blueprint answers 404 (admin config panes left as-is: admin-only)
- [x] Route trimming implemented as `cps/smallscope.py` `trim()`:
      before_request 404 guards installed pre-registration, so `url_for`
      keeps resolving everywhere (rebase-friendly)
- [x] Dropped: multi-account operation. Superseded by Phase 7 (spec §11);
      this instance has one user and no login
- [x] Verify: /tasks, /shelf/*, /admin/book/* return 404; /login renders
      200 themed; auth redirects intact; Jinja syntax pass on all four
      edited templates
- [ ] Brandon's browse pass over the trimmed UI

## Phase 3: Read-only reading_status + read-only hardening

- [x] `admin.py`: accept enumeration columns for `config_read_column`
      (dropdown filter + `check_valid_read_column`)
- [x] `db.py generate_linked_query`: enum branch via the normalized link
      table (idiom: restricted-column filter at db.py:786-809)
- [x] `db.py get_book_read_archived`: the same enum branch; a second
      bool-only query builder the research map missed, found because the
      detail badge showed To Read for a Read book (AttributeError swallowed
      by the except, yielding None)
- [x] `web.py:1644`: enum projection (`== 'Read'`) + raw label for the badge
- [x] `web.py:747-749` and `search.py:145-147`: Read/Unread filters for enum
- [x] `helper.py edit_book_read_status`: write-guard; toggle endpoint refuses
      on enum columns (verified: HTTP 400 with the refusal message)
- [x] `detail.html`: 4-state badge replaces the checkbox; grid read-tick
      condition widened to accept the enum value in index/shelf/author/search
- [x] Harden: `metadata.db` attached read-only (`file:...?mode=ro` + uri
      connect arg) at both attach sites
- [x] Link cc2 in config; verified on a scratch instance with default creds:
      badges exact on Read/Reading/To Read sample books, read section
      paginates to exactly 149 books (matches SQL), metadata.db checksum
      identical before/after, `validate_library.py` 0 errors
- [ ] Brandon: DNF badge eyeball whenever a DNF book exists (none currently
      carry the value)

## Phase 4: Wings

- [x] cquarry installed editable into the venv; its `CalibreDB` is the whole
      integration surface (`get_virtual_libraries()` + `resolve_vl(name)`,
      mode=ro by its own contract)
- [x] `cps/wings.py`: blueprint with mtime-keyed cache, app context
      processor injecting `wings_list` (name + count) into every render
- [x] Sidebar "Wings" section in the old shelves slot; `/wings/<name>`
      (+ `/page/<n>`) renders the standard index grid filtered by id set,
      title-sorted; unknown wings 404
- [x] `index.html` sort header gated off for wings (it builds
      `web.books_list` URLs that cannot exist for a wing; this was a 500)
- [x] Unsorted wing handled (vl: references resolve; empty wing renders)
- [x] Verify (scratch instance): all 32 sidebar counts match
      `cquarry --wings` exactly; Languages Wing page holds exactly its 41
      books; The Tabletop paginates 720/60 to a full page 12; metadata.db
      checksum unchanged

## Phase 5: EPUB reader theme (stretch)

- [x] "Kanagawa" entry in `epub_themes.css` (dragonBlack3 page, dragonWhite
      text) + `read.html` theme selector button and `window.themes` entry
      (oldWhite chrome title), wired identically to the five stock themes
- [ ] Brandon: read a chapter on the Kanagawa reader theme and judge it

## Phase 6: Tests and close-out

- [x] `tests/` in the fork: fixture metadata.db built from a real-library
      schema dump (`tests/calibre_schema.sql`, tables only, no FTS/triggers)
      plus hand-written cc2 enum + cc5 bool columns and wing expressions
      (including a `vl:` cross-reference). Self-cleaning sandbox
      CALIBRE_DBPATH; harness boots the real app via create_app and mirrors
      main()'s blueprint registration, stopping the updater/scheduler
      threads in tearDownModule (they otherwise hang the interpreter)
- [x] 11 tests green in ~0.4s: enum detection, all four badges (incl. DNF,
      which the live library cannot exercise), exact Read/Unread membership,
      toggle refusal + checksum, bool-path-under-mode=ro regression, direct
      SQL write rejected readonly, trimmed routes 404, wings sidebar
      names/counts, exact wing filtering, empty/bogus wings, mtime cache
      invalidation
- [x] Full verification pass (spec §10) performed across Phases 3-4;
      `validate_library.py` 0 errors
- [x] roadmap boxes ticked, patchnotes entries, spec.md synced
- [ ] VERSION 1.0.0 when Brandon signs off the instance as daily-driver
      ready (open: his visual pass, DNF/reader-theme eyeball)

## Phase 7: Single-user (spec §11)

Small, self-contained, no visual change. Lands first because everything after
it is easier to verify without a login round-trip.

- [x] `cps/single_user.py`: `before_request` authenticates the owner when
      `current_user` is anonymous. No `@login_required` decorator is touched
- [x] `/login`, `/logout`, `/register`, `/admin/user/new`, `/admin/usertable`
      answer 404; the Add New User button is gone. `/admin/user/<id>` is
      deliberately kept: it is how the owner edits their own preferences
- [x] Bind `127.0.0.1` via `cps.py -i 127.0.0.1` in the `serve` recipe (the
      address is a CLI flag, not a DB setting, so no fork diff). Verified:
      only `127.0.0.1:8083` listens, the `0.0.0.0` and `[::]` sockets are gone
- [ ] Brandon: update the `cps` shell alias in the dotfiles to pass
      `-i 127.0.0.1` too, or it will still bind every interface
- [x] Tests: 15 green. The harness no longer logs in at all, so every existing
      assertion doubles as a regression guard; commenting out the shim fails
      12 of 15 with redirects to `/login`
- [x] Verify: `/`, `/me`, `/admin/view`, `/admin/user/1` all 200 with no
      cookie; the five sealed paths 404
- [ ] Brandon: a full browse/search/read pass to confirm nothing prompts

## Phase 8: De-caliBlur and the owned stylesheet (spec §4.1, §4.4)

The large one. Reverses part of Phase 1 by design.

- [x] `config_theme` to 0; caliBlur CSS and JS no longer load. The theme link
      moved out of the `g.current_theme == 1` branch so it applies over stock
- [x] Rewrite `theme/kanagawa-dragon.css` against stock templates: `:root`
      tokens, two type registers, ledger idiom, 3px radius
- [x] Delete `scripts/recolor_caliblur.py`, its 24 tests, and the generated
      block; dropped the `regen` and `test-theme` recipes. CI repointed at the
      stylesheet's own invariants (palette closure, serif stack, no caliBlur)
- [x] Cover treatment: shadow, hover lift and 5px radius gone. Note stock
      style.css paints covers at `.container-fluid .book .cover span img`
      (0-3-2), so the override has to meet that specificity
- [x] Topbar as a status line; account link relabelled (it rendered the
      username beside the Settings link, reading "ADMIN ADMIN")
- [x] Sidebar reduced to Wings alone. The Browse loop is removed; the brand
      link returns to the whole library and the palette covers every axis
- [x] Ctrl-K command palette over wings, authors, series, categories:
      `cps/palette.py` + `static/js/palette.js`, ported from Athenaeum,
      6,975 entries, mtime-cached and immutable-cacheable
- [x] Cut Discover, Hot Books, Top Rated: `seal_browse_surfaces()` 404s them
      by path prefix (they share the `/<data>/<sort_param>` rule), sidebar
      bits unset. Dead Login/Register/Logout navbar links removed too
- [x] Font stacks lead with the exact installed families and end in generics;
      CI asserts `"EB Garamond"` never leads
- [x] Verify: both widths render `rgb(18,18,15)`, exactly dragonBlack1. Under
      caliBlur desktop rendered `#3d464f` while mobile rendered warm, so this
      closes the defect that started the phase
- [x] Brand: stock sets `.navbar-brand` to Grand Hotel cursive at
      `#45b29d !important`, the last off-palette colour on the page. Answered
      in kind and moved into the serif register; instance title is now Carrel
- [ ] Brandon: browse pass over the new surface, and a verdict on losing the
      Browse sidebar entirely in favour of Ctrl-K

## Phase 9: Search parity (spec §13)

- [x] Route the search bar through cquarry's `SearchEngine` (`cps/carrel_search.py`,
      rebound on metadata.db's mtime, its own mode=ro connection)
- [x] Advanced search removed: `/advsearch` 404s, navbar link and palette
      entry gone. Its `ilike` semantics disagreed with the engine (spec §13.2a)
- [x] Tests: field prefixes, hierarchical `tags:`, boolean logic and grouping,
      custom-column prefix, malformed input reported not 500, sealed routes.
      26 green. Found the harness never installed `seal_browse_surfaces`, so
      the Phase 8 route cuts had never been exercised either
- [x] Verified against the live library: every row inverted and matches
      cquarry exactly, `#audience:Rin` included

## Phase 10: Statistics (spec §12)

- [x] `cps/stats.py`: headless metric functions returning plain dicts,
      read-only, no formatting. A test asserts the whole payload is
      JSON-serialisable, which is what keeps them honest
- [x] `/statistics`: hero counts, readout rows, hour strip, then ranked
      ledgers for decade, genre, weekday, format, author, series, publisher
- [x] Front-page readout strip, on the whole-library view only (a
      library-wide total beside a filtered wing grid would mislead)
- [x] Degenerate axes are readout rows: rated 2.1%, status 98% To Read,
      source 96% Anna's Archive
- [x] All magnitude on the §4.3 gold ramp; no categorical colour anywhere;
      every row carries its label and value as text
- [x] Tests: metrics against the fixture, 24-bucket hour histogram, decade
      bucketing, and the empty-library divide-by-zero guard. 31 green
- [x] Verify: `metadata.db` md5 identical before and after a full stats
      render (abb47887...)
- [ ] Brandon: browse pass over statistics; `1.0.0` when it is daily-driver
      ready

## Later / opportunistic

- [ ] Offer enum read-column support upstream (it is generally useful)
- [ ] Homelab deployment (September 2026 build): explicitly gated on
      reinstating authentication. Phase 7 removes login and binds
      localhost, so serving any other machine means an authenticating
      reverse proxy in front, or reverting Phase 7. Do not simply
      rebind to 0.0.0.0
- [ ] Library-graduation check-in on cquarry: Phase 9 makes the search bar
      depend on its engine, so consumption HAS deepened (spec §13.3).
      Revisit if a fourth consumer of library metrics appears
