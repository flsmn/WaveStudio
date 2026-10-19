# Changelog

## 0.1.0 — 19 October 2026

- First experimental macOS Apple Silicon release with a self-contained ZIP, versioned app metadata and SHA-256 checksums.
- Uses engine `0.1.0.dev5`; no numerical stencil or accuracy-policy change.
- Ad-hoc signed, not notarized; native accessibility, quantitative accuracy and independent clean-Mac acceptance remain open.

### Source preparation

- Consolidated requirements, architecture and open work into `docs/REQUIREMENTS.md`, `docs/ARCHITECTURE.md` and `docs/ROADMAP.md`.
- Moved selected historical evidence into `validation/results/` with provenance; removed redundant intermediate artifacts from the checkout.
- Split editor, display and quality regressions and extracted their historical input grids into small test fixtures.
- Packaged examples are the single source of truth. New diagnostic results default to ignored `local-results/`.
- Replaced outdated status documents and per-build notes with this changelog and the validation index.

## 0.1.0.dev16

- Restored physical domain dimensions, editable grid spacing and time-step ratio after withdrawing dev15's pixel-dimension controls.
- Retained compact English inputs, organized toolbars, independent display controls and signed Field/Intensity probe selection.
- Uses engine `0.1.0.dev5`. Selected build/workflow evidence is under `validation/results/native-dev16/`.

## 0.1.0.dev15 — withdrawn

- Introduced unwanted pixel-dimension controls; replaced by dev16. This is not a supported build target.

## 0.1.0.dev13

- Avoided unnecessary scene-outline restyling during physical edits and restored simpler row reconciliation.
- Native property Undo/Redo preserves the outline; structural accessibility defects remain open. Qt 6.8.3 comparison builds crashed and were rejected.

## Earlier development

Added project persistence/recovery, references, geometry editing, dual views, resource budgets and performance diagnostics. Earlier per-build notes, plans and raw intermediate runs remain in Git history. Historical passing demonstrations do not establish current quantitative or cross-platform release acceptance.
