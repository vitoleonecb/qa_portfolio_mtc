"""Terminal logger for the QA demo.

Prints a high-contrast, ANSI-colored stream that is legible when a
screen recorder captures the terminal next to the Playwright browser.

The logger exposes a small surface:

    log = TerminalLog()
    log.scene("Invalid channel rejected", index=3, total=8)
    log.request("POST", "/api/users/login", status=401, ms=87,
                snippet='{"message":"Invalid email/username or password"}',
                tag="source=ui")
    log.bug("BUG-NOTIF-003", "IDOR on notification settings")
    log.note("Token cleared from localStorage")

Error counts (status >= 400) are tracked on the instance so tests
can assert that defensive-validation scenes actually fired.
"""

from __future__ import annotations

import re
import sys
import time
from dataclasses import dataclass, field
from typing import Optional

# --- Snippet sanitization ------------------------------------------------
# Anything printed next to request lines is visible in the screen recording,
# so we proactively redact auth material and PII from response bodies before
# they reach the terminal. This is a belt-and-suspenders layer: even if a new
# response format surfaces a token or email, the recording stays clean.

_REDACT_PATTERNS = [
    # JSON string fields we never want rendered in plain text.
    (re.compile(r'("accessToken"\s*:\s*")[^"]+(")'), r"\1<redacted>\2"),
    (re.compile(r'("token"\s*:\s*")[^"]+(")'), r"\1<redacted>\2"),
    (re.compile(r'("refreshToken"\s*:\s*")[^"]+(")'), r"\1<redacted>\2"),
    (re.compile(r'("email"\s*:\s*")[^"]+(")'), r"\1<redacted>\2"),
    (re.compile(r'("username"\s*:\s*")[^"]+(")'), r"\1<redacted>\2"),
    (re.compile(r'("phone"\s*:\s*")[^"]+(")'), r"\1<redacted>\2"),
    (re.compile(r'("first_name"\s*:\s*")[^"]+(")'), r"\1<redacted>\2"),
    (re.compile(r'("last_name"\s*:\s*")[^"]+(")'), r"\1<redacted>\2"),
    # Bare JWT strings that slipped through (header.payload[.sig]).
    (re.compile(r"eyJ[A-Za-z0-9_\-]+\.eyJ[A-Za-z0-9_\-]+(?:\.[A-Za-z0-9_\-]+)?"), "<jwt-redacted>"),
    # Free-form email addresses outside JSON quotes.
    (
        re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}"),
        "<email-redacted>",
    ),
]


def sanitize_snippet(text: Optional[str]) -> Optional[str]:
    """Strip tokens, emails, usernames, and raw JWTs from a response snippet."""
    if not text:
        return text
    out = text
    for pattern, replacement in _REDACT_PATTERNS:
        out = pattern.sub(replacement, out)
    return out


# --- ANSI helpers ---------------------------------------------------------

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

FG_GREEN = "\033[32m"
FG_YELLOW = "\033[33m"
FG_RED = "\033[31m"
FG_CYAN = "\033[36m"
FG_MAGENTA = "\033[35m"
FG_GREY = "\033[90m"
FG_WHITE = "\033[97m"

BG_GREEN = "\033[42m"
BG_YELLOW = "\033[43m"
BG_RED = "\033[41m"
BG_CYAN = "\033[46m"
BG_MAGENTA = "\033[45m"


def _supports_color(stream) -> bool:
    """Best-effort TTY check. Screen recordings always capture the terminal,
    so we keep color on unless the caller pipes to a file."""
    try:
        return stream.isatty()
    except Exception:
        return False


# --- Logger ---------------------------------------------------------------

