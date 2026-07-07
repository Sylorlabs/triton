#!/usr/bin/env bash
# Build Zag Photonics Architect — 100% Zag, zero C.
set -e
cd "$(dirname "$0")"

ZNC="${ZNC:-../zag/zag-poc/znc}"
if [ ! -x "$ZNC" ]; then
    echo "build: znc not found at $ZNC (set ZNC=/path/to/znc)" >&2
    exit 1
fi

echo "== zagpa (Zag -> native ELF, no cc/ld/libc) =="
rm -f zagpa.new
"$ZNC" src/main.zag -o zagpa.new
mv -f zagpa.new zagpa
./zagpa --mcp-install "$(pwd)"

echo "== agent multi-place + route regression =="
./zagpa --agent examples/agent_demo.tcmd >/dev/null

echo "== engine tests =="
rm -f probe/engine_test.new
"$ZNC" probe/engine_test.zag -o probe/engine_test.new
mv -f probe/engine_test.new probe/engine_test
./probe/engine_test

echo "== X11 pixel packing regression =="
rm -f probe/x11_pixel_pack_test.new
"$ZNC" probe/x11_pixel_pack_test.zag -o probe/x11_pixel_pack_test.new
mv -f probe/x11_pixel_pack_test.new probe/x11_pixel_pack_test
./probe/x11_pixel_pack_test

echo "== headless render smoke =="
./zagpa --smoke probe/smoke_app.bmp

if [ -n "$DISPLAY" ]; then
    echo "== X11 wire-protocol round-trip selftest =="
    ./zagpa --x11-selftest
else
    echo "== (no DISPLAY: skipping X11 selftest) =="
fi

echo "== agent smoke =="
printf 'ping\ndemo\nlist\nquit\n' | ./zagpa --agent >/dev/null

echo "build ok. run:  ./run.sh   agent:  ./zagpa --agent   mcp:  ./zagpa --mcp"