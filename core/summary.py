"""
Summarization utilities for Voicelogger.

Provides simple extractive summarization for Thai text. For more advanced summarization,
it is recommended to integrate with a local language model (LLM) such as those
served via Ollama or other providers.
"""

import re
from typing import Optional


def simple_summary(text: str, max_sentences: int = 5) -> str:
    """Produce a simple summary by selecting the first few sentences or lines.

    This baseline function splits the input text using common sentence delimiters
    (periods, exclamation marks, question marks and newlines). It then returns
    the first ``max_sentences`` non-empty sentences joined by a space.

    Args:
        text: Input text to summarize.
        max_sentences: Maximum number of sentences to include in the summary.

    Returns:
        A summary string consisting of the first ``max_sentences`` sentences.
    """
    if not text or not text.strip():
        return ""
    # Split by sentence delimiters and newlines; Thai language often omits punctuation
    sentences = re.split(r"[\n\.\!\?]+", text)
    # Clean up whitespace and filter out empty strings
    sentences = [s.strip() for s in sentences if s.strip()]
    if not sentences:
        return text.strip()
    return " ".join(sentences[:max_sentences])


def summarize_with_model(text: str, provider: str = "ollama", model_name: str = "llama3") -> str:
    """Placeholder for advanced summarization using an external or local model.

    Depending on the ``provider``, this function could call out to an API or a
    locally running LLM to perform abstractive summarization or translation. For
    now, it raises ``NotImplementedError`` to indicate that integration is
    required.

    Args:
        text: Input text to summarize.
        provider: Name of the provider (e.g., ``"ollama"``).
        model_name: Name of the model to use.

    Returns:
        A summarized version of the text.

    Raises:
        NotImplementedError: This function is not yet implemented.
    """
    raise NotImplementedError(
        "Advanced summarization is not implemented. Use `simple_summary` or integrate an LLM."
    )
