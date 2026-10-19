# macOS distribution status

Source pair: Studio **0.1.0.dev16**, engine **0.1.0.dev5**. The local candidate is `dist/ax-dev16/WaveStudio.app`; the default `dist/WaveStudio.app` is an older historical build. Bundles are ignored local artifacts, not repository downloads. MAC-04/05/06 remain open in [ROADMAP.md](ROADMAP.md).

## Recorded evidence

The [dev16 build](../validation/results/native-dev16/build-results.json) and [workflow report](../validation/results/native-dev16/workflow-results.json) retain supplied-wheel/source checks and the bundle's actual import locations. This is not complete clean-machine, native AX or cross-platform release acceptance.

The selected [dev13 distribution inventory](../validation/results/native-dev13/mac-distribution-audit.json) records 264 Mach-O files, arm64 only, with the highest declared minimum macOS target 26.0.0 in Qt/Shiboken bindings. Static deployment targets do not establish that a bundle works on that OS. The recorded local platform was Apple M1 / 8 GiB / macOS 27.0.1. A final dev16 inventory and independent clean-machine test are still needed before stating a supported minimum.

## Open delivery decisions

- Choose and verify the final Mac architecture/minimum OS on a separate clean installation.
- Decide private/local versus public distribution and the corresponding signing/notarization route. Current candidates are ad-hoc signed for development.
- Reconcile all bundled components, runtime licenses and required notices with final artifacts. Neither project currently includes a selected top-level project license; upstream contributions must be accounted for separately. The retained metadata/hash inventory is not a completed licensing review.
- Verify offline launch, Run/Pause, project roundtrip and PNG/CSV export without user-installed Python or neighbouring sources. Freeze source pair, wheel/bundle hashes and installation instructions together.
- Document an update path; manual download/replacement is allowed for the initial route. An automatic updater is not required.

The bundle excludes validation-only SciPy, OpenCV, Matplotlib, TorchVision/TorchAudio and Qt WebEngine. Recheck final artifacts after dependency changes. Windows/Linux native builds and acceptance remain deferred. Build commands and implementation bounds are in [DEVELOPMENT.md](DEVELOPMENT.md); historical report provenance is in the [validation index](../validation/README.md).
