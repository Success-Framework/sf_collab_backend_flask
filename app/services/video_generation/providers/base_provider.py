from abc import ABC, abstractmethod


class BaseVideoProvider(ABC):
    """
    Abstract base class for all video providers.
    """

    @abstractmethod
    def generate(
        self,
        *,
        mode: str,
        prompt: str,
        duration: int,
        input_files: dict
    ) -> dict:
        """
        Generate a video.

        Returns:
        {
            "filename": "output.mp4",
            "path": "/abs/path/to/file"
        }
        """
        pass
