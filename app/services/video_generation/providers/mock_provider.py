import os
import uuid
from flask import current_app


class MockVideoProvider:
    """
    Temporary provider that simulates video generation.
    """

    def generate(
        self,
        *,
        mode: str,
        prompt: str,
        duration: int,
        input_files: dict
    ) -> dict:

        output_dir = os.path.join(
            current_app.root_path,
            "..",
            "..",
            "uploads",
            "video_output"
        )
        os.makedirs(output_dir, exist_ok=True)

        filename = f"mock_video_{uuid.uuid4().hex}.mp4"
        filepath = os.path.join(output_dir, filename)

        # Create a dummy file (placeholder)
        with open(filepath, "wb") as f:
            f.write(b"")

        return {
            "filename": filename,
            "path": filepath
        }
