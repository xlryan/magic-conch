#!/usr/bin/env python3
"""Generate the graveyard leaderboard and badge cheatsheet.

This script scans `graveyard/entries/*.yml`, sorts by `score.total`,
updates the README leaderboard block, and rewrites
`badges/README-badges.md` with embeddable badge snippets.
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import yaml

ROOT = Path(__file__).resolve().parent.parent
ENTRIES_DIR = ROOT / "graveyard" / "entries"
README_PATH = ROOT / "README.md"
BADGES_PATH = ROOT / "badges" / "README-badges.md"
LEADERBOARD_START = "<!-- LEADERBOARD:START -->"
LEADERBOARD_END = "<!-- LEADERBOARD:END -->"


@dataclass
class Entry:
    slug: str
    title: str
    owner: str
    score_self: int
    score_reviewer: int
    score_total: int
    comeback: int
    tags: List[str]
    status: Optional[str]
    link: str
    sample: bool

    @property
    def display_title(self) -> str:
        note = " (Sample)" if self.sample else ""
        return f"{self.title}{note}"

    @property
    def owner_display(self) -> str:
        return self.owner if self.owner else "匿名"


class LeaderboardError(RuntimeError):
    """Raised when generation fails."""


def load_entries() -> List[Entry]:
    if not ENTRIES_DIR.exists():
        raise LeaderboardError(f"Entries directory not found: {ENTRIES_DIR}")

    entries: List[Entry] = []
    for path in sorted(ENTRIES_DIR.glob("*.yml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        try:
            score = data.get("score", {})
            entry = Entry(
                slug=data.get("id") or path.stem,
                title=data.get("title", "Untitled Project"),
                owner=data.get("owner", ""),
                score_self=int(score.get("self", 0)),
                score_reviewer=int(score.get("reviewer", score.get("self", 0))),
                score_total=int(score.get("total", score.get("self", 0))),
                comeback=int(data.get("comeback_potential", 0)),
                tags=list(data.get("tags", [])),
                status=data.get("status"),
                link=data.get("repo_url", "#"),
                sample=bool(data.get("sample", False)),
            )
        except (TypeError, ValueError) as exc:  # pragma: no cover - defensive
            raise LeaderboardError(f"Invalid data in {path}: {exc}") from exc
        entries.append(entry)

    return entries


def render_leaderboard(entries: List[Entry]) -> str:
    if not entries:
        return "排行榜尚未生成。请运行 `python scripts/generate_leaderboard.py`。"

    header = (
        "| 排名 | 项目 | 自评 / Reviewer | 总分 (越烂越高) | 回春潜力 | 标签 |\n"
        "| --- | --- | --- | --- | --- | --- |"
    )

    rows = []
    for idx, entry in enumerate(entries, start=1):
        owner_html = f"<br/><small>{entry.owner_display}</small>" if entry.owner_display else ""
        status_badge = ""
        if entry.status:
            status_badge = f"<br/><code>{entry.status}</code>"
        row = (
            f"| {idx} "
            f"| **{entry.display_title}**{owner_html}{status_badge} "
            f"| {entry.score_self} / {entry.score_reviewer} "
            f"| {entry.score_total} "
            f"| {entry.comeback}/10 "
            f"| {', '.join(entry.tags) if entry.tags else '—'} |"
        )
        rows.append(row)

    return "\n".join([header, *rows])


def inject_leaderboard(markdown: str, block: str) -> str:
    pattern = re.compile(
        rf"{re.escape(LEADERBOARD_START)}.*?{re.escape(LEADERBOARD_END)}",
        re.DOTALL,
    )
    replacement = f"{LEADERBOARD_START}\n{block}\n{LEADERBOARD_END}"
    if not pattern.search(markdown):
        raise LeaderboardError("Leaderboard anchor not found in README.md")
    return pattern.sub(replacement, markdown, count=1)


def build_badge_markdown(entries: List[Entry]) -> str:
    intro = (
        "# Graveyard Badges\n\n"
        "想在自己的 README 里纪念一次漂亮的翻车吗？拷贝下方徽章即可。\n\n"
        "## 嵌入方式 How to Embed\n"
        "1. 选择想展示的徽章 Markdown 片段。\n"
        "2. 粘贴到你的 README 或文章中。\n"
        "3. 欢迎链接回本仓库或原项目复盘。\n\n"
    )

    if not entries:
        return intro + "尚无条目，欢迎成为第一位投稿者！\n"

    top_section = ["## Top 10 最烂项目徽章\n"]
    comeback_section = ["## 最佳回春潜力徽章\n"]

    if entries:
        top_entries = entries
        for entry in top_entries:
            badge = _score_badge(entry)
            line = (
                f"- `[![{entry.slug} • {entry.score_total} pts]({badge})]({entry.link})` :"
                f" {entry.display_title} — 回春潜力 {entry.comeback}/10"
            )
            top_section.append(line)

        best_comeback = max(entries, key=lambda e: e.comeback, default=None)
        if best_comeback:
            badge = _comeback_badge(best_comeback)
            comeback_section.append(
                f"- `[![{best_comeback.slug} comeback {best_comeback.comeback}/10]({badge})]({best_comeback.link})`"
                f" : {best_comeback.display_title}"
            )

    return intro + "\n".join(top_section + ["", *comeback_section]) + "\n"


def _score_badge(entry: Entry) -> str:
    label_slug = entry.slug.replace("-", "--")
    return (
        "https://img.shields.io/badge/Graveyard%20Score-"
        f"{entry.score_total}%20pts-ff5d73?label={label_slug}&labelColor=232323"
    )


def _comeback_badge(entry: Entry) -> str:
    label_slug = entry.slug.replace("-", "--")
    return (
        "https://img.shields.io/badge/Comeback%20Potential-"
        f"{entry.comeback}%2F10-0b3d91?label={label_slug}&labelColor=232323"
    )


def main() -> int:
    entries = load_entries()
    ranked = sorted(entries, key=lambda e: e.score_total, reverse=True)[:10]

    leaderboard_block = render_leaderboard(ranked)
    readme_text = README_PATH.read_text(encoding="utf-8")
    README_PATH.write_text(
        inject_leaderboard(readme_text, leaderboard_block),
        encoding="utf-8",
    )

    badges_text = build_badge_markdown(ranked)
    BADGES_PATH.write_text(badges_text, encoding="utf-8")

    print(f"Updated leaderboard with {len(ranked)} entries.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except LeaderboardError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)
