#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

README_PATH = Path(__file__).resolve().parents[1] / "README.md"
LEETCODE_GRAPHQL_URL = "https://leetcode.com/graphql/"
AUTO_START = "<!-- LEETCODE_STATS_START -->"
AUTO_END = "<!-- LEETCODE_STATS_END -->"

CATEGORY_ORDER = [
    "Array",
    "String",
    "Tree",
    "Hash Table",
    "Sorting",
    "Two Pointers",
    "Sliding Window",
    "BackTracking",
    "Prefix Sum",
    "Depth-First Search",
    "Binary Search",
    "Breadth-First Search",
    "Graph Theory",
    "Linked List",
    "Dynamic Programming",
]

CATEGORY_ALIASES = {
    "array": "Array",
    "string": "String",
    "tree": "Tree",
    "hash table": "Hash Table",
    "sorting": "Sorting",
    "two pointers": "Two Pointers",
    "sliding window": "Sliding Window",
    "backtracking": "BackTracking",
    "prefix sum": "Prefix Sum",
    "depth-first search": "Depth-First Search",
    "binary search": "Binary Search",
    "breadth-first search": "Breadth-First Search",
    "graph": "Graph Theory",
    "graph theory": "Graph Theory",
    "linked list": "Linked List",
    "dynamic programming": "Dynamic Programming",
}

CATEGORY_FIELD_NAMES = {
    "Array": "array",
    "String": "string",
    "Tree": "tree",
    "Hash Table": "hash_table",
    "Sorting": "sorting",
    "Two Pointers": "two_pointers",
    "Sliding Window": "sliding_window",
    "BackTracking": "backtracking",
    "Prefix Sum": "prefix_sum",
    "Depth-First Search": "depth_first_search",
    "Binary Search": "binary_search",
    "Breadth-First Search": "breadth_first_search",
    "Graph Theory": "graph_theory",
    "Linked List": "linked_list",
    "Dynamic Programming": "dynamic_programming",
}

STATS_QUERY = """
query userProblemsSolved($username: String!) {
  matchedUser(username: $username) {
    username
    submitStatsGlobal {
      acSubmissionNum {
        difficulty
        count
        submissions
      }
    }
  }
}
""".strip()

TAGS_QUERY = """
query skillStats($username: String!) {
  matchedUser(username: $username) {
    tagProblemCounts {
      advanced {
        tagName
        problemsSolved
      }
      intermediate {
        tagName
        problemsSolved
      }
      fundamental {
        tagName
        problemsSolved
      }
    }
  }
}
""".strip()


@dataclass(frozen=True)
class DifficultyStats:
    all: int = 0
    easy: int = 0
    medium: int = 0
    hard: int = 0


@dataclass(frozen=True)
class SubmissionStatsUser:
    username: str
    difficulty_stats: DifficultyStats


@dataclass(frozen=True)
class SubmissionStatsResponse:
    matched_user: SubmissionStatsUser | None


@dataclass(frozen=True)
class TagProblemCount:
    tag_name: str
    problems_solved: int


@dataclass(frozen=True)
class TagProblemCounts:
    advanced: list[TagProblemCount]
    intermediate: list[TagProblemCount]
    fundamental: list[TagProblemCount]


@dataclass(frozen=True)
class TagStatsUser:
    tag_problem_counts: TagProblemCounts


@dataclass(frozen=True)
class TagStatsResponse:
    matched_user: TagStatsUser | None


@dataclass
class CategoryCounts:
    array: int = 0
    string: int = 0
    tree: int = 0
    hash_table: int = 0
    sorting: int = 0
    two_pointers: int = 0
    sliding_window: int = 0
    backtracking: int = 0
    prefix_sum: int = 0
    depth_first_search: int = 0
    binary_search: int = 0
    breadth_first_search: int = 0
    graph_theory: int = 0
    linked_list: int = 0
    dynamic_programming: int = 0

    def get(self, category: str) -> int:
        field_name = CATEGORY_FIELD_NAMES[category]
        return int(getattr(self, field_name))


def extract_username(readme_text: str) -> str:
    patterns = [
        r"https://leetcode\.com/u/([A-Za-z0-9_-]+)/?",
        r"https://leetcode\.com/([A-Za-z0-9_-]+)/?",
    ]
    for pattern in patterns:
        match = re.search(pattern, readme_text)
        if match:
            return match.group(1)
    raise ValueError("Não foi possível encontrar o usuário do LeetCode no README.")


def graphql_request(query: str, variables: Dict[str, str], username: str) -> Dict[str, Any]:
    payload = json.dumps({"query": query, "variables": variables}).encode("utf-8")
    request = Request(
        LEETCODE_GRAPHQL_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Origin": "https://leetcode.com",
            "Referer": f"https://leetcode.com/u/{username}/",
            "User-Agent": "Mozilla/5.0 (GitHub Actions; LeetCode README updater)",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"Falha HTTP ao consultar o LeetCode: {exc.code} {detail}") from exc
    except URLError as exc:
        raise RuntimeError(f"Falha de rede ao consultar o LeetCode: {exc}") from exc

    if data.get("errors"):
        raise RuntimeError(f"Erro retornado pelo GraphQL do LeetCode: {data['errors']}")

    return data["data"]


