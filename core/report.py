"""
Report generation utilities for Voicelogger.

Functions to build Markdown reports combining transcript and summary information.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional


def generate_markdown_report(transcript: str, summary: str, audio_name: str) -> str:
    """Compose a Markdown report from a transcript and summary.

    Args:
        transcript: Full transcript text.
        summary: Summary text (may be empty).
        audio_name: Filename of the original audio file.

    Returns:
        A Markdown-formatted string containing a report with metadata, summary and transcript.
    """
    # Start with a top-level heading
    lines = ["# Voicelogger Report", ""]
    # Metadata
    lines.append(f"- Generated: {datetime.utcnow().isoformat()}Z")
    lines.append(f"- Audio file: {audio_name}")
    lines.append("")
    # Summary section
    lines.append("## Summary")
    lines.append("")
    if summary and summary.strip():
        lines.append(summary.strip())
    else:
        lines.append("*(no summary available)*")
    lines.append("")
    # Transcript section
    lines.append("## Transcript")
    lines.append("")
    lines.append(transcript.strip() if transcript else "")
    return "\n".join(lines)


def write_report(report_content: str, out_path: str) -> None:
    """Write a report string to a file.

    Args:
        report_content: The Markdown content to write.
        out_path: Path to write the report file.
    """
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(report_content)
