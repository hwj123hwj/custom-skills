"""
Abstract base class for ASR providers.

To add a new provider:
1. Create a new file in this directory (e.g. myservice_provider.py)
2. Subclass ASRProvider and implement transcribe()
3. Register it in registry.py
"""

from abc import ABC, abstractmethod
from typing import Optional
from dataclasses import dataclass


@dataclass
class ASRResult:
    """Result of an ASR transcription."""
    text: str
    language: str = ""
    duration: float = 0.0
    provider: str = ""


class ASRProvider(ABC):
    """Interface for ASR backends."""

    @abstractmethod
    def transcribe(
        self,
        audio_path: str,
        language: str = "zh",
    ) -> Optional[ASRResult]:
        """
        Transcribe an audio file.

        Args:
            audio_path: Path to the audio file (wav/mp3/m4a/etc).
            language:   Language code (zh, en, ja, etc.) or "auto" for auto-detect.

        Returns:
            ASRResult with the transcription text, or None on failure.
        """
        ...
