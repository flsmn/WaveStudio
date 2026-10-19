# Application checks and selected evidence

Application source is `0.1.0.dev16`, paired with engine `0.1.0.dev5`. Regression tests, native workflow checks, numerical validation, performance measurements and human accessibility acceptance have different scopes. Their outcomes must not be conflated. Current open work is maintained in [ROADMAP.md](../docs/ROADMAP.md).

## Run checks

From the application repository with the development environment activated:

```sh
python -m pytest tests ../WaveSimulator2D/tests -q
python -m wave_studio --check-workflow local-results/workflow
python -m wave_studio --check-performance local-results/performance --performance-case two_views_performance --performance-warmup 15 --performance-seconds 30 --accessibility-for-check
python scripts/check_balanced_resources.py --output-dir local-results/balanced
```

Workflow checks operate real Qt widgets/worker programmatically. `QT_QPA_PLATFORM=offscreen` is appropriate for software checks, not native interaction/AX acceptance. The performance and Balanced runners need actual MPS hardware. Native bundle checks use the executable documented in [DEVELOPMENT.md](../docs/DEVELOPMENT.md).

Additional backend, representative-resource, quality/preflight and large-grid scripts live in `scripts/`. Their default outputs now go to ignored `local-results/`. The quality runner uses the shared engine `validation/mac-presets-v1.json`; its historical demonstrations do not release new presets. The opt-in event/GC tracer requires an explicit output path and is diagnostic instrumentation, not replacement acceptance.

Frozen acceptance criteria are preserved in [MAC_ACCEPTANCE_PLAN.md](plans/MAC_ACCEPTANCE_PLAN.md) and [BALANCED_MAC_PLAN.md](plans/BALANCED_MAC_PLAN.md). The engine owns its numerical policies and independent reference studies.

## Evidence index

| Evidence | Scope |
| --- | --- |
| [Native dev16 workflow](results/native-dev16/workflow-results.json), [build](results/native-dev16/build-results.json) | Recorded bundle imports, workflow and supplied-wheel/source checks; no new native AX or physics release |
| [CPU/MPS](results/backend-results.json), [representative resources](results/resource-results.json) | Historical recorded backend and 512² observations; versions and actual limits are in the reports |
| [Slit](results/quality-slit-results.json), [lens](results/quality-lens-results.json) | Historical grids and v1 criteria; not revised-preset quantitative certification |
| [Dev13 AX](results/native-dev13/accessibility-results.json), [rejected Qt 6.8 crash](results/native-dev13/qt68-crash-summary.json) | Property Undo/Redo improvement, structural outline failure and unsuccessful dependency comparison |
| [Dev13 distribution inventory](results/native-dev13/mac-distribution-audit.json) | Static arm64/minimum-OS/license metadata for that build; not independent clean-machine acceptance |
| [Dev8 resource failure](results/performance/balanced-resource-dev8.json), [dev11 resource failure](results/performance/dev11-resources-quiet/resource-results.json) | Unchanged 250-ms GUI-gap criterion remains failed |
| [Fixed-layout baseline](results/performance/frozen-matched-off.json), [scoped activity](results/performance/frozen-matched-on.json), [historical pump](results/performance/frozen-matched-pump.json) | Historical context-matched intervals; no statistically established universal speedup |
| [Source interval](results/performance/source-fixed-layout.json), [quiet dev11 package](results/performance/dev11-native-quiet/performance-results.json) | Different application/power contexts; not a directly matched source/package speed comparison |

[manifest.json](results/manifest.json) records original paths, immutable Git links and SHA-256 hashes. All selected raw reports are retained byte-for-byte. Embedded paths, wheel hashes, source hashes and versions describe the original run. Earlier intermediate reports, screenshots and withdrawn build notes remain in Git history; their removal from the current tree does not revise their outcomes.

## Working rules

- Run output goes to `local-results/` (ignored), or an explicitly chosen temporary directory. Do not overwrite selected historical evidence.
- Promote only useful results with version pair, hardware/context, scope and provenance. Preserve failures when they remain relevant; never loosen a criterion after observing a failure.
- Small deterministic inputs belong under `tests/fixtures/`. Tests must not require full historical reports or imply that reading a stored PASS reruns a physical experiment.
- Do not rewrite Git history: the engine's original-recurrence comparison needs historical commits.
