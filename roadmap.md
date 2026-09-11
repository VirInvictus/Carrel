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
- [x] Initial commits in both repos (messages reviewed before committing)

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

## Phase 7: Single-user (spec §11)

*Naming note, 2026-09-11: the fork carries its own Phase 7, the cquarry
data-layer swap (fork 0.6.30-0.6.39); this repo's Phase 7 is the single-user
shim below. The fork's phase numbers are the fork's own; this file records
both by contract.*

Small, self-contained, no visual change. Lands first because everything after
it is easier to verify without a login round-trip.

- [x] `cps/single_user.py`: `before_request` authenticates the owner when
      `current_user` is anonymous. No `@login_required` decorator is touched
- [x] `/login`, `/logout`, `/register`, `/admin/user/new`, `/admin/usertable`
      answer 404; the Add New User button is gone. `/admin/user/<id>` is
      deliberately kept: it is how the owner edits their own preferences
- [x] Bind `127.0.0.1` via `cps.py -i 127.0.0.1` in the `serve` recipe (the
      address is a CLI flag, not a DB setting, so no fork diff). Verified:
      only `127.0.0.1:8083` listens, the `0.0.0.0` and `[::]` sockets are gone.
      **Reversed on 2026-07-24**: the recipe binds `0.0.0.0` for phone access,
      with the exposure understood and accepted. Read spec §11.3, which carries
      the full revision history, before moving where this runs
- [x] Tests: 15 green. The harness no longer logs in at all, so every existing
      assertion doubles as a regression guard; commenting out the shim fails
      12 of 15 with redirects to `/login`
- [x] Verify: `/`, `/me`, `/admin/view`, `/admin/user/1` all 200 with no
      cookie; the five sealed paths 404

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

## Phase 11: Maintenance sweep (2026-08-09)

Not a feature phase. A full read of this repo (spec, roadmap, README,
stylesheet, justfile, CI, logo) plus the fork's Carrel-owned code, looking for
drift, dead code and contract violations rather than new surface. Findings in
the fork were handed to the agent working there; what came back is under
"Fork" below, including the two items that turned out to be contract
questions this file owns.

Contract drift, where a document contradicted another document or the tree:

- [x] `spec.md` §4.4 licensed the font exception "only because §11 binds the
      server to localhost". §11.3 says `0.0.0.0` and already recorded that the
      exception survives on narrower ground, so §4.4 was the pre-flip text and
      asserted something false about §11. The reasoning is now stated once, in
      §4.4; §11.3 points at it rather than restating it, which is how the two
      drifted apart in the first place
- [x] `README.md` status said v0.9.0 against a `VERSION` of 0.9.1, and predated
      the reader-theme work
- [x] `logo.svg` painted the wave's under-stroke `#658594`, which is not in the
      §4.2 palette. It is Wave-family, and the only place the spec mentions it
      is §4.3's ΔE counter-example: a pair cited as *failing* the categorical
      check. CLAUDE.md rule 4 forbids it; CI never saw the SVG. Now dragonBlue2
      at `opacity: 0.55`, because §4.2 has no blue darker than `#8ba4b0` and
      hand-picking one is the violation itself. Rendered before and after at
      256px to confirm the wave keeps its depth
- [x] Phase 7's `127.0.0.1` boxes above recorded a bind that was reversed on
      2026-07-24. `spec.md` §11.3 carries the revision history; this file did
      not, so read alone it contradicted its own later entries

Stylesheet:

- [x] `#description p` was dead: all three templates spell the id `decription`
      (the upstream typo), which the neighbouring rule already handles, and it
      is on a heading with no `<p>` children either way
- [x] Two `@media (max-width: 767px)` blocks, 260 lines apart, merged into one
- [x] The detail-page metadata rows were styled twice: once scoped under
      `.book-meta`, once unscoped eighty lines later, where the second copy
      silently adds `text-transform: uppercase` and wider tracking. Both copies
      are now scoped and adjacent, and a comment records that they overlap and
      that the second wins on source order, so `.publishing-date` and
      `.real_custom_columns` are uppercase while their siblings are not. Left
      that way deliberately: reconciling it would change the page
