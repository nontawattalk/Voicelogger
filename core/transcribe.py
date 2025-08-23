"""
Transcription utilities for Voicelogger.

Provides functions to transcribe audio files into segments and plain text using the
faster-whisper library. Each segment contains start/end timestamps (in seconds) and
its corresponding text.
"""

from typing import List, Dict, Optional

try:
    # Import here so the module does not break if faster-whisper is missing.
    from faster_whisper import WhisperModel  # type: ignore
except ImportError:
    WhisperModel = None  # type: ignore


def _get_model(model_size: str) -> "WhisperModel":
    """Load a Whisper model of the given size.

    Raises:
        ImportError: if faster-whisper is not installed.
    """
    if WhisperModel is None:
        raise ImportError(
            "faster-whisper is not installed. Install it via `pip install faster-whisper`."
        )
    return WhisperModel(model_size)


def transcribe_to_segments(
    audio_path: str,
    model_size: str = "medium",
    language: str = "th",
    beam_size: int = 5,
    vad_filter: bool = True,
) -> List[Dict[str, float | str]]:
    """Transcribe an audio file into a list of segments.

    Each segment includes start time, end time and the transcribed text.

    Args:
        audio_path: Path to the audio file to transcribe.
        model_size: Size of the Whisper model (e.g. "small", "medium", "large-v3").
        language: Language code to use for transcription (default is "th" for Thai).
        beam_size: Beam size for decoding. Larger values may improve accuracy at the cost of speed.
        vad_filter: Whether to enable Voice Activity Detection to filter out silence.

    Returns:
        A list of dictionaries with keys: "start", "end", and "text".
    """
    model = _get_model(model_size)
    segments, info = model.transcribe(
        audio_path,
        language=language,
        beam_size=beam_size,
        vad_filter=vad_filter,
    )
    result: List[Dict[str, float | str]] = []
    for seg in segments:
        result.append(
            {
                "start": float(seg.start),
                "end": float(seg.end),
                "text": seg.text.strip(),
            }
        )
    return result


def segments_to_text(segments: List[Dict[str, float | str]]) -> str:
    """Convert a list of segments into a plain-text transcript.

    Args:
        segments: List of segments with a "text" field.

    Returns:
        A string containing the concatenated text from all segments separated by newlines.
    """
    lines: List[str] = []
    for seg in segments:
        text = str(seg.get("text", "")).strip()
        if text:
            lines.append(text)
    return "\n".join(lines)


def transcribe(
    audio_path: str,
    model_size: str = "medium",
    language: str = "th",
    beam_size: int = 5,
    vad_filter: bool = True,
) -> str:
    """Convenience function to transcribe an audio file and return plain text.

    Internally calls :func:`transcribe_to_segments` and then concatenates the segments.

    Args:
        audio_path: Path to the audio file.
        model_size: Whisper model size.
        language: Language code for transcription.
        beam_size: Beam size.
        vad_filter: Whether to filter silence.

    Returns:
        The full transcript as a single string separated by newlines.
    """
    segments = transcribe_to_segments(
        audio_path,
        model_size=model_size,
        language=language,
        beam_size=beam_size,
        vad_filter=vad_filter,
    )
    return segments_to_text(segments)
