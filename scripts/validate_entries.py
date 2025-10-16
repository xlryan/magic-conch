#!/usr/bin/env python3
"""Validate graveyard entries against the published schema."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import List

import yaml
from jsonschema import ValidationError, validate

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_MD = ROOT / "graveyard" / "schema.md"
ENTRIES_DIR = ROOT / "graveyard" / "entries"

SCHEMA_PATTERN = re.compile(r"```json\n(.*?)\n```", re.DOTALL)
SUSPECT_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"AKIA[0-9A-Z]{16}",  # AWS access key
        r"ASIA[0-9A-Z]{16}",
        r"ghp_[A-Za-z0-9]{36}",  # GitHub PAT
        r"-----BEGIN [A-Z ]+PRIVATE KEY-----",
        r"aws_secret_access_key",
        r"secret_key",
        r"api[_-]?key",
    ]
]


def load_schema() -> dict:
    text = SCHEMA_MD.read_text(encoding="utf-8")
    match = SCHEMA_PATTERN.search(text)
    if not match:
        raise RuntimeError("JSON schema block not found in graveyard/schema.md")
    return json.loads(match.group(1))


def detect_secrets(content: str, path: Path) -> List[str]:
    findings: List[str] = []
    for pattern in SUSPECT_PATTERNS:
        if pattern.search(content):
            findings.append(f"Potential secret matched `{pattern.pattern}` in {path}")
    return findings


def main() -> int:
    schema = load_schema()
    if not ENTRIES_DIR.exists():
        print("No entries directory found; nothing to validate.")
        return 0

    errors: List[str] = []
    for entry_path in sorted(ENTRIES_DIR.glob("*.yml")):
        raw = entry_path.read_text(encoding="utf-8")
        data = yaml.safe_load(raw)
        try:
            validate(data, schema)
        except ValidationError as exc:
            errors.append(f"Schema validation failed for {entry_path}: {exc.message}")
            continue

        if not data.get("consent", {}).get("confirmed", False):
            errors.append(f"{entry_path} must set consent.confirmed: true")

        if data.get("score", {}).get("total") is None:
            errors.append(f"{entry_path} is missing score.total")

        if isinstance(data.get("comeback_potential"), int):
            total = data.get("score", {}).get("total", 0)
            if not (0 <= total <= 100):
                errors.append(f"{entry_path} has score.total outside 0-100")

        for finding in detect_secrets(raw, entry_path):
            errors.append(finding)

    if errors:
        print("Validation issues detected:\n" + "\n".join(f"- {msg}" for msg in errors))
        return 1

    print("All graveyard entries passed validation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
