#!/usr/bin/env bash
# Bootstrap the pure-Zag verification orchestrator.
set -eu
cd "$(dirname "$0")"
ZNC="${ZNC:-../zag/zag-poc/znc}"
if ! xdpyinfo -display "${DISPLAY:-}" >/dev/null 2>&1; then
    unset DISPLAY
fi
rm -f tools/verify.new
"$ZNC" tools/verify.zag -o tools/verify.new
mv -f tools/verify.new tools/verify
exec ./tools/verify "${1:-safe}"
