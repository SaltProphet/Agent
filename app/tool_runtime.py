from __future__ import annotations

import ast
import os
import subprocess
import sys
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
    """
    Basic AST-based Python safety checks.
    
    WARNING: This is NOT a secure sandbox for untrusted code. It can be trivially 
    bypassed (e.g., via importlib.import_module, __builtins__ access, or other 
    reflection/introspection methods). This validation is intended ONLY for trusted 
    local development and testing. For untrusted code execution, use proper 
    sandboxing (containers, VMs, namespaces, seccomp).
    """
    tree = ast.parse(code)
    denied_names = {
        "__import__",
        "eval",
        "exec",
        "open",
        "compile",
        "input",
        "breakpoint",
        "__builtins__",
        "globals",
        "locals",
        "vars",
        "dir",
        "getattr",
        "setattr",
        "delattr",
        "hasattr",
    }
    denied_modules = {
        "os",
        "sys",
        "subprocess",
        "socket",
        "pathlib",
        "shutil",
        "http",
        "urllib",
        "requests",
        "importlib",
        "ctypes",
        "multiprocessing",
        "threading",
    }

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
        # Block attribute access to common escape hatches
        if isinstance(node, ast.Attribute) and node.attr in {"__builtins__", "__globals__", "__code__"}:
            raise UnsafeCodeError(f"Attribute access blocked: {node.attr}")


def _safe_env() -> dict[str, str]:
    allowed = {"PATH": os.environ.get("PATH", "")}
    return allowed


def execute_python(code: str, timeout_seconds: int) -> ToolExecutionResult:
    _validate_python(code)
    with tempfile.TemporaryDirectory(prefix="agent_py_") as temp_dir:
        script_path = Path(temp_dir) / "script.py"
        script_path.write_text(code, encoding="utf-8")

        try:
            completed = subprocess.run(
                [sys.executable, "-I", "-B", str(script_path)],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
                env=_safe_env(),
            )
            return ToolExecutionResult(completed.stdout, completed.stderr, completed.returncode)
        except subprocess.TimeoutExpired:
            return ToolExecutionResult("", f"Execution timed out after {timeout_seconds} seconds", 124)


def execute_javascript(code: str, timeout_seconds: int) -> ToolExecutionResult:
    with tempfile.TemporaryDirectory(prefix="agent_js_") as temp_dir:
        script_path = Path(temp_dir) / "script.mjs"
        prelude = """
const process = undefined;
const require = undefined;
const global = undefined;
const fetch = undefined;
"""
        script_path.write_text(prelude + "\n" + code, encoding="utf-8")

        try:
            completed = subprocess.run(
                ["node", "--disallow-code-generation-from-strings", str(script_path)],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
                env=_safe_env(),
            )
            return ToolExecutionResult(completed.stdout, completed.stderr, completed.returncode)
        except subprocess.TimeoutExpired:
            return ToolExecutionResult("", f"Execution timed out after {timeout_seconds} seconds", 124)


def execute_tool(language: str, code: str, timeout_seconds: int) -> ToolExecutionResult:
    if language == "python":
        return execute_python(code, timeout_seconds)
    if language == "javascript":
        return execute_javascript(code, timeout_seconds)
    raise ValueError(f"Unsupported language: {language}")
