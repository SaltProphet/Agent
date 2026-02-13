from __future__ import annotations

import ast
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


class UnsafeCodeError(ValueError):
    pass


@dataclass
class ToolExecutionResult:
    stdout: str
    stderr: str
    exit_code: int


def _validate_python(code: str) -> None:
    tree = ast.parse(code)
    denied_names = {"__import__", "eval", "exec", "open", "compile", "input"}
    denied_modules = {"os", "sys", "subprocess", "socket", "pathlib", "shutil"}

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in denied_modules:
                    raise UnsafeCodeError(f"Import blocked: {alias.name}")
        if isinstance(node, ast.ImportFrom):
            if node.module and node.module.split(".")[0] in denied_modules:
                raise UnsafeCodeError(f"Import blocked: {node.module}")
        if isinstance(node, ast.Name) and node.id in denied_names:
            raise UnsafeCodeError(f"Name blocked: {node.id}")


def execute_python(code: str, timeout_seconds: int) -> ToolExecutionResult:
    _validate_python(code)
    with tempfile.TemporaryDirectory(prefix="agent_py_") as temp_dir:
        script_path = Path(temp_dir) / "script.py"
        script_path.write_text(code, encoding="utf-8")

        completed = subprocess.run(
            ["python3", "-I", str(script_path)],
            cwd=temp_dir,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
        return ToolExecutionResult(
            stdout=completed.stdout,
            stderr=completed.stderr,
            exit_code=completed.returncode,
        )


def execute_javascript(code: str, timeout_seconds: int) -> ToolExecutionResult:
    with tempfile.TemporaryDirectory(prefix="agent_js_") as temp_dir:
        script_path = Path(temp_dir) / "script.mjs"
        # Reduce surface area for accidental host access.
        prelude = """
const process = undefined;
const require = undefined;
const global = undefined;
"""
        script_path.write_text(prelude + "\n" + code, encoding="utf-8")

        completed = subprocess.run(
            ["node", str(script_path)],
            cwd=temp_dir,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
        return ToolExecutionResult(
            stdout=completed.stdout,
            stderr=completed.stderr,
            exit_code=completed.returncode,
        )


def execute_tool(language: str, code: str, timeout_seconds: int) -> ToolExecutionResult:
    if language == "python":
        return execute_python(code=code, timeout_seconds=timeout_seconds)
    if language == "javascript":
        return execute_javascript(code=code, timeout_seconds=timeout_seconds)
    raise ValueError(f"Unsupported language: {language}")
