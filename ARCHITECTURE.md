ARCHITECTURE.md# Architecture

This document describes the high level architecture and directory layout for Voicelogger after the refactoring toward a modular core and multi‑interface application.

## Directory structure

```
Voicelogger/
├── core/
│   ├── __init__.py
│   ├── transcribe.py    # wrappers around whisper.cpp or faster‑whisper
│   ├── summary.py       # simple extractive summarization and adapters to local LLMs
│   ├── crypto.py        # AES‑GCM encryption helpers
│   ├── report.py        # generate Markdown reports
│   └── exporters.py     # output formats: txt, srt, vtt, json
├── cli/
│   ├── __init__.py
│   └── voicelogger_cli.py  # command line interface for batch processing
├── desktop/
│   └── …                # future Tauri based desktop GUI
├── server/
│   └── …                # future API server (FastAPI/Axum)
├── docs/
│   └── …                # design documents, API specs
├── ROADMAP.md
├── ARCHITECTURE.md
├── README.md
└── requirements.txt
```

## Data flow

1. **Input** – One or more audio files are passed to the CLI or GUI.
2. **Transcription** – `core.transcribe.transcribe()` invokes whisper.cpp or faster‑whisper to produce segments with start/end times and plain text.
3. **Summarization** – `core.summary.simple_summary()` produces a concise Thai summary (optional local LLM summarization is integrated here).
4. **Export** – `core.exporters` converts segments into requested formats (TXT, SRT, VTT, JSON).
5. **Report** – `core.report.generate_report()` assembles a Markdown report combining transcript and summary.
6. **Encryption (optional)** – `core.crypto.encrypt_file_aes_gcm()` encrypts audio files and results before storage.

This modular design allows the same core functions to be used by a command line tool, a desktop application or a server API.
