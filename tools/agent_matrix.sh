#!/bin/sh
# agent_matrix.sh — exercise the agent command layer across request classes
# (Masterplan Section 8.3) with a focus on the preview (ask-before-write) and
# streaming/cancellation paths. Every advertised class is covered here or by a
# sibling gate: valid=agent-ops, unauthorized=agent-capability-denial,
# conflicting=agent-revision-conflict, replayed=idempotency, invalid/malformed=
# agent-error-codes; this gate adds preview + cancelled + malformed for the new
# commands and re-checks a valid/invalid pair end to end.
set -e
Z=./zagpa
TMP=/tmp/triton_agent_matrix
rm -f /tmp/triton_cancel

fail() { echo "agent-matrix: FAIL: $1" >&2; exit 1; }

# ── preview: ask-before-write, no mutation ──────────────────────────────────
$Z --agent --once 'preview place detector 2 1 6' | grep -q 'PREVIEW place ok' || fail "legal preview not ok"
$Z --agent --once 'preview place plate 99 99 99' | grep -q 'PREVIEW place blocked' || fail "illegal preview not blocked"
$Z --agent --once 'preview delete 4242' | grep -q 'no-such-id' || fail "missing-id delete preview"
# preview leaves the scene unchanged in a live session (chamber id=3 survives)
printf 'preview delete 3\npreview place detector 2 1 6\nlist\n' > "$TMP.tcmd"
N=$($Z --agent "$TMP.tcmd" | grep -c '^C ')
[ "$N" -eq 4 ] || fail "preview mutated the scene (got $N components, want 4)"

# ── streaming progress + safe cancellation ──────────────────────────────────
$Z --agent --once 'simstream 20' | grep -q 'DONE steps=20' || fail "simstream did not finish"
P=$($Z --agent --once 'simstream 20' | grep -c 'PROGRESS')
[ "$P" -ge 5 ] || fail "simstream did not stream progress (got $P lines)"
printf x > /tmp/triton_cancel
$Z --agent --once 'simstream 1000' | grep -q 'CANCELLED step=0' || fail "cancel sentinel not honored"
rm -f /tmp/triton_cancel

# ── malformed requests are rejected with stable codes ───────────────────────
$Z --agent --once 'simstream' | grep -q 'E_SIMSTREAM' || fail "malformed simstream not rejected"
$Z --agent --once 'simstream -5' | grep -q 'E_SIMSTREAM' || fail "negative simstream not rejected"
$Z --agent --once 'preview frobnicate' | grep -q 'E_PREVIEW' || fail "unknown preview subcommand not rejected"
$Z --agent --once 'preview place bogus 1 1 1' | grep -q 'E_PREVIEW unknown kind' || fail "invalid kind not rejected"

# ── valid/invalid tool pair end to end ──────────────────────────────────────
$Z --agent --once 'kinds' | grep -q 'chamber' || fail "valid read tool failed"
$Z --agent --once 'get 999999' | grep -qi 'err' || fail "invalid get not rejected"

echo "agent-matrix: ALL PASS"
