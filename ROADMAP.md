# Roadmap

This roadmap outlines the planned development phases for Voicelogger as we extend it toward the functionality of vibe. The goal is to support offline transcription, batch processing, multiple export formats, summaries and translation, and to offer both a CLI and a desktop GUI.

## Phase 1 – Foundation
- Split the original CLI logic into a reusable core library.
- Support batch transcription: process multiple audio files or entire folders.
- Produce multiple outputs: plain text transcript, summary, and optional formats such as SRT, VTT and JSON.
- Add a new CLI interface (`cli/voicelogger_cli.py`) with flags:
  - `--outdir` to specify the output directory.
  - `--model` to choose the Whisper model size.
  - `--language` (default "th") to override automatic detection.
  - `--txt`, `--srt`, `--vtt`, `--json` to enable export formats.
- Keep all processing offline using whisper.cpp or faster‑whisper.
- Preserve optional AES‑GCM encryption for audio and results.

## Phase 2 – Desktop GUI (Tauri)
- Scaffold a Tauri based desktop application in the `desktop/` directory.
- Provide a drag‑and‑drop interface to queue up audio files.
- Display real‑time progress and previews of transcripts and summaries.
- Expose settings for model choice, output formats and encryption.

## Phase 3 – HTTP API
- Add a small API server (FastAPI or Rust) under `server/`.
- Endpoints to submit files, query job status and download results.
- Generate an OpenAPI/Swagger schema for integration.

## Phase 4 – Diarization and advanced exports
- Integrate speaker diarization to label speakers in transcripts.
- Add exporters to PDF and DOCX.
- Allow tuning caption lengths for SRT/VTT (useful for video subtitling).
- Implement retention policies and role‑based access control.
