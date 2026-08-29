#!/usr/bin/env python3
"""
Centralized script for creating or commenting on pull requests in GitHub Actions.
Safely chunks long output logs to prevent shell argument limits (ARG_MAX) and
GitHub API body character limits (65,536 characters).
"""

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

MAX_CHUNK_SIZE = 60000  # Safe buffer below GitHub's 65,536 character limit


def chunk_markdown(text: str, max_size: int = MAX_CHUNK_SIZE) -> list[str]:
    """
    Splits markdown text into line-safe chunks within character limits,
    preserving code block formatting across chunks when split.
    """
    clean_text = text.strip()
    if not clean_text:
        return ["_No output log provided._"]

    if len(clean_text) <= max_size:
        return [clean_text]

    chunks: list[str] = []
    current_lines: list[str] = []
    current_length = 0
    in_code_block = False
    fence_marker = "```"

    for line in text.splitlines(keepends=True):
        line_len = len(line)

        # In case a single line is excessively long (> max_size)
        if line_len > max_size:
            # Flush existing lines first
            if current_lines:
                if in_code_block:
                    current_lines.append(f"\n{fence_marker}\n")
                chunks.append("".join(current_lines))
                current_lines = []
                current_length = 0
                if in_code_block:
                    current_lines.append(f"{fence_marker}\n")
                    current_length += len(current_lines[0])

            # Slice the long line into pieces
            start = 0
            while start < line_len:
                sub_slice = line[start : start + max_size]
                if in_code_block and start > 0:
                    chunks.append(f"{fence_marker}\n{sub_slice}\n{fence_marker}")
                else:
                    chunks.append(sub_slice)
                start += max_size
            continue

        if current_length + line_len > max_size and current_lines:
            if in_code_block:
                current_lines.append(f"\n{fence_marker}\n")
            chunks.append("".join(current_lines))
            current_lines = []
            current_length = 0

            if in_code_block:
                current_lines.append(f"{fence_marker}\n")
                current_length += len(current_lines[0])

        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            if in_code_block:
                fence_marker = stripped[: stripped.find(" ") if " " in stripped else len(stripped)]
                if not fence_marker:
                    fence_marker = "```"

        current_lines.append(line)
        current_length += line_len

    if current_lines:
        chunks.append("".join(current_lines))

    total = len(chunks)
    if total > 1:
        return [
            f"### 📝 Update Log (Part {i + 1}/{total})\n\n{chunk.strip()}"
            for i, chunk in enumerate(chunks)
        ]
    return [chunk.strip() for chunk in chunks]


def run_gh(*args: str) -> subprocess.CompletedProcess:
    """Executes a gh CLI command and prints outputs."""
    cmd = ["gh", *args]
    print(f"Running: {' '.join(cmd[:4])} ...")
    res = subprocess.run(cmd, text=True, capture_output=True)
    if res.returncode != 0:
        print(f"Error running gh command: {res.stderr}", file=sys.stderr)
        res.check_returncode()
    return res


def is_pr_open(head: str) -> bool:
    """Checks if there is already an open pull request for the head branch."""
    res = subprocess.run(
        ["gh", "pr", "list", "--state", "open", "--head", head, "--json", "number"],
        text=True,
        capture_output=True,
    )
    if res.returncode != 0:
        print(f"Warning: Failed to list PRs: {res.stderr}", file=sys.stderr)
        return False

    try:
        prs = json.loads(res.stdout.strip() or "[]")
        return len(prs) > 0
    except json.JSONDecodeError:
        return bool(res.stdout.strip() and res.stdout.strip() != "[]")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create or comment on a pull request with automatic log chunking."
    )
    parser.add_argument("--head", required=True, help="Head branch (e.g. maimai/update-20260723)")
    parser.add_argument("--base", default="main", help="Base branch (default: main)")
    parser.add_argument("--title", required=True, help="Pull request title")
    parser.add_argument("--log-file", required=True, help="Path to the output log file")
    parser.add_argument("--labels", default="", help="Comma-separated labels for new PRs (e.g. automation)")

    args = parser.parse_args()

    log_path = Path(args.log_file)
    log_text = ""
    if log_path.exists():
        try:
            log_text = log_path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Warning: Failed to read {log_path}: {e}", file=sys.stderr)

    chunks = chunk_markdown(log_text)
    total_chunks = len(chunks)
    print(f"Log prepared: {len(log_text)} chars divided into {total_chunks} chunk(s).")

    has_open_pr = is_pr_open(args.head)

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        if has_open_pr:
            print(f"Found existing open PR for '{args.head}'. Posting {total_chunks} comment(s)...")
            for i, chunk in enumerate(chunks, start=1):
                comment_file = tmp_path / f"comment_{i}.md"
                comment_file.write_text(chunk, encoding="utf-8")
                run_gh("pr", "comment", args.head, "--body-file", str(comment_file))
                print(f"Successfully posted comment part {i}/{total_chunks}.")
        else:
            print(f"No existing PR found for '{args.head}'. Creating new PR...")
            pr_body_file = tmp_path / "pr_body.md"
            pr_body_file.write_text(chunks[0], encoding="utf-8")
            create_cmd = [
                "pr",
                "create",
                "--base",
                args.base,
                "--head",
                args.head,
                "--title",
                args.title,
                "--body-file",
                str(pr_body_file),
            ]
            if args.labels:
                for label in args.labels.split(","):
                    lbl = label.strip()
                    if lbl:
                        create_cmd.extend(["--label", lbl])
            res = run_gh(*create_cmd)
            print(f"Successfully created PR: {res.stdout.strip()}")

            if total_chunks > 1:
                print(f"Posting {total_chunks - 1} follow-up comment(s)...")
                for i, chunk in enumerate(chunks[1:], start=2):
                    comment_file = tmp_path / f"comment_{i}.md"
                    comment_file.write_text(chunk, encoding="utf-8")
                    run_gh("pr", "comment", args.head, "--body-file", str(comment_file))
                    print(f"Successfully posted follow-up comment part {i}/{total_chunks}.")


if __name__ == "__main__":
    main()
