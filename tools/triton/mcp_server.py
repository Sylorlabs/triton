#!/usr/bin/env python3
"""MCP server exposing Triton design automation to AI agents."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, Optional

from .client import TritonAgent, _repo_root

# Lazy import so `zagctl test engine` works without mcp installed.
def _mcp():
    try:
        from mcp.server import Server
        from mcp.server.stdio import stdio_server
        from mcp import types
    except ImportError as e:
        raise SystemExit(
            "MCP SDK not installed. Run: pip install mcp\n"
            "Or use the CLI directly: ./zagctl place plate 6 0 10"
        ) from e
    return Server, stdio_server, types


def run_mcp(zagpa: Optional[Path] = None, cwd: Optional[Path] = None) -> int:
    Server, stdio_server, types = _mcp()
    agent = TritonAgent(zagpa=zagpa, cwd=cwd or _repo_root(), persistent=True)
    agent.start()
    server = Server("triton")

    def _text(resp) -> list[types.TextContent]:
        body = resp.text or ("ok" if resp.ok else "error")
        if not resp.ok:
            body = f"ERROR: {body}"
        return [types.TextContent(type="text", text=body)]

    async def _cmd(line: str):
        return await asyncio.to_thread(agent.command, line)

    @server.list_tools()
    async def list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name="triton_command",
                description="Run any native Triton agent command (place, route, sim, save, ...). See triton_help.",
                inputSchema={
                    "type": "object",
                    "properties": {"command": {"type": "string", "description": "Full agent command line"}},
                    "required": ["command"],
                },
            ),
            types.Tool(
                name="triton_help",
                description="List all native agent commands and component kinds.",
                inputSchema={"type": "object", "properties": {}},
            ),
            types.Tool(
                name="triton_demo",
                description="Load the built-in reference photonic processor design.",
                inputSchema={"type": "object", "properties": {}},
            ),
            types.Tool(
                name="triton_list",
                description="List all components and waveguides in the current design.",
                inputSchema={"type": "object", "properties": {}},
            ),
            types.Tool(
                name="triton_place",
                description="Place a component on the 250nm lattice. Kinds: plate, chamber, soh, emitter, detector.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "kind": {"type": "string"},
                        "x": {"type": "integer"},
                        "y": {"type": "integer"},
                        "z": {"type": "integer"},
                        "rot": {"type": "integer", "default": 0},
                    },
                    "required": ["kind", "x", "y", "z"],
                },
            ),
            types.Tool(
                name="triton_route",
                description="Route a waveguide from an output port to an input port (A* over free lattice).",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "from_comp": {"type": "integer"},
                        "from_port": {"type": "integer"},
                        "to_comp": {"type": "integer"},
                        "to_port": {"type": "integer"},
                    },
                    "required": ["from_comp", "from_port", "to_comp", "to_port"],
                },
            ),
            types.Tool(
                name="triton_sim_step",
                description="Advance the 110 GHz balanced-ternary wave simulation by n symbols.",
                inputSchema={
                    "type": "object",
                    "properties": {"n": {"type": "integer", "default": 1}},
                },
            ),
            types.Tool(
                name="triton_sim_state",
                description="Show live trit states on emitters, chambers, detectors, and waveguides.",
                inputSchema={"type": "object", "properties": {}},
            ),
            types.Tool(
                name="triton_save",
                description="Save the current design to a .zpa file.",
                inputSchema={
                    "type": "object",
                    "properties": {"path": {"type": "string"}},
                    "required": ["path"],
                },
            ),
            types.Tool(
                name="triton_open",
                description="Open a .zpa design file.",
                inputSchema={
                    "type": "object",
                    "properties": {"path": {"type": "string"}},
                    "required": ["path"],
                },
            ),
            types.Tool(
                name="triton_render",
                description="Render a BMP screenshot of the current design.",
                inputSchema={
                    "type": "object",
                    "properties": {"path": {"type": "string"}},
                    "required": ["path"],
                },
            ),
            types.Tool(
                name="triton_test",
                description="Run engine, smoke, or full build verification.",
                inputSchema={
                    "type": "object",
                    "properties": {"name": {"type": "string", "enum": ["engine", "smoke", "build"]}},
                    "required": ["name"],
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
        args = arguments or {}
        if name == "triton_command":
            resp = await _cmd(args["command"])
        elif name == "triton_help":
            resp = await _cmd("help")
        elif name == "triton_demo":
            resp = await _cmd("demo")
        elif name == "triton_list":
            resp = await _cmd("list")
        elif name == "triton_place":
            rot = args.get("rot", 0)
            resp = await _cmd(
                f"place {args['kind']} {args['x']} {args['y']} {args['z']} {rot}"
            )
        elif name == "triton_route":
            resp = await _cmd(
                f"route {args['from_comp']} {args['from_port']} {args['to_comp']} {args['to_port']}"
            )
        elif name == "triton_sim_step":
            resp = await _cmd(f"sim step {args.get('n', 1)}")
        elif name == "triton_sim_state":
            resp = await _cmd("sim state")
        elif name == "triton_save":
            resp = await _cmd(f"save {args['path']}")
        elif name == "triton_open":
            resp = await _cmd(f"open {args['path']}")
        elif name == "triton_render":
            resp = await _cmd(f"render {args['path']}")
        elif name == "triton_test":
            resp = await _cmd(f"test {args['name']}")
        else:
            return [types.TextContent(type="text", text=f"unknown tool: {name}")]
        return _text(resp)

    async def _main():
        async with stdio_server() as (read, write):
            await server.run(read, write, server.create_initialization_options())

    try:
        asyncio.run(_main())
    finally:
        agent.close()
    return 0