import subprocess
import os
import uuid


def trim_video(input_path, start, end):
    output_path = _temp_video_path()

    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-ss", str(start),
        "-to", str(end),
        "-c", "copy",
        output_path
    ]

    _run(cmd)
    return output_path


def add_subtitles(input_path, subtitle_path):
    output_path = _temp_video_path()

    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-vf", f"subtitles={subtitle_path}",
        output_path
    ]

    _run(cmd)
    return output_path


def _temp_video_path():
    base_dir = os.path.join(
        os.getcwd(),
        "uploads",
        "video_temp"
    )
    os.makedirs(base_dir, exist_ok=True)
    return os.path.join(base_dir, f"tmp_{uuid.uuid4().hex}.mp4")


def _run(cmd):
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    if result.returncode != 0:
        raise Exception(result.stderr.decode())
