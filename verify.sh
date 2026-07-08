#!/usr/bin/env bash
# Bootstrap the pure-Zag verification orchestrator.
set -eu
cd "$(dirname "$0")"
ZNC="${ZNC:-../zag/zag-poc/znc}"
rm -f tools/verify.new
"$ZNC" tools/verify.zag -o tools/verify.new
mv -f tools/verify.new tools/verify
exec ./tools/verify "${1:-safe}"
