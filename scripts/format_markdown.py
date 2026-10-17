#!/usr/bin/env python3
"""Format markdown files to keep line lengths under a specified limit.

This script formats paragraphs, lists, and markdown links to comply with line
length constraints (default: 79 characters, to strictly keep lines under 80
characters), while preserving headings, code fences, blockquotes, and tables.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import textwrap
from typing import Sequence


def wrap_blockquote(lines: list[str], prefix: str, width: int) -> list[str]:
    """Wrap lines within a blockquote preserving the quote prefix."""
    text = " ".join(line.strip() for line in lines if line.strip())
    sub_width = max(20, width - len(prefix))
    wrapped = textwrap.fill(
        text,
        width=sub_width,
        break_on_hyphens=False,
        break_long_words=False,
    )
    return [f"{prefix}{wl}" for wl in wrapped.splitlines()]


def wrap_list_item(
    item_lines: list[str],
    lead_indent: str,
    marker: str,
    width: int,
) -> list[str]:
    """Wrap a single list item preserving indentation and links."""
    marker_len = len(lead_indent) + len(marker) + 1
    sub_indent = " " * marker_len
    initial_indent = f"{lead_indent}{marker} "
    raw_item_text = " ".join(item_lines)

    # Check for bullet item with single markdown link:
    # e.g.: * manufacturer link: [Title](url "desc")
    link_match = re.search(
        r'^(.*?:(?:\*\*|\*|__|_)?\s*)?(\[[^\]]+\])\(\s*(https?://[^\s\)]+)'
        r'(?:\s+"([^"]*)")?\s*\)$',
        raw_item_text,
    )
    if link_match:
        prefix = link_match.group(1) or ""
        link_text = link_match.group(2)
        url = link_match.group(3)
        title = link_match.group(4)

        title_part = f' "{title}"' if title else ""
        one_line = f"{initial_indent}{prefix}{link_text}({url}{title_part})"
        if len(one_line) <= width:
            return [one_line]

        l1 = f"{initial_indent}{prefix}{link_text}("
        l2 = f"{sub_indent}{url}"
        if title:
            return [l1, l2, f'{sub_indent}"{title}")']
        return [l1, f"{sub_indent}{url})"]

    wrapped = textwrap.fill(
        raw_item_text,
        width=width,
        initial_indent=initial_indent,
        subsequent_indent=sub_indent,
        break_on_hyphens=False,
        break_long_words=False,
    )
    return wrapped.splitlines()


def format_markdown(content: str, width: int = 79) -> str:
    """Format markdown content so that lines do not exceed width."""
    lines = content.split("\n")
    output_lines: list[str] = []

    in_code_block = False
    code_fence = ""

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Handle fenced code blocks (``` or ~~~)
        if stripped.startswith("```") or stripped.startswith("~~~"):
            fence = stripped[:3]
            if not in_code_block:
                in_code_block = True
                code_fence = fence
                output_lines.append(line)
                i += 1
                continue
            if stripped.startswith(code_fence):
                in_code_block = False
                code_fence = ""
                output_lines.append(line)
                i += 1
                continue

        if in_code_block:
            output_lines.append(line)
            i += 1
            continue

        # Preserve empty lines
        if not stripped:
            output_lines.append("")
            i += 1
            continue

        # Markdown table row
        if stripped.startswith("|") and stripped.endswith("|"):
            output_lines.append(line)
            i += 1
            continue

        # Headings
        if re.match(r"^#{1,6}\s+", line):
            output_lines.append(line)
            i += 1
            continue

        # Horizontal rules
        if re.match(r"^(-{3,}|\*{3,}|_{3,})$", stripped):
            output_lines.append(line)
            i += 1
            continue

        # Blockquote
        bq_match = re.match(r"^(\s*>+\s*)(.*)$", line)
        if bq_match:
            bq_prefix = bq_match.group(1)
            bq_lines = [bq_match.group(2)]
            i += 1
            while i < len(lines):
                next_l = lines[i]
                next_m = re.match(r"^(\s*>+\s*)(.*)$", next_l)
                if next_m and next_m.group(1).strip() == bq_prefix.strip():
                    bq_lines.append(next_m.group(2))
                    i += 1
                else:
                    break
            output_lines.extend(wrap_blockquote(bq_lines, bq_prefix, width))
            continue

        # List item
        list_match = re.match(r"^(\s*)([*+-]|\d+[.)])\s+(.*)$", line)
        if list_match:
            lead_indent = list_match.group(1)
            marker = list_match.group(2)
            first_text = list_match.group(3)

            item_lines = [first_text]
            i += 1
            while i < len(lines):
                next_l = lines[i]
                if not next_l.strip():
                    break
                if (
                    re.match(r"^(\s*)([*+-]|\d+[.)])\s+", next_l)
                    or re.match(r"^#{1,6}\s+", next_l)
                    or next_l.strip().startswith("```")
                    or next_l.strip().startswith("~~~")
                    or (
                        next_l.strip().startswith("|")
                        and next_l.strip().endswith("|")
                    )
                ):
                    break
                item_lines.append(next_l.strip())
                i += 1

            output_lines.extend(
                wrap_list_item(item_lines, lead_indent, marker, width)
            )
            continue

        # Regular paragraph
        para_lines = [line.strip()]
        i += 1
        while i < len(lines):
            next_l = lines[i]
            if not next_l.strip():
                break
            if (
                re.match(r"^(\s*)([*+-]|\d+[.)])\s+", next_l)
                or re.match(r"^#{1,6}\s+", next_l)
                or next_l.strip().startswith("```")
                or next_l.strip().startswith("~~~")
                or re.match(r"^\s*>+", next_l)
                or (
                    next_l.strip().startswith("|")
                    and next_l.strip().endswith("|")
                )
            ):
                break
            para_lines.append(next_l.strip())
            i += 1

        para_text = " ".join(para_lines)
        wrapped = textwrap.fill(
            para_text,
            width=width,
            break_on_hyphens=False,
            break_long_words=False,
        )
        output_lines.extend(wrapped.splitlines())

    result = "\n".join(output_lines)
    if content.endswith("\n") and not result.endswith("\n"):
        result += "\n"
    return result


def check_line_lengths(content: str, width: int) -> list[tuple[int, int]]:
    """Return line numbers and lengths of lines exceeding width."""
    violations: list[tuple[int, int]] = []
    in_code_block = False
    code_fence = ""

    for idx, line in enumerate(content.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            fence = stripped[:3]
            if not in_code_block:
                in_code_block = True
                code_fence = fence
                continue
            if stripped.startswith(code_fence):
                in_code_block = False
                code_fence = ""
                continue
        if in_code_block:
            continue
        if stripped.startswith("|") and stripped.endswith("|"):
            continue
        # Standalone URLs or link destination lines cannot be broken
        if re.match(r"^https?://\S+\)?$", stripped):
            continue
        if len(line) > width:
            violations.append((idx, len(line)))
    return violations


def collect_markdown_files(paths: Sequence[str]) -> list[str]:
    """Collect markdown file paths from files and directories."""
    files: list[str] = []
    for path in paths:
        if os.path.isdir(path):
            for root, _, filenames in os.walk(path):
                for filename in filenames:
                    if filename.endswith(".md"):
                        files.append(os.path.join(root, filename))
        elif os.path.isfile(path):
            files.append(path)
        else:
            print(f"Warning: path not found: {path}", file=sys.stderr)
    return sorted(files)


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point for formatting markdown files."""
    parser = argparse.ArgumentParser(
        description="Format markdown files to stay under line length limits."
    )
    parser.add_argument(
        "paths",
        nargs="+",
        help="Markdown file(s) or directory(ies) to format.",
    )
    parser.add_argument(
        "-w",
        "--width",
        type=int,
        default=79,
        help="Maximum line width (default: 79 for strictly < 80 characters).",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help=(
            "Check compliance without writing changes. "
            "Exit 1 if unformatted."
        ),
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print formatted output to stdout instead of modifying in-place.",
    )

    args = parser.parse_args(argv)
    targets = collect_markdown_files(args.paths)

    if not targets:
        print("No markdown files found.", file=sys.stderr)
        return 1

    has_violations = False

    for target in targets:
        try:
            with open(target, "r", encoding="utf-8") as f:
                original = f.read()
        except OSError as err:
            print(f"Error reading {target}: {err}", file=sys.stderr)
            has_violations = True
            continue

        formatted = format_markdown(original, width=args.width)
        long_lines = check_line_lengths(formatted, args.width)
        needs_formatting = original != formatted

        if args.check:
            if needs_formatting or long_lines:
                has_violations = True
                print(f"FAIL: {target} requires formatting.")
                for line_no, length in long_lines:
                    msg = (
                        f"  line {line_no} exceeds "
                        f"{args.width} chars ({length})"
                    )
                    print(msg)
            else:
                print(f"OK: {target}")
            continue

        if args.stdout:
            sys.stdout.write(formatted)
            continue

        if needs_formatting:
            try:
                with open(target, "w", encoding="utf-8") as f:
                    f.write(formatted)
                print(f"Formatted: {target}")
            except OSError as err:
                print(f"Error writing {target}: {err}", file=sys.stderr)
                has_violations = True
        else:
            print(f"Unchanged: {target}")

    return 1 if (args.check and has_violations) else 0


if __name__ == "__main__":
    sys.exit(main())
