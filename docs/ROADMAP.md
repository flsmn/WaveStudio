# Roadmap and current status

Source pair: **Wave Studio 0.1.0 / WaveSimulator2D 0.1.0.dev5**. Local test platform: Apple M1, 8 GiB, macOS arm64. Version 0.1 is published as an experimental macOS release. Broader accuracy, accessibility and cross-platform acceptance remain open. Windows/Linux acceptance remains deferred.

This is the single open-work tracker. Product requirements are in [REQUIREMENTS.md](REQUIREMENTS.md), implementation boundaries in [ARCHITECTURE.md](ARCHITECTURE.md), selected evidence in the [validation index](../validation/README.md), and completed changes in [CHANGELOG.md](../CHANGELOG.md). Historical counts and reports describe their recorded versions, not a permanent current test count.

| Priority / ID | Open work | Completion evidence |
| --- | --- | --- |
| P1 · MAC-01 | Quantitative source/slit/lens accuracy and quality presets | Independent matched references; spatial/time/domain/window/geometry/peak sensitivity; suitable versioned tolerances and a stated uncertainty/scope |
| P1 · MAC-02 | Context-dependent GUI interruptions | Reproduce and fix remaining production-loop/resource gaps; pass the unchanged interaction budgets with matched power/activity/thermal state |
| P2 · MAC-03 | Native accessibility, keyboard and human usability | Stable scene outline after structural/theme/text edits; actual candidate keyboard/focus checks and human VoiceOver acceptance |
| P2 · MAC-04 | Distribution scope and dependencies | Supported Mac architecture/minimum OS tested on another clean machine; public GitHub ZIP/manual-update model, remaining Developer ID signing decision and complete license/attribution inventory |
| P3 · MAC-05 | Freeze final version pair | Matching source, wheels, bundle, hashes and targeted regression/workflow/physics/resource evidence after the above corrections |
| P3 · MAC-06 | Final delivery and acceptance | Offline launch and core workflow without user Python/network on a clean target; documented installation/update path and remaining limitations |

## Known findings to retain

- Independent point-source subcase passes its defined scope; line-window/border sensitivity and full lens complex-profile refinement remain failed. Historical slit/lens demonstration PASS results do not certify arbitrary presets. See the engine's [quantitative progress](../../WaveSimulator2D/docs/QUANTITATIVE_PROGRESS.md).
- The rate-display bug was corrected, but the historical 5–8 versus 18–20 FPS difference has no single proven cause. Resource runs retained 500.86-ms (dev8) and 252.316-ms (dev11) interruptions against a 250-ms criterion. See [performance findings](PERFORMANCE_INVESTIGATION.md).
- Native property Undo/Redo retains the scene outline; adding objects still lost the accessibility outline in dev13. Qt 6.8.3 comparison builds crashed. This is not a full accessibility pass. See [accessibility findings](MAC_ACCESSIBILITY_FOLLOWUP.md).
- Selected dev16 historical bundle workflow/build reports exist; distribution and AX checks from dev13 do not automatically qualify the 0.1 release. The default historical `dist/WaveStudio.app` and the local `dist/release-0.1.0/WaveStudio.app` are not equivalent. The first public ZIP is experimental; it does not close the remaining acceptance work. See [distribution status](MAC_DISTRIBUTION.md).

No unsupported platform, arbitrary grid or untested hardware receives an accuracy/performance guarantee from a historical passing report. An automatic updater is not required for an initial manual distribution route.
