import pytest

from app.tool_runtime import UnsafeCodeError, execute_python


def test_python_runtime_executes_safe_code() -> None:
    result = execute_python("print('ok')", timeout_seconds=3)
    assert result.exit_code == 0
    assert result.stdout.strip() == "ok"


def test_python_runtime_blocks_unsafe_import() -> None:
    with pytest.raises(UnsafeCodeError):
        execute_python("import os\nprint('x')", timeout_seconds=3)
