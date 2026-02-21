import os
from werkzeug.datastructures import FileStorage

# ---------- CONFIG ----------
ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
ALLOWED_VIDEO_EXTENSIONS = {"mp4", "mov", "webm"}
MAX_IMAGE_COUNT = 5
MAX_IMAGE_SIZE_MB = 5
MAX_VIDEO_SIZE_MB = 50


def _get_extension(filename: str) -> str:
    return filename.rsplit(".", 1)[-1].lower()


def _file_size_mb(file: FileStorage) -> float:
    file.seek(0, os.SEEK_END)
    size = file.tell() / (1024 * 1024)
    file.seek(0)
    return size


def validate_files(mode: str, files) -> dict:
    """
    Validate uploaded files based on mode.
    Returns prepared inputs for provider.
    """

    prepared_inputs = {
        "images": [],
        "video": None
    }

    # ------------------------
    # TEXT → VIDEO
    # ------------------------
    if mode == "text":
        if files:
            raise ValueError("Files are not allowed for text-to-video")
        return prepared_inputs

    # ------------------------
    # IMAGE → VIDEO
    # ------------------------
    if mode == "image":
        images = files.getlist("images")

        if not images:
            raise ValueError("At least one image is required")

        if len(images) > MAX_IMAGE_COUNT:
            raise ValueError("Maximum 5 images allowed")

        for img in images:
            ext = _get_extension(img.filename)
            if ext not in ALLOWED_IMAGE_EXTENSIONS:
                raise ValueError(f"Unsupported image format: {ext}")

            size = _file_size_mb(img)
            if size > MAX_IMAGE_SIZE_MB:
                raise ValueError("Each image must be under 5MB")

            prepared_inputs["images"].append(img)

        return prepared_inputs

    # ------------------------
    # VIDEO → VIDEO
    # ------------------------
    if mode == "video":
        video = files.get("video")

        if not video:
            raise ValueError("Video file is required")

        ext = _get_extension(video.filename)
        if ext not in ALLOWED_VIDEO_EXTENSIONS:
            raise ValueError("Unsupported video format")

        size = _file_size_mb(video)
        if size > MAX_VIDEO_SIZE_MB:
            raise ValueError("Video must be under 50MB")

        prepared_inputs["video"] = video
        return prepared_inputs

    raise ValueError("Invalid mode")
