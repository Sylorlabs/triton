# Triton verified release notes

These notes summarize behavior verified by the local safe gate. They are not
based on commit count and they do not imply unrun hardware certification.

## Verified in the current safe gate

- Production binary builds through the supported `../zag/zag-poc/znc` path.
  Evidence: `build-production`.
- Engine, persistence, routing, simulation, parser corpus, and protocol parser
  regression tests pass. Evidence: `engine`, `simulation-properties`,
  `parser-corpus`, `protocol-parser`.
- Native X11 self-test and deterministic captures pass when `DISPLAY` is
  available. Evidence: `x11-live`, `x11-captures`.
- The reference balanced-ternary Flash workload rebuilds, imports through the
  public agent mutation envelope, verifies with zero detector mismatches, and
  byte-compares against maintained canonical artifacts. Evidence:
  `flash-photonic`.
- The maintained reference trace is deterministic across fresh exports.
  Evidence: `deterministic-trace`.
- Agent mutations require idempotency keys and revision preconditions; replay is
  byte-inert. Evidence: `agent-idempotency`, `agent-mutation-envelope`,
  `agent-revision-conflict`.
- MCP exposes schema-described mutation envelopes and specialized wrappers for
  placement, deletion, inspection, export, trace, and Flash import/verification.
  Evidence: `mcp-mutation-envelope`, `mcp-specialized-mutations`,
  `mcp-tool-coverage`.
- The live UI exposes schema-described controls, stable IDs, exact bounds, state,
  screenshot capture, and guarded activation through native agent and MCP paths.
  Evidence: `ui-agent-access`.
- Physical-model schema v2 covers eight device families and 25 provenance-bearing
  inputs; legacy v1 projects remain pinned until explicitly migrated without
  invented evidence. Evidence: `model-schema-migration`, `provenance-units`.
- Unauthorized mutation attempts and outside-root writes are rejected without
  changing project bytes or creating forbidden outputs. Evidence:
  `agent-capability-denial`, `agent-path-confinement`.
- Unsupported physical/performance claims and stale positive marketing phrases
  are rejected by release gates. Evidence: `unsupported-claim-audit`,
  `stale-language-audit`.

## Explicitly not claimed

- No GPU dispatch reliability certification is claimed. GPU memory/submit/compute
  gates are opt-in and are not part of the safe gate.
- No destructive GPU reset/fault certification is claimed on the available RX
  5700 XT because it is also the display GPU.
- No fabricated photonic hardware, silicon, lab measurement, or production
  manufacturing result is claimed.
- Flash source/FIR import and trace inspection are software-simulation tooling;
  their UI does not validate fabricated hardware.
- Move, rotate, disconnect, reroute, close-project, cancellation, and full
  per-tool invalid/unauthorized/conflict matrices are not yet complete.

## Reproduction commands

Run:

```sh
./verify.sh safe
```

For the reference PCU specifically, see
`docs/REPRODUCE_REFERENCE_PCU.md`.
