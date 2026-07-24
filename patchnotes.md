# Patchnotes

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

- Repos established: `calibre-web-kanagawa` (project home) and
  `calibre-web-smallscope` (fork of janeczku/calibre-web; branch
  `smallscope` cut from tag 0.6.26, upstream remote wired).
- Documentation framework: README, spec.md (full contract: palette and
  caliBlur mapping, feature-removal lists, read-only reading_status
  semantics, metadata.db mode=ro guarantee, Wings design, testing
  contract), roadmap.md (Phases 0-6), CLAUDE.md, .gitignore, GPL-3.0
  LICENSE, logo.svg, VERSION, justfile.
- Theme stub: `theme/kanagawa-dragon.css` with the pinned Dragon palette
  as CSS custom properties (palette sourced from kanagawa-dragon-nvim-emacs).
- No fork code changes yet; baseline is stock 0.6.26.
