# macOS distribution status

Source pair: Studio **0.1.0**, engine **0.1.0.dev5**. The local candidate is `dist/release-0.1.0/WaveStudio.app`; the default `dist/WaveStudio.app` is an older historical build. Version 0.1 is distributed as an experimental ZIP from [GitHub Releases](https://github.com/flsmn/WaveStudio/releases/tag/v0.1.0); intermediate bundles remain ignored local artifacts. The public artifact is ad-hoc signed and not notarized. MAC-04/05/06 remain open in [ROADMAP.md](ROADMAP.md).

## Recorded evidence

The [dev16 build](../validation/results/native-dev16/build-results.json) and [workflow report](../validation/results/native-dev16/workflow-results.json) retain supplied-wheel/source checks and the bundle's actual import locations. This is not complete clean-machine, native AX or cross-platform release acceptance.

The selected [dev13 distribution inventory](../validation/results/native-dev13/mac-distribution-audit.json) records 264 Mach-O files, arm64 only, with the highest declared minimum macOS target 26.0.0 in Qt/Shiboken bindings. Static deployment targets do not establish that a bundle works on that OS. The recorded local platform was Apple M1 / 8 GiB / macOS 27.0.1. The release includes a fresh static inventory. An independent clean-machine test is still needed before treating the declared minimum as verified compatibility.

## Open delivery decisions

- Choose and verify the final Mac architecture/minimum OS on a separate clean installation.
- Initial distribution uses public GitHub Releases and manual ZIP replacement. Developer ID signing/notarization remains open.
- Reconcile all bundled components, runtime licenses and required notices with final artifacts. Neither project currently includes a selected top-level project license; upstream contributions must be accounted for separately. The retained metadata/hash inventory is not a completed licensing review.
- Verify offline launch, Run/Pause, project roundtrip and PNG/CSV export without user-installed Python or neighbouring sources. Freeze source pair, wheel/bundle hashes and installation instructions together.
- Updates use manual download/replacement. An automatic updater is not required.

The bundle excludes validation-only SciPy, OpenCV, Matplotlib, TorchVision/TorchAudio and Qt WebEngine. Recheck final artifacts after dependency changes. Windows/Linux native builds and acceptance remain deferred. Build commands and implementation bounds are in [DEVELOPMENT.md](DEVELOPMENT.md); historical report provenance is in the [validation index](../validation/README.md).
