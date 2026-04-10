#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable
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


def graphql_request(query: str, variables: Dict[str, str], username: str) -> Dict:
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


def flatten_tags(tag_groups: Dict[str, Iterable[Dict]]) -> Dict[str, int]:
    counts: Dict[str, int] = {category: 0 for category in CATEGORY_ORDER}

    for group in ("advanced", "intermediate", "fundamental"):
        for item in tag_groups.get(group) or []:
            raw_name = (item.get("tagName") or "").strip().lower()
            normalized_name = CATEGORY_ALIASES.get(raw_name)
            if not normalized_name:
                continue
            counts[normalized_name] = int(item.get("problemsSolved") or 0)

    return counts


def build_stats_block(username: str, submission_stats: Dict, tag_counts: Dict[str, int]) -> str:
    stats_by_difficulty = {
        item["difficulty"]: int(item.get("count") or 0)
        for item in submission_stats["matchedUser"]["submitStatsGlobal"]["acSubmissionNum"]
    }

    total = stats_by_difficulty.get("All", 0)
    easy = stats_by_difficulty.get("Easy", 0)
    medium = stats_by_difficulty.get("Medium", 0)
    hard = stats_by_difficulty.get("Hard", 0)
    updated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    rows = [
        "| Categoria | Quantidade resolvida |",
        "| --- | ---: |",
    ]
    for category in CATEGORY_ORDER:
        rows.append(f"| {category} | {tag_counts.get(category, 0)} |")

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

    submission_stats = graphql_request(STATS_QUERY, {"username": username}, username)
    tag_stats = graphql_request(TAGS_QUERY, {"username": username}, username)

    if not submission_stats.get("matchedUser"):
        raise RuntimeError(f"Usuário '{username}' não encontrado no LeetCode.")

    matched_user = tag_stats.get("matchedUser")
    if not matched_user:
        raise RuntimeError(f"Usuário '{username}' não encontrado no LeetCode.")

    tag_counts = flatten_tags(matched_user.get("tagProblemCounts") or {})
    new_block = build_stats_block(username, submission_stats, tag_counts)
    updated_readme = replace_auto_block(readme_text, new_block)
    README_PATH.write_text(updated_readme + ("" if updated_readme.endswith("\n") else "\n"), encoding="utf-8")


if __name__ == "__main__":
    main()