def parse_submission_stats(data: Dict[str, Any]) -> SubmissionStatsResponse:
    matched_user_data = data.get("matchedUser")
    if not matched_user_data:
        return SubmissionStatsResponse(matched_user=None)

    difficulty_counts = {
        item["difficulty"]: int(item.get("count") or 0)
        for item in matched_user_data["submitStatsGlobal"]["acSubmissionNum"]
    }

    return SubmissionStatsResponse(
        matched_user=SubmissionStatsUser(
            username=matched_user_data["username"],
            difficulty_stats=DifficultyStats(
                all=difficulty_counts.get("All", 0),
                easy=difficulty_counts.get("Easy", 0),
                medium=difficulty_counts.get("Medium", 0),
                hard=difficulty_counts.get("Hard", 0),
            ),
        )
    )


def parse_tag_stats(data: Dict[str, Any]) -> TagStatsResponse:
    matched_user_data = data.get("matchedUser")
    if not matched_user_data:
        return TagStatsResponse(matched_user=None)

    tag_problem_counts_data = matched_user_data.get("tagProblemCounts") or {}

    def build_tag_list(items: Iterable[Dict[str, Any]] | None) -> list[TagProblemCount]:
        return [
            TagProblemCount(
                tag_name=item["tagName"],
                problems_solved=int(item.get("problemsSolved") or 0),
            )
            for item in (items or [])
        ]

    return TagStatsResponse(
        matched_user=TagStatsUser(
            tag_problem_counts=TagProblemCounts(
                advanced=build_tag_list(tag_problem_counts_data.get("advanced")),
                intermediate=build_tag_list(tag_problem_counts_data.get("intermediate")),
                fundamental=build_tag_list(tag_problem_counts_data.get("fundamental")),
            )
        )
    )


def fetch_submission_stats(username: str) -> SubmissionStatsResponse:
    data = graphql_request(STATS_QUERY, {"username": username}, username)
    return parse_submission_stats(data)


def fetch_tag_stats(username: str) -> TagStatsResponse:
    data = graphql_request(TAGS_QUERY, {"username": username}, username)
    return parse_tag_stats(data)


def flatten_tags(tag_groups: TagProblemCounts) -> CategoryCounts:
    counts = CategoryCounts()

    for group in (tag_groups.advanced, tag_groups.intermediate, tag_groups.fundamental):
        for item in group:
            raw_name = item.tag_name.strip().lower()
            normalized_name = CATEGORY_ALIASES.get(raw_name)
            if not normalized_name:
                continue
            field_name = CATEGORY_FIELD_NAMES[normalized_name]
            setattr(counts, field_name, item.problems_solved)

    return counts


def build_stats_block(username: str, submission_stats: SubmissionStatsResponse, tag_counts: CategoryCounts) -> str:
    difficulty_stats = submission_stats.matched_user.difficulty_stats

    total = difficulty_stats.all
    easy = difficulty_stats.easy
    medium = difficulty_stats.medium
    hard = difficulty_stats.hard
    updated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    rows = [
        "| Categoria | Quantidade resolvida |",
        "| --- | ---: |",
    ]
    for category in CATEGORY_ORDER:
        rows.append(f"| {category} | {tag_counts.get(category)} |")

    lines = [
        AUTO_START,
        "Este bloco é atualizado automaticamente com base no perfil público do LeetCode.",
        "",
        f"- Perfil monitorado: [leetcode.com/{username}](https://leetcode.com/{username})",
        f"- Última atualização: {updated_at}",
        "",
        *rows,
        "",
        f"**Total resolvido:** {total} questões  ",
        f"**Por dificuldade:** Easy {easy} · Medium {medium} · Hard {hard}",
        "",
        "> Observação: a soma por categoria pode ser maior que o total resolvido, porque uma mesma questão pode ter múltiplas tags no LeetCode.",
        AUTO_END,
    ]
    return "\n".join(lines)


def replace_auto_block(readme_text: str, new_block: str) -> str:
    pattern = re.compile(
        rf"{re.escape(AUTO_START)}.*?{re.escape(AUTO_END)}",
        re.DOTALL,
    )
    if pattern.search(readme_text):
        return pattern.sub(new_block, readme_text)
    raise ValueError("Não foi possível encontrar o bloco automático no README.")


def main() -> None:
    readme_text = README_PATH.read_text(encoding="utf-8")
    username = extract_username(readme_text)

    submission_stats = fetch_submission_stats(username)
    tag_stats = fetch_tag_stats(username)

    if not submission_stats.matched_user:
        raise RuntimeError(f"Usuário '{username}' não encontrado no LeetCode.")

    matched_user = tag_stats.matched_user
    if not matched_user:
        raise RuntimeError(f"Usuário '{username}' não encontrado no LeetCode.")

    tag_counts = flatten_tags(matched_user.tag_problem_counts)
    new_block = build_stats_block(username, submission_stats, tag_counts)
    updated_readme = replace_auto_block(readme_text, new_block)
    README_PATH.write_text(updated_readme + ("" if updated_readme.endswith("\n") else "\n"), encoding="utf-8")


if __name__ == "__main__":
    main()