@dataclass
class TerminalLog:
    """Colorized stdout logger with error/event counters."""

    use_color: Optional[bool] = None
    stream: object = field(default_factory=lambda: sys.stdout)
    started_at: float = field(default_factory=time.monotonic)
    error_count: int = 0
    request_count: int = 0
    bug_count: int = 0

    def __post_init__(self) -> None:
        if self.use_color is None:
            self.use_color = _supports_color(self.stream)

    # ---- formatting helpers ----
    def _c(self, code: str, text: str) -> str:
        if not self.use_color:
            return text
        return f"{code}{text}{RESET}"

    def _elapsed(self) -> str:
        secs = time.monotonic() - self.started_at
        mm = int(secs // 60)
        ss = int(secs % 60)
        return f"{mm:01d}:{ss:02d}"

    def _timestamp(self) -> str:
        return self._c(FG_GREY, f"[{self._elapsed()}]")

    # ---- public API ----
    def scene(self, title: str, index: Optional[int] = None, total: Optional[int] = None) -> None:
        """Print a full-width scene banner."""
        label = " SCENE "
        if index and total:
            label = f" SCENE {index}/{total} "
        banner = self._c(BOLD + BG_CYAN + FG_WHITE, label)
        body = self._c(BOLD + FG_CYAN, f" {title}")
        bar = self._c(FG_CYAN, "─" * 60)
        self._write("")
        self._write(bar)
        self._write(f"{self._timestamp()} {banner}{body}")
        self._write(bar)

    def note(self, message: str) -> None:
        """Print a neutral narration line."""
        prefix = self._c(FG_MAGENTA, "▸")
        self._write(f"{self._timestamp()} {prefix} {message}")

    def info(self, message: str) -> None:
        """Print a low-emphasis informational line."""
        prefix = self._c(DIM + FG_GREY, "·")
        self._write(f"{self._timestamp()} {prefix} {self._c(DIM, message)}")

    def request(
        self,
        method: str,
        path: str,
        status: Optional[int] = None,
        ms: Optional[float] = None,
        snippet: Optional[str] = None,
        tag: Optional[str] = None,
    ) -> None:
        """Print a single HTTP request/response line."""
        self.request_count += 1
        method_fmt = self._c(BOLD + FG_CYAN, f"{method:<6}")
        path_fmt = self._c(FG_WHITE, path)

        if status is None:
            status_fmt = self._c(DIM, "pending")
            arrow = self._c(DIM, "→")
        else:
            arrow = "→"
            if 200 <= status < 300:
                status_fmt = self._c(BG_GREEN + FG_WHITE + BOLD, f" {status} ")
            elif 400 <= status < 500:
                status_fmt = self._c(BG_YELLOW + FG_WHITE + BOLD, f" {status} ")
                self.error_count += 1
            elif status >= 500:
                status_fmt = self._c(BG_RED + FG_WHITE + BOLD, f" {status} ")
                self.error_count += 1
            else:
                status_fmt = self._c(DIM, f" {status} ")

        parts = [self._timestamp(), method_fmt, path_fmt, arrow, status_fmt]
        if ms is not None:
            parts.append(self._c(FG_GREY, f"({ms:.0f}ms)"))
        if tag:
            parts.append(self._c(DIM + FG_MAGENTA, f"[{tag}]"))
        self._write(" ".join(parts))

        if snippet:
            cleaned = sanitize_snippet(snippet) or ""
            trimmed = cleaned.strip().replace("\n", " ")
            if len(trimmed) > 160:
                trimmed = trimmed[:157] + "..."
            self._write(f"        {self._c(DIM, '↳')} {self._c(FG_GREY, trimmed)}")

    def highlight(self, label: str, value: str) -> None:
        """Render a label/value pair in a highlighted box (used for tokens)."""
        label_fmt = self._c(BG_MAGENTA + FG_WHITE + BOLD, f" {label} ")
        value_fmt = self._c(FG_CYAN + BOLD, value)
        self._write(f"{self._timestamp()} {label_fmt} {value_fmt}")

    def bug(self, bug_id: str, description: str) -> None:
        """Call out a known bug encountered during a scene."""
        self.bug_count += 1
        tag = self._c(BG_RED + FG_WHITE + BOLD, f" {bug_id} ")
        body = self._c(FG_RED + BOLD, description)
        self._write(f"{self._timestamp()} {tag} {body}")

    def success(self, message: str) -> None:
        tag = self._c(BG_GREEN + FG_WHITE + BOLD, " PASS ")
        self._write(f"{self._timestamp()} {tag} {self._c(FG_GREEN, message)}")

    def warn(self, message: str) -> None:
        tag = self._c(BG_YELLOW + FG_WHITE + BOLD, " WARN ")
        self._write(f"{self._timestamp()} {tag} {self._c(FG_YELLOW, message)}")

    def error(self, message: str) -> None:
        tag = self._c(BG_RED + FG_WHITE + BOLD, " FAIL ")
        self._write(f"{self._timestamp()} {tag} {self._c(FG_RED, message)}")

    def outro(self, message: str) -> None:
        bar = self._c(FG_CYAN, "═" * 60)
        self._write("")
        self._write(bar)
        self._write(
            f"{self._timestamp()} "
            f"{self._c(BOLD + BG_CYAN + FG_WHITE, '  DONE  ')} "
            f"{self._c(BOLD + FG_CYAN, message)}"
        )
        self._write(
            f"        "
            f"{self._c(FG_GREY, 'requests=')}{self.request_count}  "
            f"{self._c(FG_GREY, 'errors=')}{self.error_count}  "
            f"{self._c(FG_GREY, 'bugs=')}{self.bug_count}"
        )
        self._write(bar)

    # ---- internals ----
    def _write(self, line: str) -> None:
        self.stream.write(line + "\n")
        try:
            self.stream.flush()
        except Exception:
            pass
