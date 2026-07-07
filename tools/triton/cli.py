#!/usr/bin/env python3
"""zagctl — CLI for Triton / Zag Photonics Architect agent mode."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .client import TritonAgent, run_script, _repo_root


def _print_response(resp, as_json: bool) -> int:
    if as_json:
        print(json.dumps({"ok": resp.ok, "message": resp.message, "lines": resp.lines}))
    elif resp.lines:
        for line in resp.lines:
            print(line)
    elif resp.message:
        stream = sys.stdout if resp.ok else sys.stderr
        print(resp.message if resp.ok else f"error: {resp.message}", file=stream)
    return 0 if resp.ok else 1


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="zagctl",
        description="Control Triton (zagpa) headlessly — place parts, route waveguides, run sims, tests.",
    )
    p.add_argument("--json", action="store_true", help="emit JSON responses")
    p.add_argument("--zagpa", type=Path, default=None, help="path to zagpa binary")
    p.add_argument("--cwd", type=Path, default=None, help="working directory (default: repo root)")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("repl", help="interactive agent session")

    run_p = sub.add_parser("run", help="execute a script of agent commands")
    run_p.add_argument("script", type=Path)

    once_p = sub.add_parser("cmd", help="run one agent command")
    once_p.add_argument("command", nargs=argparse.REMAINDER, help="e.g. place plate 6 0 10")

    do_p = sub.add_parser("do", help="run multiple commands in one session (state persists)")
    do_p.add_argument("commands", nargs="+", help="agent commands in order")

    for name in ("ping", "help", "demo", "new", "list", "list_files"):
        sub.add_parser(name)

    place_p = sub.add_parser("place", help="place component")
    place_p.add_argument("kind")
    place_p.add_argument("x", type=int)
    place_p.add_argument("y", type=int)
    place_p.add_argument("z", type=int)
    place_p.add_argument("rot", type=int, nargs="?", default=0)

    route_p = sub.add_parser("route", help="route waveguide between ports")
    route_p.add_argument("from_comp", type=int)
    route_p.add_argument("from_port", type=int)
    route_p.add_argument("to_comp", type=int)
    route_p.add_argument("to_port", type=int)

    del_p = sub.add_parser("delete", help="delete component by id")
    del_p.add_argument("id", type=int)

    open_p = sub.add_parser("open", help="open .zpa design")
    open_p.add_argument("path")

    save_p = sub.add_parser("save", help="save .zpa design")
    save_p.add_argument("path")

    sim_p = sub.add_parser("sim", help="simulation control")
    sim_p.add_argument("action", choices=["step", "reset", "state"])
    sim_p.add_argument("n", type=int, nargs="?", default=1)

    render_p = sub.add_parser("render", help="render BMP screenshot")
    render_p.add_argument("path")

    test_p = sub.add_parser("test", help="run engine/smoke/build tests")
    test_p.add_argument("name", choices=["engine", "smoke", "build"])

    mcp_p = sub.add_parser("mcp", help="start MCP server (stdio)")
    mcp_p.add_argument("--transport", default="stdio", choices=["stdio"])

    args = p.parse_args(argv)
    root = args.cwd or _repo_root()

    if args.cmd == "mcp":
        from .mcp_server import run_mcp

        return run_mcp(zagpa=args.zagpa, cwd=root)

    if args.cmd == "run":
        code, out = run_script(args.script.resolve(), zagpa=args.zagpa)
        print(out, end="")
        return code

    if args.cmd == "do":
        with TritonAgent(zagpa=args.zagpa, cwd=root, persistent=True) as agent:
            last = 0
            for line in args.commands:
                resp = agent.command(line)
                last = _print_response(resp, args.json)
            return last

    if args.cmd == "repl":
        agent = TritonAgent(zagpa=args.zagpa, cwd=root, persistent=True)
        agent.start()
        print("triton agent repl (Ctrl-D to exit)", file=sys.stderr)
        try:
            for line in sys.stdin:
                line = line.strip()
                if not line:
                    continue
                resp = agent.command(line)
                code = _print_response(resp, args.json)
                if not resp.ok or line in ("quit", "exit"):
                    return code
        finally:
            agent.close()
        return 0

    # map subcommands to agent lines
    line: str | None = None
    if args.cmd == "ping":
        line = "ping"
    elif args.cmd == "help":
        line = "help"
    elif args.cmd == "demo":
        line = "demo"
    elif args.cmd == "new":
        line = "new"
    elif args.cmd == "list":
        line = "list"
    elif args.cmd == "list_files":
        line = "list_files"
    elif args.cmd == "cmd":
        line = " ".join(args.command)
    elif args.cmd == "place":
        line = f"place {args.kind} {args.x} {args.y} {args.z} {args.rot}"
    elif args.cmd == "route":
        line = f"route {args.from_comp} {args.from_port} {args.to_comp} {args.to_port}"
    elif args.cmd == "delete":
        line = f"delete {args.id}"
    elif args.cmd == "open":
        line = f"open {args.path}"
    elif args.cmd == "save":
        line = f"save {args.path}"
    elif args.cmd == "sim":
        if args.action == "step":
            line = f"sim step {args.n}"
        else:
            line = f"sim {args.action}"
    elif args.cmd == "render":
        line = f"render {args.path}"
    elif args.cmd == "test":
        line = f"test {args.name}"

    assert line is not None
    with TritonAgent(zagpa=args.zagpa, cwd=root, persistent=False) as agent:
        return _print_response(agent.command(line), args.json)


if __name__ == "__main__":
    raise SystemExit(main())