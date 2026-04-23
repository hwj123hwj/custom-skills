"""
Abstract base class for image generation providers.

To add a new provider:
1. Create a new file in this directory (e.g. myservice_provider.py)
2. Subclass ImageProvider and implement generate()
3. Register it in registry.py
"""

from abc import ABC, abstractmethod
from typing import Optional


class ImageProvider(ABC):
    """Interface for image generation backends."""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        size: str,
        ratio: str,
        output_path: str,
    ) -> Optional[str]:
        """
        Generate an image and save it to output_path.

        Args:
            prompt:      Text description of the image.
            size:        Canonical size string (0.5K / 1024x1024 / 1024x1792 / 1792x1024 / 2K / 4K).
            ratio:       Aspect ratio string (1:1 / 16:9 / 9:16 / 4:3 / 3:4).
            output_path: Absolute path where the image should be saved.

        Returns:
            Absolute path to the saved image, or None on failure.
        """
        ...
