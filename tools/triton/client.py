"""Native Triton agent client — talks to `zagpa --agent` over stdin/stdout."""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


@dataclass
class AgentResponse:
    ok: bool
    message: str = ""
    lines: List[str] = field(default_factory=list)

    @property
    def text(self) -> str:
        if self.lines:
            return "\n".join(self.lines)
        return self.message


class TritonAgent:
    def __init__(
        self,
        zagpa: Optional[Path] = None,
        cwd: Optional[Path] = None,
        persistent: bool = True,
    ) -> None:
        self.root = cwd or _repo_root()
        self.zagpa = zagpa or (self.root / "zagpa")
        if not self.zagpa.is_file():
            raise FileNotFoundError(f"zagpa not found at {self.zagpa} — run ./build.sh")
        self.persistent = persistent
        self._proc: Optional[subprocess.Popen[str]] = None

    def start(self) -> None:
        if self._proc is not None:
            return
        self._proc = subprocess.Popen(
            [str(self.zagpa), "--agent"],
            cwd=str(self.root),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        banner = self._readline()
        if not banner.startswith("OK ready"):
            raise RuntimeError(f"agent failed to start: {banner}")

    def close(self) -> None:
        if self._proc is None:
            return
        try:
            if self._proc.stdin:
                self._proc.stdin.write("quit\n")
                self._proc.stdin.flush()
            self._proc.wait(timeout=5)
        except Exception:
            self._proc.kill()
        self._proc = None

    def _readline(self) -> str:
        assert self._proc and self._proc.stdout
        line = self._proc.stdout.readline()
        if line == "":
            err = ""
            if self._proc.stderr:
                err = self._proc.stderr.read()
            raise RuntimeError(f"agent closed stdout unexpectedly{': ' + err if err else ''}")
        return line.rstrip("\n")

    def _run_once(self, command: str) -> AgentResponse:
        proc = subprocess.run(
            [str(self.zagpa), "--agent", "--once", command],
            cwd=str(self.root),
            capture_output=True,
            text=True,
            check=False,
        )
        out = proc.stdout.strip().splitlines()
        if not out:
            return AgentResponse(False, proc.stderr.strip() or "no output")
        return self._parse_response(out)

    def _parse_response(self, lines: List[str]) -> AgentResponse:
        head = lines[0]
        if head.startswith("ERR "):
            return AgentResponse(False, head[4:])
        if head == "OK":
            body = lines[1:]
            if body and body[-1] == ".":
                body = body[:-1]
            return AgentResponse(True, lines="\n".join(body) if body else "ok", lines=body)
        if head.startswith("OK "):
            return AgentResponse(True, head[3:])
        return AgentResponse(False, f"unexpected response: {head}")

    def command(self, line: str) -> AgentResponse:
        line = line.strip()
        if not line:
            return AgentResponse(True, "")

        if not self.persistent:
            return self._run_once(line)

        self.start()
        assert self._proc and self._proc.stdin
        self._proc.stdin.write(line + "\n")
        self._proc.stdin.flush()

        first = self._readline()
        if first.startswith("ERR "):
            return AgentResponse(False, first[4:])
        if first.startswith("OK "):
            return AgentResponse(True, first[3:])
        if first != "OK":
            return AgentResponse(False, first)

        block: List[str] = []
        while True:
            row = self._readline()
            if row == ".":
                break
            block.append(row)
        return AgentResponse(True, lines=block)

    def __enter__(self) -> "TritonAgent":
        if self.persistent:
            self.start()
        return self

    def __exit__(self, *_) -> None:
        self.close()


def run_script(path: Path, zagpa: Optional[Path] = None) -> Tuple[int, str]:
    root = path.parent if path.is_absolute() else _repo_root()
    z = zagpa or (_repo_root() / "zagpa")
    proc = subprocess.run(
        [str(z), "--agent", "--script", str(path)],
        cwd=str(_repo_root()),
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.returncode, proc.stdout + proc.stderr