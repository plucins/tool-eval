# Capgemini executive comparison report: visual redesign plan

Status: Implemented and verified on 2026-10-11.
Date: 2026-10-11.

## Agreed Scope

Restyle the generated, interactive, self-contained HTML comparison for senior
management viewing on a large screen. Keep the comparison tables, group tabs,
tool profiles, filters, tooltips, evidence, and existing data semantics.

Use official public Capgemini logo assets and draw the visual direction from
verified Capgemini AI publications from 2026. The user selected interactive HTML,
not a separate slide deck or a new print/PDF export.

Do not add rankings, recommendations, market scores, narrative AI summaries,
new research, or a claim that this is an official Research Institute publication.
Do not change profile data, research timestamps, freshness calculations, or
distribution-flag logic to make the presentation look better.

## Verified References and Asset Provenance

All local reference paths below are relative to this plan's directory.

| Reference | Source and verified observation |
|---|---|
| Official blue logo | https://www.capgemini.com/wp-content/themes/capgemini2025/assets/images/capgeminiBlue.svg ; discovered in the public Capgemini homepage; downloaded as `capgemini-reference/capgemini-blue.svg`. SVG viewBox is `0 0 285 65`; its explicit blue fill is `#0058AB`. |
| Official white logo | https://www.capgemini.com/wp-content/themes/capgemini2025/assets/images/capgeminiWhite.svg ; downloaded as `capgemini-reference/capgemini-white.svg`. Use the supplied variant without recoloring or reconstructing its paths. |
| AI perspectives 2026 | https://www.capgemini.com/insights/research-library/AI-perspectives-2026/ links directly to https://www.capgemini.com/wp-content/uploads/2026/01/Digital-191226-CRI-AI-research-brief-Davos.pdf . Saved as `capgemini-reference/ai-perspectives-2026.pdf`. |
| AI report observations | Cover and page 4 inspected visually: large light-weight headings, strong blue fields, cyan accents, disciplined spacing, restrained navigation, and organic abstract imagery. `pdffonts` confirms Ubuntu Light, Regular, Medium, and Bold in the PDF. |
| TechnoVision 2026 Financial Services | https://www.capgemini.com/wp-content/uploads/2026/04/TV2026-FS-report_web-Mar-13.pdf ; saved as `capgemini-reference/technovision-fs-2026.pdf`. Cover inspected; `pdffonts` independently confirms Ubuntu variants. Blue ground, white/light headings, cyan year label, and a flowing multi-strand motif. |
| Public website typography | https://www.capgemini.com/wp-content/themes/capgemini2025/public/dist/app.css declares Ubuntu for site typography. Icon-font declarations are not body-font guidance. |
| Brand guidelines portal | https://visualidentity.capgemini.com/ redirects to a login page. No current, publicly accessible brandbook was verified. Do not describe inferred spacing, colors, or components as official brand rules. |
| Ubuntu licensing reference | https://design.ubuntu.com/font confirms the family is openly licensed and links to the font license. Source complete fonts from the publisher/distribution, with their actual license; do not extract subset fonts from PDFs. |

Downloaded logo SHA-256:

- Blue: `7c32998ea3afdfc0f1fede03f824a5b402824e65f5b60ab78553e81936df426c`
- White: `306dda528f78702c4d16ee6c524e0f549e481d3de984d11986619cceb9ec52cb`

Public availability is not a blanket redistribution license. Record logo origin
and trademark ownership separately from open-source font/software licensing.
Confirm permission for the intended branded report and for any repository/package
redistribution before shipping the logo. Do not copy report photography,
illustrations, Research Institute lockups, or a complete publication layout.
The downloaded PDFs are design references, not application assets.

Search summaries returned inconsistent font claims and some incorrect PDF URLs.
Only the directly verified sources above inform the plan.

## Existing Implementation and Visual Findings

- `src/tool_eval/reporting/templates/comparison.html.j2` embeds a hand-authored
  cloud-shaped approximation and a text-rendered Capgemini name, not the official
  wordmark. Replace the complete combination, not just the icon.
- `src/tool_eval/reporting/static/theme-capgemini.css` uses Montserrat and
  `#0070AD`, with gradients, rounded overlapping panels, multiple shadows,
  colored KPI circles, flag chips, and gradient profile avatars.
- The current report was opened locally in a browser at 1512 x 749.
  Computed feature-label size is 11.52px, status text 13.6px, KPI labels 12.48px.
  Group tabs require 1603px in a 1208px track.
- The `.cg-constraint` class styles both primary feature names and ancillary
  constraints. Separate their presentation so raising feature readability does
  not unintentionally overemphasize every constraint.
