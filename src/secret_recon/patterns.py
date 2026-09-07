"""High-signal secret patterns. Values are never logged by callers."""

from __future__ import annotations

import re
from dataclasses import dataclass


PLACEHOLDER_HINTS = (
    "your-openai-api-key",
    "sk-xxxxxxxx",
    "replace_me",
    "example_key",
    "dummy_token",
    "changeme",
    "xxx",
    "placeholder",
    "not_a_real",
    "sample",
)


ALLOW_PATH_FRAGMENTS = (
    "/test/",
    "/tests/",
    "tests/",
    "/fixtures/",
    "/mocks/",
    "/examples/",
    ".env.example",
    ".env.sample",
    "readme.md",
    "/docs/",
    "docs/",
)


@dataclass(frozen=True)
class Rule:
    id: str
    description: str
    regex: re.Pattern
    severity_hint: str
    entropy_min: float = 3.0


RULES: list[Rule] = [
    Rule("openai-api-key", "OpenAI API key", re.compile(r"sk-[a-zA-Z0-9]{20,}T3BlbkFJ[a-zA-Z0-9]{20,}"), "critical", 3.5),
    Rule("openai-project-key", "OpenAI project-style key", re.compile(r"sk-proj-[A-Za-z0-9_-]{40,}"), "critical", 3.8),
    Rule("openai-generic", "Generic OpenAI-style key", re.compile(r"sk-[a-zA-Z0-9]{48,}"), "high", 3.8),
    Rule("anthropic-api-key", "Anthropic API key", re.compile(r"sk-ant-[a-zA-Z0-9\-_]{80,}"), "critical", 3.5),
    Rule("aws-access-key", "AWS Access Key ID", re.compile(r"(A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}"), "critical", 3.0),
    Rule("cloudflare-api-token", "Cloudflare API token assignment", re.compile(r"(?i)(cloudflare|cf[_-]?api[_-]?token|CF_API_TOKEN)\s*[:=]\s*['\"]?[a-zA-Z0-9_-]{37,}['\"]?"), "critical", 3.5),
    Rule("supabase-jwt", "Supabase / JWT-shaped token", re.compile(r"eyJ[a-zA-Z0-9_-]{10,}\.eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}"), "high", 3.5),
    Rule("github-pat", "GitHub personal access token", re.compile(r"ghp_[A-Za-z0-9]{36}"), "critical", 3.5),
    Rule("github-fine-grained", "GitHub fine-grained PAT", re.compile(r"github_pat_[A-Za-z0-9_]{20,}"), "critical", 3.5),
    Rule("slack-token", "Slack token", re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"), "high", 3.2),
    Rule("jwt-secret-assign", "JWT / signing secret assignment", re.compile(r"(?i)(jwt[_-]?secret|signing[_-]?key|secret[_-]?key)\s*[:=]\s*['\"]?[A-Za-z0-9+/=_\-]{32,}['\"]?"), "high", 3.0),
    Rule("generic-api-key", "Generic API key assignment", re.compile(r"(?i)(api[_-]?key|apikey|access[_-]?token|auth[_-]?token)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{24,}['\"]?"), "medium", 3.5),
]

SKIP_SUFFIXES = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf", ".zip", ".gz", ".woff", ".woff2", ".ttf", ".mp4", ".mov", ".lock")