- [x] **Resolved 2026-09-02 (Brandon: move the uses up a step).** The
      information-carrying uses moved to `--kngw-gray3` (4.82:1, passes AA):
      the sidebar wing and category counts, `.nav-head`, `.hero-l`, `.ro-k`,
      `.hour-tick`, the `.masthead` readout and its link. black6 keeps the
      genuinely decorative uses (scrollbar hover, placeholders, the category
      disclosure arrow, `.cat-all`, the button-hover border), which is what
      §4.2's "muted/disabled text" role was always fair for. The two status
      colours on black4 are untouched (separate question, not raised by this
      box). Shipped with Phase 12 (Carrel 0.9.6); `check-theme` green.

Tooling:

- [x] The palette guard could only be run by pushing. It moved out of CI's
      inline heredoc into `scripts/check-theme.py`, which both CI and the new
      `just check` run, so the two cannot drift. This is the repo's only Python
      file and is tooling, not application code
- [x] That guard extended to `logo.svg`: it was the other colour-bearing asset
      here and nothing checked it. Verified by reintroducing each violation in
      turn (`#658594` in the logo, a bare `#ff0000` rule, `"EB Garamond"`
      leading the stack) and confirming a non-zero exit each time
- [x] `just check-theme`: `sync-theme` is a one-way copy with no verify, so a
      hand-edit in the fork (forbidden by CLAUDE.md rule 3) was undetectable.
      Diffs the canonical sheet against the vendored copy
- [x] `actions/checkout@v4` to `v5`, retiring the Node 20 deprecation
      annotation. Atrium already moved workspace-wide
- [x] `justfile` repeated `env_var('HOME')` three times
- [x] Run `just sync-theme` to vendor this phase's stylesheet edits into the
      fork. Held back while another agent was working in that tree; done once
      it finished (fork commit `b32654f8`). `just check-theme` now reports the
      vendored copy matches. Checked that merging the two `@media` blocks did
      not drop the mobile statistics rules: `.hero-row`, `.hero-n` and
      `.stat-label` are all in the surviving block

Fork (`Carrel-calibre-web`, commit `a6797c22` on `smallscope`):

The code side swept in parallel. It is summarised here rather than left only
in that repo's history, because two of its findings are contract questions this
file owns and the rest is context for the next sweep.

- [x] Search results ignored the sort the reader picked.
      `render_search_results` took an `order` argument and dropped it, pinning
      every query to `Books.sort` while `search.html` rendered eight sort
      buttons that still marked themselves active. Confirmed by observation
      (five different sort params returned identical ordering), then fixed by
      passing the order through with the series join `authaz`/`authza` need
- [x] CI in the fork linted three of its nine Carrel-owned modules, which is
      how an unused variable and two unformatted files reached the branch.
      Both ruff steps now share one `CARREL_PY` list
- [x] The `metadata.db` mtime-cache idiom was copy-pasted across six modules
      and is now `cps/library_cache.py`. `/statistics` and `/palette-data.js`
      had called `getmtime` outside any guard, so an unreadable library took
      them down with a traceback where every sibling surface degraded; they
      now answer 503 and an empty palette
- [x] The two comments claiming the server binds localhost, which §11.3
      reversed on 2026-07-24. `cps/single_user.py` is the file a reader
      consults before deciding whether the instance is safe where it runs
- [x] Fork tests 33 to 35. Three existing ones did not assert what they
      claimed, including one that sliced on a literal string the rendered page
      never contains

Deliberately not touched, recorded so the next sweep does not re-raise them:

- [x] **Decided against.** Ctrl-K does not index the implied intermediate
      category nodes. Only leaf tags exist as rows in `tags`, so `Fic.Fantasy`
      is browsable in the sidebar tree and unreachable from the palette.
      Brandon was asked directly on 2026-08-09 and chose not to index them:
      the payload cost is not worth destinations that are one click away in
      the sidebar. The related half of that question *was* fixed, so the two
      surfaces no longer disagree about what a category is: palette rows point
      at `/categories/<name>`, the roll-up browser, instead of stock
      calibre-web's exact-tag `/category/stored/<id>`
- [x] **Resolved 2026-09-02 (Brandon: drop the fallbacks).** palette.js's
      eight hardcoded Dragon fallbacks are gone; the injected palette styles
      inherit the sheet's `:root` tokens (the `--mono`/`--radius` generics
      stay, they are not palette copies). A missing token now fails visibly
      instead of silently diverging, and the guard question dissolves:
      nothing second-copies the palette anymore. Shipped with Phase 12
      (fork 0.6.29).- [x] No contrast rule was added in the fork. The `--kngw-black6` question
      above is its only home: the sheet is vendored there and CLAUDE.md rule 3
      forbids hand-editing the copy