- The page-level and group-level Bootstrap tabs, filter hooks, and tooltip hooks
  already work through `static/app.js`. Preserve their contracts.
- `reporting/assets.py` verifies assets using `static/checksums.json` and embeds
  fonts. Its existing WOFF2 path matcher can support lowercase Ubuntu filenames;
  SVG embedding needs a small extension rather than a new asset framework.
- `reporting/html.py` supplies a shared renderer and derived summary values.
  Keep data calculations unchanged; any new fields are presentational only.
- `pyproject.toml` already force-includes the static and template directories.
- `static/LICENSES.md` and the template footer currently claim there is no
  official logo and identify Montserrat. These must change with the assets.
- Source changes affect future generation only. The existing file under
  `outputs/comparisons/` must not be treated as automatically updated.

## Design Direction

An executive research-report aesthetic rather than a colorful dashboard:
a compact blue editorial header above calm, white analytical content.
The impression of quality should come from typography, proportion, consistency,
and readable evidence, not from extra decoration.

### Proposed Design Tokens

These are implementation starting values, not a certified Capgemini brandbook.
Only the logo blue and Ubuntu usage have been directly verified as above.

| Role | Proposal |
|---|---|
| Primary brand blue | `#0058AB`, matching the downloaded official blue logo |
| Dark text / supporting navy | `#0B2038` |
| Cyan accent | `#12ABDB`, retained as a proposed accent, not asserted as a current official token |
| Main content surface | `#FFFFFF` |
| Page / secondary surface | `#F4F7FA` |
| Separators | `#DCE5ED` |
| Secondary text | `#526171` |
| Success / partial / missing / uncertain | Distinct restrained semantic tones, verified for contrast; keep labels and glyphs, not color alone |
| Spacing | Consistent 4/8px-derived scale, typically 24-32px between major sections |
| Corners / elevation | Small 4-8px radii; borders first; no stacked decorative shadows |

Typography: Ubuntu 300 for large display headings only; 400 body; 500 controls
and table headings; 700 emphasis and metrics. Bundle only weights actually used.
Use 16-18px core table/body text on desktop, at least 14px secondary readable
details, 40-48px desktop title, and approximately 1.4-1.5 body line-height.
Never shrink type to fit additional tool columns; allow deliberate table scrolling.

### Page Composition

1. **Brand and title:** official white logo on a solid blue field, with a quiet
   title and report metadata. Preserve the logo's native aspect ratio, colors,
   and visible breathing room. No synthetic wordmark, clipped mark, CSS filter,
   or Research Institute endorsement. Keep the header compact enough that the
   comparison starts in the first screen.
2. **AI reference:** at most one subtle, original line/flow treatment or narrow
   blue-to-cyan divider outside the data area. Reference the 2026 publications'
   sense of flow, not their exact artwork. No robots, brains, neon particles,
   copied cover photography, or large decorative background competing with data.
3. **Summary:** replace the five boxed, multicolored cards with a quiet aligned
   metrics strip. Preserve all existing counts and freshness information.
   Make units clear: feature counts and tool-feature status counts are not
   equivalent. Do not invent an executive score.
4. **Navigation:** preserve Comparison / Profiles and group tabs, with one
   consistent active blue treatment, visible keyboard focus, and clear hover.
   Prefer a wrapping group-tab layout with full labels on large screens rather
   than a partially clipped last tab. Use deliberate responsive wrapping or
   scrolling on narrow screens; do not truncate silently.
5. **Comparison table:** increase feature-label and status readability,
   standardize column spacing and vertical alignment, reserve blue for structure
   rather than every cell, and use restrained row separators/zebra contrast.
   Preserve text labels and status glyphs. Keep all tool names exactly as supplied
   by profiles; do not blindly title-case brand names.
6. **Details and warnings:** restyle constraints, tooltip surfaces, freshness
   badges, distribution flags, and warning banners with one hierarchy.
   Keep warnings conspicuous without becoming decorative colored tiles.
   Preserve "Not found" as an evidence status, not a definitive absence claim.
7. **Profiles and footer:** apply the same type scale, section rhythm, and
   restrained metadata treatment to descriptions, use cases, features, facts,
   releases, and links. Remove gradient avatar emphasis and the promotional
   footer card treatment. Keep methodological caveats and license attribution.
   Do not add unsupported confidentiality or publication-authority claims.

## Implementation Plan

### 1. Establish the visual acceptance sample

Use the existing four-tool report as the baseline and preserve it unchanged.
Prepare a newly generated sample from existing profiles, not manually edited HTML.
Capture Comparison, a dense feature group, Profiles, and non-current/unresearched
states. Use deterministic fixtures for test scenarios and keep source data English.

