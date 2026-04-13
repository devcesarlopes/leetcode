from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict

ARRAYS_DOC_PATH = Path(__file__).resolve().parents[1] / "Arrays.md"
ARRAYS_AUTO_START = "<!-- ARRAY_QUESTIONS_START -->"
ARRAYS_AUTO_END = "<!-- ARRAY_QUESTIONS_END -->"

RECENT_SUBMISSIONS_QUERY = """
query recentSubmissions($username: String!, $limit: Int!) {
    recentSubmissionList(username: $username, limit: $limit) {
        title
        titleSlug
        statusDisplay
        timestamp
    }
}
""".strip()

QUESTION_TAGS_QUERY = """
query questionTags($titleSlug: String!) {
    question(titleSlug: $titleSlug) {
        questionFrontendId
        title
        titleSlug
        topicTags {
            name
            slug
        }
    }
}
""".strip()

GraphQLRequester = Callable[[str, Dict[str, Any], str], Dict[str, Any]]


@dataclass(frozen=True)
class RecentSubmission:
    title: str
    title_slug: str
    status_display: str
    timestamp: int


@dataclass(frozen=True)
class QuestionBrief:
    frontend_id: str
    title: str
    title_slug: str
    topic_tag_slugs: tuple[str, ...]


def fetch_recent_submissions(
    graphql_request: GraphQLRequester,
    username: str,
    limit: int = 100,
) -> list[RecentSubmission]:
    data = graphql_request(
        RECENT_SUBMISSIONS_QUERY,
        {"username": username, "limit": limit},
        username,
    )
    items = data.get("recentSubmissionList") or []
    submissions: list[RecentSubmission] = []
    for item in items:
        submissions.append(
            RecentSubmission(
                title=item.get("title") or "",
                title_slug=item.get("titleSlug") or "",
                status_display=item.get("statusDisplay") or "",
                timestamp=int(item.get("timestamp") or 0),
            )
        )
    return submissions


def fetch_question_brief(
    graphql_request: GraphQLRequester,
    username: str,
    title_slug: str,
) -> QuestionBrief | None:
    data = graphql_request(QUESTION_TAGS_QUERY, {"titleSlug": title_slug}, username)
    question_data = data.get("question")
    if not question_data:
        return None

    topic_tag_slugs = tuple((tag.get("slug") or "") for tag in (question_data.get("topicTags") or []))
    return QuestionBrief(
        frontend_id=str(question_data.get("questionFrontendId") or ""),
        title=question_data.get("title") or "",
        title_slug=question_data.get("titleSlug") or "",
        topic_tag_slugs=topic_tag_slugs,
    )


def _safe_frontend_id_key(frontend_id: str) -> tuple[int, str]:
    if frontend_id.isdigit():
        return (0, f"{int(frontend_id):08d}")
    return (1, frontend_id)


def collect_array_questions_from_recent(
    graphql_request: GraphQLRequester,
    username: str,
) -> list[QuestionBrief]:
    submissions = fetch_recent_submissions(graphql_request, username)

    seen_slugs: set[str] = set()
    accepted_slugs_in_order: list[str] = []
    for submission in submissions:
        if submission.status_display != "Accepted":
            continue
        if not submission.title_slug or submission.title_slug in seen_slugs:
            continue
        seen_slugs.add(submission.title_slug)
        accepted_slugs_in_order.append(submission.title_slug)

    array_questions: list[QuestionBrief] = []
    for slug in accepted_slugs_in_order:
        question = fetch_question_brief(graphql_request, username, slug)
        if not question:
            continue
        if "array" in question.topic_tag_slugs:
            array_questions.append(question)

    array_questions.sort(key=lambda question: _safe_frontend_id_key(question.frontend_id))
    return array_questions


def replace_auto_block_generic(text: str, start_marker: str, end_marker: str, new_block: str) -> str:
    pattern = re.compile(
        rf"{re.escape(start_marker)}.*?{re.escape(end_marker)}",
        re.DOTALL,
    )
    if pattern.search(text):
        return pattern.sub(new_block, text)
    raise ValueError(f"Não foi possível encontrar o bloco automático: {start_marker} ... {end_marker}")


def build_array_questions_block(username: str, questions: list[QuestionBrief]) -> str:
    updated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        ARRAYS_AUTO_START,
        "This block is auto-updated by `scripts/update_leetcode_stats.py`.",
        "",
        f"- Profile: [leetcode.com/{username}](https://leetcode.com/{username})",
        f"- Updated at: {updated_at}",
        "- Source: recent accepted submissions filtered by the `array` tag",
        "",
    ]

    if not questions:
        lines.extend(
            [
                "No solved Array questions were found in the current public feed.",
                ARRAYS_AUTO_END,
            ]
        )
        return "\n".join(lines)

    lines.append("| # | LeetCode ID | Problem |")
    lines.append("| ---: | ---: | --- |")
    for index, question in enumerate(questions, start=1):
        lines.append(
            "| "
            f"{index} | {question.frontend_id} | "
            f"[{question.title}](https://leetcode.com/problems/{question.title_slug}/) |"
        )

    lines.append(ARRAYS_AUTO_END)
    return "\n".join(lines)


def update_arrays_doc(
    username: str,
    graphql_request: GraphQLRequester,
    arrays_doc_path: Path = ARRAYS_DOC_PATH,
) -> None:
    arrays_text = arrays_doc_path.read_text(encoding="utf-8")
    array_questions = collect_array_questions_from_recent(graphql_request, username)
    arrays_block = build_array_questions_block(username, array_questions)
    updated_arrays_doc = replace_auto_block_generic(
        arrays_text,
        ARRAYS_AUTO_START,
        ARRAYS_AUTO_END,
        arrays_block,
    )
    arrays_doc_path.write_text(
        updated_arrays_doc + ("" if updated_arrays_doc.endswith("\n") else "\n"),
        encoding="utf-8",
    )
