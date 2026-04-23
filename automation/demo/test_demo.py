"""Pytest wrapper for the 90-second QA demo.

Runs the full demo orchestrator and asserts that it finishes within the
target window and actually exercised defensive validation paths.

Usage:
    pytest automation/demo/ -v -s

`-s` is recommended so the colorized terminal log is streamed live
rather than captured by pytest — that's the output you'll screen-record.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure automation/ is on sys.path for shared conftest + demo_runner import.
_AUTOMATION_ROOT = Path(__file__).resolve().parents[1]
if str(_AUTOMATION_ROOT) not in sys.path:
    sys.path.insert(0, str(_AUTOMATION_ROOT))

import pytest

from demo.demo_runner import DemoRunner  # noqa: E402


# Max wall-clock time we'll tolerate. Target is ~90s; allow a small overrun
# for slow local environments.
MAX_SECONDS = 110.0
# How many 4xx/5xx responses we must observe — proves validation scenes ran.
MIN_ERROR_RESPONSES = 3


@pytest.mark.demo
def test_demo_runs_within_90s():
    """Happy-path for the demo: finishes on time and shows defensive errors."""
    runner = DemoRunner()
    result = runner.run()

    assert result.elapsed_seconds < MAX_SECONDS, (
        f"Demo took {result.elapsed_seconds:.1f}s — expected under {MAX_SECONDS}s."
    )
    assert result.error_count >= MIN_ERROR_RESPONSES, (
        f"Demo only captured {result.error_count} error responses; "
        f"expected at least {MIN_ERROR_RESPONSES} to prove validation scenes fired."
    )
    assert result.request_count > 0, "No requests were observed by the terminal log."
