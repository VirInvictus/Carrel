# Roadmap

Phases for calibre-web-kanagawa and the `smallscope` fork branch. Tick boxes
when shipping; details and rationale live in `spec.md`.

## Phase 0: Scaffold (in flight)

- [x] Clone `calibre-web-kanagawa` and `calibre-web-smallscope` into `~/.gitrepos/`
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
- [ ] Rin's account created (Brandon: admin UI, needs a password chosen)
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
      ready (open: his visual pass, Rin's account, DNF/reader-theme eyeball)

## Later / opportunistic

- [ ] Offer enum read-column support upstream (it is generally useful)
- [ ] Homelab deployment notes (September 2026 build): serve from Rin's
      machine against the mirrored library
- [ ] Library-graduation check-in on cquarry's search engine if the fork's
      consumption deepens
