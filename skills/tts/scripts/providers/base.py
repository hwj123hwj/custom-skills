"""
Abstract base class for TTS providers.

To add a new provider:
1. Create a new file in this directory (e.g. myservice_provider.py)
2. Subclass TTSProvider and implement synthesize()
3. Register it in registry.py
"""

from abc import ABC, abstractmethod
from typing import Optional
from dataclasses import dataclass


@dataclass
class TTSResult:
    """Result of a TTS synthesis."""
    output_path: str
    duration: float = 0.0
    provider: str = ""


class TTSProvider(ABC):
    """Interface for TTS backends."""

    @abstractmethod
    def synthesize(
        self,
        text: str,
        output_path: str,
        voice: str = "",
        language: str = "",
        speed: float = 1.0,
    ) -> Optional[TTSResult]:
        """
        Synthesize text to speech and save to file.

        Args:
            text:        Text to convert to speech.
            output_path: Where to save the audio file.
            voice:       Voice name (provider-specific).
            language:    Language code (e.g. zh-CN, en-US).
            speed:       Speech speed multiplier (1.0 = normal).

        Returns:
            TTSResult with the output path, or None on failure.
        """
        ...
