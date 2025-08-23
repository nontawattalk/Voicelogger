#!/usr/bin/env python3
"""
voicelogger_cli.py

Command-line interface for the Voicelogger project. This script wraps the core
functionality to transcribe audio files (or directories of files), optionally
summarize transcripts, export them to multiple formats (TXT, SRT, VTT, JSON),
generate Markdown reports, and encrypt original audio files using AES-GCM.

The CLI is designed to mirror features found in modern transcription tools like
Vibe, supporting batch processing and flexible output options. It relies on
modules implemented in the `core` package.
"""

import argparse
import os
import sys
from typing import List

# Import core modules
try:
    from core.transcribe import transcribe_to_segments, segments_to_text
    from core.exporters import export_txt, export_srt, export_vtt, export_json
    from core.summary import simple_summary
    from core.report import generate_markdown_report
    from core.crypto import encrypt_file_aes_gcm
except ImportError as e:
    # If running from source repository, adjust sys.path to include project root
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))  # add project root
    from core.transcribe import transcribe_to_segments, segments_to_text
    from core.exporters import export_txt, export_srt, export_vtt, export_json
    from core.summary import simple_summary
    from core.report import generate_markdown_report
    from core.crypto import encrypt_file_aes_gcm


def find_audio_files(input_path: str) -> List[str]:
    """Return a list of audio file paths based on the input path.

    If `input_path` is a directory, all supported audio files within the
    directory are returned. Otherwise, the single file path is returned.
    Supported extensions include .wav, .mp3, .m4a, .aac, .flac, .ogg, .opus.
    """
    supported_exts = (
        ".wav", ".mp3", ".m4a", ".aac", ".flac", ".ogg", ".opus", ".webm"
    )
    if os.path.isdir(input_path):
        files = []
        for fname in os.listdir(input_path):
            if fname.lower().endswith(supported_exts):
                files.append(os.path.join(input_path, fname))
        return files
    else:
        return [input_path]


def process_audio_file(audio_path: str, outdir: str, args: argparse.Namespace) -> None:
    """Process a single audio file: transcribe, export, summarize, report, encrypt."""
    base_name = os.path.splitext(os.path.basename(audio_path))[0]
    print(f"Transcribing {audio_path} ...")
    segments = transcribe_to_segments(audio_path, model_size=args.model, language=args.language)

    # Ensure output directory exists
    os.makedirs(outdir, exist_ok=True)

    # Export transcripts
    any_flag = args.txt or args.srt or args.vtt or args.json
    # If no specific export flag is provided, default to TXT
    if args.txt or not any_flag:
        txt_path = os.path.join(outdir, f"{base_name}.txt")
        export_txt(segments, txt_path)
        print(f"  -> TXT saved to {txt_path}")
    if args.srt:
        srt_path = os.path.join(outdir, f"{base_name}.srt")
        export_srt(segments, srt_path)
        print(f"  -> SRT saved to {srt_path}")
    if args.vtt:
        vtt_path = os.path.join(outdir, f"{base_name}.vtt")
        export_vtt(segments, vtt_path)
        print(f"  -> VTT saved to {vtt_path}")
    if args.json:
        json_path = os.path.join(outdir, f"{base_name}.json")
        export_json(segments, json_path)
        print(f"  -> JSON saved to {json_path}")

    # Compose full transcript text
    transcript_text = segments_to_text(segments)

    # Summarize transcript if requested
    summary_text: str = ""
    if args.summary:
        max_sentences = args.summary_length or 5
        summary_text = simple_summary(transcript_text, max_sentences=max_sentences)
        summary_path = os.path.join(outdir, f"{base_name}.summary.txt")
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(summary_text)
        print(f"  -> Summary saved to {summary_path}")

    # Generate report (always)
    report_path = os.path.join(outdir, f"{base_name}_report.md")
    generate_markdown_report(transcript_text, summary_text, report_path, os.path.basename(audio_path))
    print(f"  -> Report saved to {report_path}")

    # Encrypt original audio file if passphrase provided
    if args.passphrase:
        enc_path = os.path.join(outdir, f"{base_name}.enc")
        encrypt_file_aes_gcm(audio_path, enc_path, args.passphrase)
        print(f"  -> Encrypted audio saved to {enc_path} and metadata")



def build_parser() -> argparse.ArgumentParser:
    """Configure and return the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        description="Transcribe and process audio files with multiple output formats."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to an audio file or directory containing audio files.",
    )
    parser.add_argument(
        "--outdir",
        default="output",
        help="Directory to place output files (default: output)",
    )
    parser.add_argument(
        "--model",
        default="medium",
        help="Whisper model size to use (e.g., small, medium, large-v2)",
    )
    parser.add_argument(
        "--language",
        default="th",
        help="Language code for transcription (default: th)",
    )

    # Output format flags
    parser.add_argument("--txt", action="store_true", help="Export plain text transcript")
    parser.add_argument("--srt", action="store_true", help="Export SRT subtitles")
    parser.add_argument("--vtt", action="store_true", help="Export VTT subtitles")
    parser.add_argument("--json", action="store_true", help="Export JSON with timestamps")

    parser.add_argument(
        "--summary",
        action="store_true",
        help="Generate a summary of the transcript (simple extractive)",
    )
    parser.add_argument(
        "--summary-length",
        type=int,
        default=5,
        help="Number of sentences to include in the summary (default: 5)",
    )
    parser.add_argument(
        "--passphrase",
        help="Passphrase for AES-GCM encryption of the original audio file",
    )
    return parser


def main(argv: List[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    # Gather files
    audio_files = find_audio_files(args.input)
    if not audio_files:
        print(f"No supported audio files found at {args.input}", file=sys.stderr)
        sys.exit(1)

    for audio_file in audio_files:
        process_audio_file(audio_file, args.outdir, args)

    print("\nAll files processed.")


if __name__ == "__main__":
    main()
