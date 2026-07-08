# Master Plan Progress Ledger

Environment snapshot (2026-07-07): Triton starting commit `1e83207`; Zag
starting commit `807c03d`; compiler SHA-256
`713f3b60dfa07a6e8f2683a06de854ec40de495469a4b9cf0f3a03c40ba5eed6`;
Linux `7.0.11-76070011-generic`; x86-64; X11 `:0`; PowerColor Radeon RX 5700 XT
is the only GPU and drives the display.

| Item | State | Change / evidence | Last result | Next |
|---|---|---|---|---|
| A.inventory | pass | `rg --files`; source/probe/tool inventory recorded during baseline | 69 Zag/Python modules plus scripts/docs identified | Keep updated in evidence index |
| A.compiler | pass | `../zag/zag-poc/znc`, sibling Git commit `807c03d`, SHA above | Supported self-hosted compiler identified | Re-record at release |
| A.single-test-entry | pass | `verify.sh`, `tools/verify.zag` | Pure-Zag orchestrator emits JSON result records | Run safe gate |
| A.baseline-engine | pass | `./verify.sh safe`; `probe/engine_test.zag` | 61 assertions passed after replacing a stale user-specific temp path | Expand persistence fault coverage |
| A.gpu-default-safety | pass | `build.sh`, `tools/verify.zag` | GPU memory and dispatch probes are explicit modes; default does not touch DRM | Keep GPU opt-in |
| F.x11-live-baseline | pass | `./verify.sh safe`; `--x11-selftest` on `DISPLAY=:0` | Motion, modifier, key, button, WM_DELETE, and PutImage round trip passed | Add resize/focus/reopen coverage |
| I.display-gpu-certification | blocked | `lspci`, `/dev/dri`; masterplan 12.1 | Only RX 5700 XT is also the display GPU; destructive reset/fault certification requires a non-display GPU | Complete all bounded non-destructive work; do not fake certification |

Unchecked items in `masterplan.md` remain `not-run` unless this ledger or a
linked dated report gives a more specific state.