## Sign-off: what 1.0.0 waits on

(The per-phase sign-off boxes were consolidated here on 2026-07-24; the
phases above are code-complete.)

Phases 0 through 13 are code-complete (13 is the 2026-09-11 sealing release;
the fork's own phase numbering differs, see the Phase 13 note below).
Everything here needs Brandon's eyes or
hands; none of it is a code task.

- [ ] One browse pass over the whole surface: front page, a wing, a category,
      a detail page, search, and the EPUB reader, at desktop and mobile width.
      This replaces the six per-phase passes that had accumulated
- [ ] Verdict on losing the Browse sidebar entirely in favour of Ctrl-K. It is
      the most opinionated change made, and the easiest to revert
- [ ] Logo verdict. It holds at 64px, works at 32px, and turns to mush at 16px,
      so the favicon wants a simplified variant rather than a resize
- [ ] DNF badge eyeball, whenever a book actually carries the value
- [x] Read a chapter on the Kanagawa reader theme and judge it *(signed off
      2026-08-08: "it looks great", judged on Redshirts chapter 4. The read
      surfaced and fixed the dark-theme flaw where book stylesheets painted
      over the class themes; see patchnotes 0.9.1)*
- [ ] `dotfile-sync` the `.zshrc` change (the `cps` alias now binds
      `0.0.0.0`, matching `just serve`). *(Measured 2026-09-11: the working
      `.zshrc` carries the alias, but the change is still uncommitted drift
      in the dotfiles repo, so the sync itself has not happened.)*
- [ ] `VERSION` 1.0.0 once the instance is signed off as daily-driver ready

## Later / opportunistic

- [ ] Offer enum read-column support upstream (it is generally useful)
- [ ] Homelab deployment (September 2026 build): the instance already binds
      `0.0.0.0` with no authentication (spec §11.3), which is acceptable on a
      trusted home network run on demand. An always-on homelab is a different
      threat model and needs authentication reinstated or an authenticating
      reverse proxy in front. Decide that deliberately, not by inheriting
      this config. *(The auth decision is MADE, 2026-09-11: the LAN-trust
      posture stands, no auth code ships, recorded in spec §11.3; revisit
      only if the instance leaves the LAN. The build itself stays
      Brandon's.)*
- [ ] Library-graduation check-in on cquarry: Phase 9 makes the search bar
      depend on its engine, so consumption HAS deepened (spec §13.3).
      Revisit if a fourth consumer of library metrics appears

## Phase 12: Code Sweep & UX Polish (2026-08-23)
*Context: Found falsy index rendering issues, modal input bleeds, and route guard bypasses.*

### Bugs to Fix
- [x] **Falsy Series Index 0:** Update `cps/series_info.py` and `detail.html` to treat index `0` and `0.0` as explicit values, preventing "Book 0" badges from disappearing. *(Shipped in fork 0.6.29: `is not None` in the module, `is not none` in the template; fixture test pins #0 as int and the 7.5 passthrough.)*
- [x] **Case-Sensitive Route Guards:** Normalize paths with `.lower()` in `seal_browse_surfaces()` to prevent capitalized URL bypasses (e.g. `/Hot/`). *(Shipped in 0.6.29; `/HOT`, `/Hot`, `/Discover` pinned 404.)*
- [x] **Palette Modifier Capture:** Ensure `palette.js` ignores `/` keystrokes if Ctrl, Alt, or Meta are held. *(Shipped in 0.6.29.)*
- [x] **Background Grid Navigation:** Prevent `keynav.js` from intercepting vim keys (j/k) when configuration or book detail modals are open. *(Shipped in 0.6.29: `modal-open` body class + `.modal.in/.show` + native `dialog[open]` guard.)*
- [x] **Docs Sync:** Update README test counts from 33 to 35. *(Done and re-done in 0.6.29: the count had moved again with the new tests; README now says 46 and names the shelf coverage.)*

### Refactoring & Growth
- [x] **Thread-Safe LibraryCache:** Add `threading.Lock()` in `LibraryCache` transitions to prevent race conditions during DB rebuilds. *(Shipped in 0.6.29: `get()`/`invalidate()` serialize; four-concurrent-gets test asserts one build.)*
- [x] **Remove Inline CSS Hexes:** Delete inline Kanagawa fallback hex codes in `palette.js` to rely entirely on the `:root` stylesheet overrides. *(Shipped in 0.6.29; this is the palette.js verdict above, resolved the same way.)*
- [x] **Currently Reading Shelf:** Surface books marked as "Reading" on the front page index. *(Shipped in 0.6.29 as `cps/reading_shelf.py`: the library's own enum is the source of truth, newest-grid page only, absent when unconfigured or empty; joined `CARREL_PY`.)*
- [x] **Prefix Filtering in Ctrl-K:** Support prefix commands (e.g., `a ` for authors) inside the command palette to shrink the 6,975-item haystack. *(Shipped in 0.6.29: `w/a/s/c/p` + space scopes the haystack; the counter reports the shelf; the search fallback sees the full query.)*

## Phase 13: hardening backlog from the 2026-09-08 audit sweep (proposed 2026-09-08, digging only)

*Context: a five-agent adversarial sweep covering BOTH repos (fork security
and the read-only invariant, the cquarry-integration modules, fork tests and
upstream-diff hygiene, the theme guard and CI, and contract-vs-code drift),
prompted by the same-day sweeps of bindery-cli, CalibreQuarry, and cquarry.
No code was changed anywhere; the security agent booted the app in-process
against the fixture DB and probed 44 requests, the integration agent drove
the real routes against hostile fixtures. Findings for the fork are recorded
here because this repo is the contract for both. The headline: the
load-bearing invariants all held (mode=ro proven at the engine level, the
seal normalization-proof, OPDS authenticated, no secrets or book data in
git), but the fork carries eight live routes the seal never met (one of
which can replace the source tree), and the contract is nine fork releases
behind the Phase 7 architecture swap.*

*Verification postscript (2026-09-08, an independent batch re-derived the
sharpest claims; all confirmed, corrections folded in above): the updater
kill chain is two unauthenticated requests with self-mintable CSRF; the
broken wing kills its whole section while the page and the sibling feature
survive; the send chain's full auth passes before the SMTP guard and the
converted file lands in the book folder before the ro commit fails closed;
the fork's favicon.ico and icon.png demonstrably still render the pre-fix
Wave artwork (pixel-histogrammed), and the favicon is served on every page;
every doc-drift claim re-checked, with the 154 corrections noted in the
sync box. The mitigating facts also re-verified: mode=ro holds at the
engine level, and every route proposed for `_SEALED` is confirmed unsealed
today.*

### Fork: seal the surfaces the seal never met

- [x] **Extend `_SEALED` by eight routes (P1).** Probed live from a LAN
      position: `/get_updater_status` with `start=True` resumes the updater
      thread, which replaces the checkout with an upstream release,
      destroying the smallscope patches and stopping the server
      (`cps/admin.py:1537-1563`, `UPDATER_AVAILABLE = True`); the user
      management AJAX trio (`/ajax/listusers`, `/ajax/editlistusers`,
      `/ajax/deleteuser`) survives the UI-layer seal, and deleting the
      owner bricks the room into a redirect loop between two 404s
      (`cps/single_user.py:40-48`, `:69-74`); `/ajax/pathchooser/` is an
      unauthenticated arbitrary directory-listing primitive
      (`cps/admin.py:946`); `/shutdown` is a one-POST LAN DoS
      (`cps/admin.py:140-156`). The full eight:
      `/get_updater_status`, `/get_update_status`, the user trio,
      `/ajax/pathchooser`, `/shutdown`, `/reconnect`. Verification
      sharpened the updater chain (it is two requests: the GET primes the
      updater's `updateFile`; the POST alone dies on an unset attribute)
      and CSRF: it is active in production but self-mintable, a fresh
      client GETs `/admin/view` (200; single_user auto-authenticates),
      harvests the token from the HTML, and posts it back. Every closure
      is a one-line addition to the existing rebase-friendly pattern.
      *(Shipped 2026-09-11, fork 0.6.40 [230c42bc]: one frozenset
      extension plus a `_SEALED_PREFIXES` tuple for the one route that
      takes a path parameter, both in `single_user.py`; method-exact
      regression test including case and trailing-slash variants.)*
- [x] **Kill the send/convert chain structurally (P1).** `/send` is still
      routed (the spec removed only the template entry point); with SMTP
      armed via `/admin/mailsettings` and `kindle_mail` set via `/me`, a
      POST queues `ebook-convert`, which writes a converted file INTO the
      library directory (metadata.db stays safe: the ro commit fails
      closed, but the file lands first) (`cps/web.py:1619`,
      `cps/helper.py:290-301`, `cps/tasks/convert.py`). Stub
      `send_mail`/`convert_book_format` so no config state can re-enable
      it. Related near-miss worth short-circuiting while in there:
      `TaskBackupMetadata` writes `metadata.opf` into book folders and is
      fail-closed today only by operation ORDER
      (`cps/tasks/metadata_backup.py:110-117`).
      *(Shipped 2026-09-11, fork 0.6.40 [b1953382]: both helpers refuse
      before touching the ORM via AST-bounded heredoc patches;
      TaskBackupMetadata.run refuses outright.)*
- [x] **Pin the invariant with a committed regression test.** The sweep
      proved mode=ro holds at the engine level (an UPDATE through
      `calibre_db.session` raises, title intact) and that the single
      pooled connection carries the attach for every request; that proof
      lives only in this audit. Add the PRAGMA `database_list` assertion
      plus the refused-UPDATE probe as tests, so a refactor of the
      StaticPool attach cannot silently widen the connection.
      *(Shipped 2026-09-11, fork 0.6.40 [d4b79ae6]: the UPDATE probe
      already lived in the suite; the PRAGMA `database_list` assertion
      joins it, pinning the calibre + app_settings attaches to the pooled
      connection.)*
- [x] **Close the harness-vs-main drift permanently.** The test harness
      hand-syncs blueprint registration with `cps/main.py` and has drifted
      twice before, once silently voiding the Phase 8 route cuts; gdrive's
      five routes are registered in production but never test-exercised.
      One parity test (parse `register_blueprint` calls from main.py,
      compare against `app.blueprints`) plus a pinned "kobo/oauth/gdrive
      are off" assertion would have caught both. Related unpinned edges:
      `single_user._owner()` returning None (the brick scenario), the
      credential seal against uppercase paths, an OPDS acquisition link
      followed to bytes, and 7 of 11 SEARCH_SORTS keys.
      *(Shipped 2026-09-11, fork 0.6.40 [d4b79ae6]: an ast-based parity
      test compares main.py's registrations with the harness in both
      directions and proved it bites during development; kobo/kobo_auth/
      oauth/gdrive pinned off, gdrive documented as the one
      production-only registration. The related edges ride the other
      boxes: the brick scenario is unreachable while the user trio is
      sealed, uppercase seal paths are test-pinned [230c42bc], OPDS
      acquisition feeds are capped and degrade [b2de603e], SEARCH_SORTS
      stays 11 keys with the unknown-token fallback pinned by the sort
      tests.)*

### Fork: the cquarry integration's failure modes

- [x] **One broken wing or saved search poisons the whole feature, per
      request, forever (P1).** `_resolve_wings` resolves every wing in one
      comprehension and saved searches interpolate names into the grammar,
      so a single renamed/deleted `vl:` target or a saved-search name
      containing a quote breaks the build; the failed build never updates
      the cache mtime, and both sidebar injectors are context processors,
      so every page render pays a full rebuild and the whole affected
      section vanishes: all wings, or all saved searches (verification
      corrected the sweep's first wording: the sibling feature and the
      rest of the sidebar survive, and the page still renders 200; the
      measured cost is a fresh cquarry connection plus re-evaluation of
      every expression on every request, forever, until the entry is
      fixed) (`cps/wings.py:24-52`,
      `cps/saved_searches.py:27-36`, `cps/library_cache.py:124-142`).
      Per-name try/except fault isolation is the highest value-per-line
      change in the fork sweep.
      *(Shipped 2026-09-11, fork 0.6.40 [5c588469]: per-name try/except
      in both resolvers; the broken entry is skipped and logged, siblings
      and cache survive, a later Calibre-side fix arrives on the next
      mtime move. Tests pin a dangling `vl:` wing and a quote-named saved
      search surviving alongside their siblings.)*
- [x] **OPDS hardening (P1/P2).** The OPDS search feed calls `resolve()`
      with no SearchError handling, so any unparseable query 500s (the web
      bar and /basic both degrade gracefully; Moon+ Reader users type
      stray quotes), and it renders ALL matches in one unbounded feed with
      full comments and an N+1 `get_formats` per format, where cquarry
      parity makes broad matches the norm (`cps/opds.py:733-741`,
      `cps/quarry_grid.py:68-89`). Also `int()` on offset query params
      escapes as 500s (`cps/opds.py:93-94` and kin). One helper pass:
      SearchError to empty feed, capped per_page with the existing
      rel="next", `_int_param()`.
      *(Shipped 2026-09-11, fork 0.6.40 [b2de603e]: `_int_param()`
      replaces all 22 bare offset reads (garbage degrades, negatives
      clamp), a bad query renders an empty feed, and the search feed
      pages at the configured books-per-page with feed.xml's existing
      rel="next"; the size N+1 is bounded by the page cap rather than
      removed.)*
- [ ] **Decide the common_filters drift (P3).** cquarry grids skip
      upstream's archived/language/denied-tags filtering; invisible under
      the default single-user config, but archiving a book currently hides
      it from nothing. A spec note or the filters.
      *(Drafted 2026-09-11: spec §6.3's last bullet records the deviation
      and names both answers. The pick is Brandon's: adopt the filters in
      the cquarry-backed grids, or amend §6.3 to call the deviation
      accepted. No code moves until he picks.)*
- [x] **Smaller fork papercuts:** `resolve()` converts every exception
      (including a vanished metadata.db) into "could not parse that
      search"; wing/saved-search URLs are case-sensitive while everything
      beneath is case-insensitive; the vacuous `assertGreaterEqual(..., 0)`
      at `tests/test_smallscope.py:641-643` would pass the exact regression
      its docstring names (should be assertGreater); the
      `TestQuarryExtensions` subclass double-runs all 48 parent tests (108
      executions for 60 unique tests, documented but compounding).
      *(Shipped 2026-09-11, fork 0.6.40 [99bfcc54]: resolve() raises
      SearchError for parse errors and LibraryUnavailable for an
      unreadable library, answered 503 by /search and /basic and by the
      empty feed in OPDS, with anything else propagating unswallowed;
      wing and saved-search URLs match case-insensitively with the
      canonical spelling driving title and active marker; the vacuous
      assertion is assertGreater; the shared client wiring moved to a
      _ClientCase base so collected equals executed.)*

### Fork: rebase hygiene and one licensing smell

- [x] **Revert `cps/clean_html.py` to upstream byte-for-byte.** It is a
      pure whole-file reformat with zero functional change, and the
      reformat stripped upstream's GPL-3.0 license header from third-party
      code. The 0.6.39 patchnote calls it "rewritten from scratch", which
      git disproves (it exists at the 0.6.26 base; the diff is +10/-20);
      the same-day correction commit caught two sibling overclaims and
      missed this one. Fix the file and append a dated correction; decide
      whether the CI lint list (which omits the file) or the ownership
      claim is the one to keep.
      *(Shipped 2026-09-11, fork 0.6.40 [b701913e]: the file is
      byte-identical to 0.6.26 (`git diff 0.6.26 -- cps/clean_html.py` is
      empty) and the 0.6.39 entry carries the dated correction. Brandon's
      micro-call, drafted not decided: (a) keep the CI lint list as it is
      and let the ownership claim die: the file is upstream third-party
      code again, so its omission from `CARREL_PY` is now correct and no
      fork doc claims it; or (b) re-assert ownership someday, which would
      mean actually rewriting the file fork-side and adding it to the lint
      list in the same commit. Nothing to execute unless he picks (b).)*
- [x] **Minimize the `about.py` churn before the next rebase** (~4
      functional lines inside ~60 lines of quote-style reflow), and record
      the rebase posture honestly: web.py (+1310/-730), helper.py
      (+679/-309), opds.py (+471/-188), and the advsearch deletion in
      search.py are the four files that will conflict on any upstream
      touch; main.py/constants.py/admin.py/db.py are the done-right
      counterexamples. The disable-not-delete rule in CLAUDE.md rule 6 and
      spec §6.2 was amended by no one when 0.6.36 deleted advsearch
      (deliberate, patchnoted, contract unamended): amend the contract to
      match the shipped decision.
      *(Shipped 2026-09-11, fork 0.6.40 [b701913e]: about.py is upstream
      plus one import and the cquarry-backed stats() body; the fork's
      CLAUDE.md carries the rebase posture with CURRENT diffstats (the
      audit's numbers were stale: web.py ~2000 changed lines, helper.py
      ~1000, opds.py ~700, search.py ~450 deleted, vs main.py +32,
      constants.py 1, admin.py 6, db.py 36); the contract amendment for
      the advsearch deletion landed in spec §6.2's rule paragraph [8c1432d].)*

### Theme and guard

- [x] **Regenerate the fork's derived logo assets (live palette
      violation).** `cps/static/icon.svg:15` still renders the Wave hex
      `#658594` (the exact 2026-08-09 sin), and icon.png/favicon.ico still
      carry their fork-cut mtimes: the canonical logo.svg was fixed but
      nothing regenerates the derivatives, and no guard sees them
      (spec §4.5 says they "are regenerated from" logo.svg; no recipe
      does). Add a `sync-logo` recipe and have check-theme.py diff the
      fork's icon.svg against logo.svg when the sibling checkout exists.
      *(Shipped 2026-09-11 [Carrel 29df953 + fork 7a8e44b7]: just
      sync-logo cuts icon.svg as a byte copy plus rsvg/ImageMagick
      renders; check-theme diffs icon.svg against logo.svg and caught the
      real drift on its first run; renders eyeballed at 256px and all
      three favicon frames.)*
- [x] **Harden check-theme.py against its two proven bypasses.** `:root`
      is the allowlist source, so declaring `--evil: #ff0000` legalizes it
      (pin the 30-hex spec palette instead); and rgb()/hsl()/named-color
      notations pass the hex-only regex (the same trap spec §4.7 already
      recorded once); plus the rule-before-`:root` extraction poisoning.
      The vendored CSS itself is currently in sync and green.
      *(Shipped 2026-09-11 [29df953]: 31 hexes pinned from spec 4.2 +
      4.3, functional and named notations refused with whole-token
      matching so white-space/grayscale/currentColor/transparent stay
      legal, :root found by regex wherever it sits. Verified Phase 11
      style: each bypass reintroduced and confirmed non-zero, the
      false-positive probe confirmed green.)*

### Release records and contract sync

- [x] **Cut a Carrel contract release for the fork's Phase 7 completion.**
      Carrel's newest entry (0.9.7) narrates fork 0.6.30 "Phase 7 begins";
      the fork then shipped 0.6.31-0.6.39 closing the entire cquarry
      data-layer swap, and no contract document records it: a 0.9.8
      patchnotes entry, a roadmap note, the spec deltas (§5.3's dead
      search.py row, §12.3's "queries written fresh" claim now that stats
      ride cquarry.analytics, §6.2's three new sealed prefixes, the §3
      version clause "the fork keeps upstream's version number" which has
      been false since 0.6.28), and one disambiguating sentence about the
      colliding Phase 7 numbering.
      *(Shipped 2026-09-11 as 0.9.8: the patchnotes entry narrates
      0.6.31-0.6.40, spec §6.3 records the swap, §5.3/§12.3/§6.2/§3 are
      synced [8c1432d], and the disambiguation note sits under this file's
      Phase 7 heading.)*
- [x] **Sync the stale contract lines the drift audit found:** spec §6.2's
      removal table is half false (only the email field was patched out;
      Kobo fields are stock config-gated UI, exactly as roadmap Phase 2
      recorded, and the spec row's own line citations have gone stale);
      fork CLAUDE.md's sealed-surfaces list predates the
      `/table` and `/ajax/listbooks` seals; the 154 figure survives in
      THREE places after the correction pass fixed Carrel's README/spec
      (Carrel's 0.7.0 entry says 154; the fork's `single_user.py:10` has
      the full 154/10 phrase; the fork's README:20 still says 154), and
      the correction itself is half-stale: spec §11.2 still pairs 39 with
      "across 10", the strict decorator count at smallscope HEAD is 42
      across 10 modules, and 154 is defensible only as a substring count
      across 14 modules (the indefensible part is pairing it with
      "10 modules"); §8.2 names a "cquarry v2.6+" floor that
      matches no repo (real floor >=1.11.1) and the deployment venv's
      dist-info still says 1.8.0 against a 1.14.0 editable tree; the
      sign-off section's "Phases 0 through 10" line; the done-but-unticked
      `.zshrc` box; four surviving em-dashes in contract prose plus a
      literal `\u2014` escape in the fork's patchnotes (and note the
      v0.9.7 tag message carries one em-dash verbatim from its entry:
      fixing that means a tag force-push, noted only).
      *(Shipped 2026-09-11 [8c1432d]: the four prose em-dashes recast, the
      6.2 table repainted and the seal lists recorded, the decorator
      counts set to 39 upstream / 42 across 10 at HEAD, the 8.2 floor to
      1.11.1+ editable, the sign-off intro to Phases 0-13, and CLAUDE.md
      synced. The fork-side 154/em-dash survivors shipped in the fork's
      docs commit [fb3cb4aa] and single_user.py now says 39/42 [230c42bc].
      Measured corrections to the audit itself: the `.zshrc` box is NOT
      done (the alias lives in the working file but is uncommitted drift
      in the dotfiles repo), and the venv's dist-info still reads 1.8.0
      against the 1.17.0 editable tree. The v0.9.7 tag-message em-dash
      stays as recorded: fixing it is a force-push call, Brandon's.)*
- [x] **Untagged releases, noted and parked.** Carrel has six (0.9.1-0.9.6)
      and the fork six (0.6.27-0.6.32) pre-discipline releases with
      patchnotes entries but no tags. Per Brandon's 2026-09-08 standing
      decision, pre-workflow history stays as it is; recorded here only so
      the release-record audit is complete. Neither repo publishes
      anywhere, so there is no workflow hazard either way.
      *(Record-only; nothing to execute. Both repos remain tag-on-release
      from 0.9.7 / v0.6.33 onward.)*
- [x] **Pin fork CI's cquarry install** (`@main` today: a sibling-repo push
      can redden fork CI with no fork change; pin to a tag or SHA), and
      note Carrel CI's Python 3.13 pin vs the fork's 3.14 (cosmetic for a
      stdlib-only script).
      *(Shipped 2026-09-11, fork [892ab34d]: pinned to the v1.17.0 tag;
      bump deliberately when adopting a cquarry release. The 3.13-vs-3.14
      note stands as cosmetic, no action.)*

### Remainders routed (2026-09-11, Brandon's decisions)

The three unboxed remainders from the audit, given owning boxes or explicit
waivers per the contract rule that nothing "finishes" informally:

- [ ] **Swap `read_book`'s audio branch off the ORM** (`cps/web.py`
      route at :2096): it still resolves through `get_filtered_book` and
      passes an ORM object to `listenmp3.html`. Work shape from the audit:
      precompute everything in the route from `quarry_grid.build_detail`
      and pass plain template variables; the property-proxy approach
      FAILED here once already (proxies return fresh objects per access,
      so route mutations are lost, NEW-AUDIT Stage 6). When swapping,
      pass `cc=[]` and `books_shelfs=[]` explicitly: listenmp3.html reads
      both and its route never passes them (latent bug the audit noted).
      Same release: flip the 0.6.39 correction note in the fork's
      patchnotes to "done".
- [ ] **`/basic_book` detail is still ORM** (`cps/basic.py:81`
      `get_book_read_archived`); marked low priority. The basic theme is
      the phone fallback; the ORM read is read-only and safe, so this
      moves only when it is in the way of something.
- [x] **Waived: the deferred OPDS items.** The custom-column content
      block needs a cc adapter (quarry_grid's `custom_column_N` accessor
      returns [], and cquarry's books_series_link.extra gap blocks the
      series `.extra`); the Calibre-Companion JSON endpoint wants cquarry
      `get_book_by_uuid` (a recorded 1.12 candidate). Brandon waived both
      on 2026-09-11: KOReader (the only OPDS client here) consumes the
      feeds as they ship, the feeds are now capped and degrade cleanly,
      and neither item has a consumer. Revisit only if a reader app
      actually asks for the cc block or the JSON endpoint.

### Completeness verdict from the sweep

*Close, with one sharp edge. The architecture is right and unusually
well-tested for a fork (108 green tests, the invariants actually pinned),
the read-only promise is real at the engine level, and the theme pipeline
works. But "single-user reading room" is currently one config flag away
from admin-authenticated kobo/sync endpoints on the LAN, eight live routes
were never met by the seal, and the contract documents a product that is
nine releases stale. The fork's completeness work is a sealing release
(an afternoon: eight `_SEALED` lines, the send/convert stub, the parity
and invariant tests) plus the contract catch-up; Carrel's own surface
(theme, guard, docs) needs the sync-logo recipe and the check-theme
hardening. Nothing found threatens the library or the archive: the
destructive classes all failed closed.*
