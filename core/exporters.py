"""
Export utilities for Voicelogger.

Convert transcription segments to various output formats such as plain text,
SRT, WebVTT, and JSON. These helpers operate on the list of segments
returned from :func:`core.transcribe.transcribe_to_segments`.
"""

from __future__ import annotations

import json
from typing import List, Dict


def _format_srt_timestamp(seconds: float) -> str:
    """Format a time in seconds into an SRT timestamp (HH:MM:SS,ms)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int(round((seconds - int(seconds)) * 1000))
    return f"{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}"


def _format_vtt_timestamp(seconds: float) -> str:
    """Format a time in seconds into a WebVTT timestamp (HH:MM:SS.mmm)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int(round((seconds - int(seconds)) * 1000))
    return f"{hours:02}:{minutes:02}:{secs:02}.{milliseconds:03}"


def export_txt(segments: List[Dict[str, float | str]]) -> str:
    """Convert segments into a plain-text transcript separated by newlines."""
    return "\n".join([str(seg.get("text", "")).strip() for seg in segments if seg.get("text")])


def export_srt(segments: List[Dict[str, float | str]]) -> str:
    """Convert segments into the SubRip (SRT) subtitle format."""
    lines: List[str] = []
    for idx, seg in enumerate(segments, start=1):
        start = _format_srt_timestamp(float(seg.get("start", 0.0)))
        end = _format_srt_timestamp(float(seg.get("end", 0.0)))
        text = str(seg.get("text", "")).strip()
        lines.append(str(idx))
        lines.append(f"{start} --> {end}")
        lines.append(text)
        lines.append("")  # blank line between entries
    return "\n".join(lines).strip() + "\n"


def export_vtt(segments: List[Dict[str, float | str]]) -> str:
    """Convert segments into the WebVTT subtitle format."""
    lines: List[str] = ["WEBVTT", ""]
    for seg in segments:
        start = _format_vtt_timestamp(float(seg.get("start", 0.0)))
        end = _format_vtt_timestamp(float(seg.get("end", 0.0)))
        text = str(seg.get("text", "")).strip()
        lines.append(f"{start} --> {end}")
        lines.append(text)
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def export_json(segments: List[Dict[str, float | str]], ensure_ascii: bool = False, indent: int = 2) -> str:
    """Convert segments into a JSON-formatted string.

    Args:
        segments: A list of segment dictionaries.
        ensure_ascii: Whether to escape non-ASCII characters.
        indent: Indentation level for pretty printing.

    Returns:
        A JSON-formatted string representing the segments.
    """
    return json.dumps(segments, ensure_ascii=ensure_ascii, indent=indent)