Before polishing all sections, review the new header, metrics strip, navigation,
and one table together at 1920 x 1080. This is the visual decision point; avoid
repeated palette-only tweaks without judging the complete composition.

### 2. Replace branding assets and typography

- Add approved official logo variant(s) to the packaged static directory.
  Downloaded reference copies are available beside this plan.
- Obtain full Ubuntu WOFF2 weights from a traceable, licensed distribution.
  Bundle the actual license and source/version details; do not label Ubuntu
  automatically as SIL OFL because the old Montserrat assets used that license.
- Extend `BundledAssets` and `load_assets` minimally to supply a checksum-verified,
  base64 SVG image URI. Prefer an `<img alt="Capgemini">` over injecting raw SVG
  markup. Inspect logo SVG for scripts, external references, and active content.
- Use repository-standard `ToolEvalError` failures for missing/corrupt logo assets.
  Never fall back silently to the approximate mark or an external URL.
- Update font declarations, checksum manifest, and package attribution together.
  Remove obsolete Montserrat assets only after all actual references are migrated.
- Do not add network calls to the Python renderer, CDN links, or new runtime
  dependencies.

### 3. Restyle the shared report

- Refactor existing theme tokens and component rules in place. Avoid layering
  conflicting overrides or introducing a multi-theme configuration system.
- Replace approximate SVG/text branding in `comparison.html.j2`; remove obsolete
  decorative symbols and header artwork that are no longer used.
- Update the header, metrics, both navigation levels, tables, profile sections,
  status/flag/freshness/constraint treatments, filter, tooltips, and footer.
- Separate primary feature-name styling from secondary constraint styling.
- Preserve IDs and Bootstrap hooks unless an explicit corresponding update is
  needed. If wrapping eliminates a tab scroller, remove only its now-unused
  markup/handler and update the JS checksum; otherwise leave unrelated JS alone.
- Preserve autoescape, StrictUndefined, safe Markdown handling, and source links.
- Read `standards/global/coding-style.md` and
  `standards/global/error-handling.md` before editing Python. Keep changed public
  types explicit and error handling aligned with the existing asset loader.

### 4. Verify measurable behavior and visual quality

Start with existing `tests/test_bundled_assets.py`,
`tests/test_html_rendering.py`, and `tests/test_markdown_sanitization.py`.
Update old font/color expectations rather than keeping obsolete values to satisfy
tests. Add behavior checks in the relevant existing test files for:

- Exact verified logo embedding, meaningful alternative text, and removal of the
  approximate brand symbol.
- Ubuntu embedding, no stale Montserrat references, missing/corrupt logo failures,
  and checksum consistency.
- No external resource loads, including image/font/CSS URLs; safe external
  evidence hyperlinks remain permitted.
- Preservation of summary counts, all status/flag labels, warnings, profile
  sections, and arbitrary tool names / unknown feature-group handling.

Perform browser review with fresh generation, not only string assertions:

- 1920 x 1080, 1440 x 900, 1280 x 720, and a 390px-wide narrow-screen regression.
- Four-tool baseline plus two tools, more tools, long tool/feature names,
  constraints, stale profiles, requires-research states, and missing descriptions.
- At 1920 x 1080, show the title, summary, group controls, table header, and first
  three rows of the baseline group without vertical scrolling.
- Core table text at least 16px and secondary detail at least 14px at desktop
  widths; no clipped content or page-level horizontal overflow. Extra-wide tables
  may scroll inside a clearly usable container instead of shrinking text.
- Text contrast at least 4.5:1 for normal text, 3:1 for qualifying large text;
  essential controls/focus indicators at least 3:1 against adjacent colors.
  Do not use cyan for small text on white unless its measured contrast passes.
- Usable tabs, filter, profile link, and detail tooltips with keyboard as well as
  pointer. Do not make essential explanations hover-only.
- No obscured focused controls at 200% zoom. Honor reduced-motion preferences
  if retained navigation or decorative motion exists.
- Browser reload with networking blocked: logo/fonts/content remain complete;
  external resource requests absent; no new console errors.
- Actual font loading verified through browser font APIs/computed styles, not
  just a CSS declaration. Consistent line breaks, aligned baselines, balanced
  whitespace, correct SVG proportions, and no distracting visual duplication.

If package assets change, inspect the built wheel for the shipped logo, fonts,
licenses, stylesheet, and checksums. Verify loading from the built package.
Escalate beyond the targeted tests if these changes expose wider regressions.

### 5. Documentation and demonstration artifact

Update `src/tool_eval/reporting/static/LICENSES.md`, template attribution, and
the directly relevant README description. Clearly distinguish Capgemini trademark
assets from third-party open-source licenses and original application styling.

Generate a new comparison HTML using the existing CLI contract; check
`.venv/bin/python -m tool_eval compare -h` before invoking it. Preserve the old
report and verify the exact new output path. Do not silently substitute a
historical generation timestamp or hide legitimately stale research.

Keep design-reference PDFs/screenshots in this task's `capgemini-reference/`
directory, not runtime package data. Leave unrelated staged deletions under `.claude/commands/` and `.idea/`
untouched. No commit, rollback, or extra workflow artifacts are implied.

## Applicable Standards

Standards actually read during planning:

- `.flowbit/docs/standards/global/architecture.md`: deterministic offline core;
  keep harness/network activity outside Python; preserve src-layout packaging.
- `.flowbit/docs/standards/global/security.md`: self-contained embedded assets;
  sanitize Markdown, escape data, preserve safe links, and never execute source
  content or copy secrets into HTML.
- `.flowbit/docs/standards/global/minimal-implementation.md`: use the existing
  renderer and lean stack; no new theme engine, dependencies, or tool-specific
  generator changes.
- `.flowbit/docs/standards/global/conventions.md`: English UI and technical
  documentation, lowercase asset filenames, unchanged exact excerpts, and
  documentation updates alongside implementation.
- `.flowbit/docs/standards/testing/test-writing.md`: deterministic offline pytest,
  behavior-oriented tests, shared fixtures, and risk-based coverage. Extend the
  existing reporting test files rather than reorganizing their legacy names.

The documentation index has no project frontend standards. The proposed visual
tokens and accessibility thresholds are task acceptance criteria, not newly
adopted repository-wide standards.

## Standards Compliance Checklist

- [x] Core rendering remains deterministic and offline; no model/network calls.
- [x] All visual resources are embedded and distributed through existing package data.
- [x] New/changed assets have verified checksums and clear source/license records.
- [x] Missing or corrupt required assets fail explicitly using ToolEvalError.
- [x] HTML escaping, StrictUndefined, Markdown sanitization, and safe URLs remain intact.
- [x] No research/profile text is executed or used as trusted raw markup.
- [x] Existing data semantics, counts, caveats, and exact excerpts remain unchanged.
- [x] UI and committed technical documentation remain in English.
- [x] No unnecessary dependencies, generalized theming framework, or per-tool styling logic.
- [x] Python coding-style and error-handling standards read before Python edits.
- [x] Targeted offline tests cover the changed output and failure paths.
- [x] Visual acceptance is checked in a browser, including embedded fonts and logo.
- [x] README, attribution, and asset licenses accurately describe the shipped result.
- [x] Prior report and unrelated worktree changes remain untouched.

## Implementation Results

- Follow-up: removed the visible "About this report & asset licenses" section
  at the user's request. Required font licensing and trademark attribution remain
  in an HTML source comment and the packaged license files, not in the report UI.
- Generated report: `outputs/comparisons/capgemini-executive-comparison-20261011.html`.
  Open directly without a server. Original comparison snapshots were preserved.
- Official white logo is embedded unchanged; Ubuntu 300/400/500/700 Latin and
  Latin Extended are vendored from `@fontsource/ubuntu@5.0.8` with its verified
  Ubuntu Font Licence. Removed obsolete Montserrat assets.
- Retained all data and existing comparison/profile workflows. Group tabs wrap,
  feature names and statuses use 16px text, secondary details use 14px, and all
  tooltip triggers are keyboard-addressable with Escape dismissal.
- Existing freshness warnings are summarized in an expandable banner and remain
  visible through per-profile freshness labels. Four profiles are stale because
  their research dates are in July; no dates were changed to hide this.
- Corrected wheel configuration to exclude automatically discovered asset
  directories before force-including them, preventing duplicate archive entries.
  Verified every packaged schema, template, font, logo, and license byte-for-byte.
- Reporting subset: 47 passing tests. Full regression suite: 222 passing tests.
  Updated the security acceptance test to permit only the trusted embedded logo
  while continuing to reject injected images and event handlers.
- Browser evidence and measured acceptance results are under `verification/`.
- Also read and applied `standards/global/coding-style.md` (typed public surface,
  no dead code) and `standards/global/error-handling.md` (explicit ToolEvalError
  codes for required assets) before Python edits.
- The local pip installation initially lacked a vendored dependency. Restored it
  with `ensurepip` and used isolated declared build dependencies for wheel
  verification; no runtime dependency was added.

## Approval Gate

The user approved this design direction and bounded scope on 2026-10-11 and
subsequently requested implementation through quick-dev. Implementation and
verification are complete.
The public references establish a defensible visual direction, not certified
compliance with a private brandbook. Logo usage/redistribution permission remains
a shipping consideration; no unverified license claim may be added.
