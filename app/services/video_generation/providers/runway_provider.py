import os
import time
import uuid
import requests
from flask import current_app
from app.services.video_generation.scene_builder import build_image_scenes
from app.services.video_generation.ffmpeg_utils import (
    trim_video,
    add_subtitles
)
from app.services.video_generation.subtitle_service import generate_subtitles

class RunwayVideoProvider:
    """
    Real video generation provider (Runway-style API).
    Supports:
    - Text → Video
    - Image(s) → Video
    - Video → Video
    """

    BASE_URL = "https://api.runwayml.com/v1"

    # --------------------------------------------------
    # Public entry point (called by video_service)
    # --------------------------------------------------
    def generate(self, *, mode, prompt, duration, input_files):

        if mode == "text":
            return self._generate_text_video(prompt, duration)

        if mode == "image":
            return self._generate_image_video(
                prompt=prompt,
                duration=duration,
                images=input_files.get("images", [])
            )

        if mode == "video":
            return self._generate_video_edit(
                prompt=prompt,
                duration=duration,
                video=input_files.get("video")
            )

        raise Exception("Unsupported video generation mode")

    # --------------------------------------------------
    # TEXT → VIDEO
    # --------------------------------------------------
    def _generate_text_video(self, prompt, duration):
        payload = {
            "prompt": prompt,
            "duration": duration,
            "mode": "text"
        }

        job_id = self._submit_job(payload)
        video_url = self._poll_until_ready(job_id)
        return self._download_video(video_url)

    # --------------------------------------------------
    # IMAGE(S) → VIDEO
    # --------------------------------------------------
    def _generate_image_video(self, prompt, duration, images):
        if not images:
            raise Exception("No images provided for image-to-video")

        scenes = build_image_scenes(images, prompt)

        payload = {
            "mode": "image",
            "duration": duration,
            "scenes": []
        }

        # NOTE:
        # Real Runway API may require image uploads first.
        # This structure is intentionally abstracted.
        for scene in scenes:
            payload["scenes"].append({
                "prompt": scene["prompt"],
                "image_name": scene["image"].filename
            })

        job_id = self._submit_job(payload)
        video_url = self._poll_until_ready(job_id)
        return self._download_video(video_url)

    # --------------------------------------------------
    # VIDEO → VIDEO (EDIT / ENHANCE)
    # --------------------------------------------------
    def _generate_video_edit(self, prompt, duration, video):
        if not video:
            raise Exception("No video provided for video-to-video")

        payload = {
            "mode": "video_edit",
            "prompt": prompt,
            "duration": duration,
            "preserve_structure": True
        }

        job_id = self._submit_job(payload)
        video_url = self._poll_until_ready(job_id)
        return self._download_video(video_url)

    # --------------------------------------------------
    # Job submission (shared)
    # --------------------------------------------------
    def _submit_job(self, payload):
        response = requests.post(
            f"{self.BASE_URL}/video/generate",
            headers=self._headers(),
            json=payload,
            timeout=30
        )

        if response.status_code != 200:
            raise Exception(
                f"Video generation request failed: {response.text}"
            )

        job_id = response.json().get("id")
        if not job_id:
            raise Exception("No job ID returned from video provider")

        return job_id

    # --------------------------------------------------
    # Polling until ready (shared)
    # --------------------------------------------------
    def _poll_until_ready(self, job_id):
        max_attempts = 12      # ~1 minute total
        interval = 5           # seconds

        for _ in range(max_attempts):
            response = requests.get(
                f"{self.BASE_URL}/video/status/{job_id}",
                headers=self._headers(),
                timeout=15
            )

            if response.status_code != 200:
                raise Exception("Failed to poll video status")

            data = response.json()
            status = data.get("status")

            if status == "completed":
                return data.get("video_url")

            if status == "failed":
                raise Exception("Video generation failed")

            time.sleep(interval)

        raise Exception("Video generation timed out")

    # --------------------------------------------------
    # Download & store output video (shared)
    # --------------------------------------------------
    def _download_video(self, video_url):
        output_dir = os.path.join(
            current_app.root_path,
            "..",
            "..",
            "uploads",
            "video_output"
        )
        os.makedirs(output_dir, exist_ok=True)

        filename = f"video_{uuid.uuid4().hex}.mp4"
        filepath = os.path.join(output_dir, filename)

        with requests.get(video_url, stream=True) as r:
            r.raise_for_status()
            with open(filepath, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        return {
            "filename": filename,
            "path": filepath
        }
    def _generate_video_edit(self, prompt, duration, video):
        if not video:
            raise Exception("No video provided for video editing")

        # Save uploaded video locally
        base_dir = os.path.join(
            current_app.root_path,
            "..",
            "..",
            "uploads",
            "video_input"
        )
        os.makedirs(base_dir, exist_ok=True)

        input_path = os.path.join(base_dir, video.filename)
        video.save(input_path)

        working_path = input_path

        # ----------------------------
        # 1. Trim (example logic)
        # ----------------------------
        if duration:
            working_path = trim_video(
                input_path=working_path,
                start=0,
                end=duration
            )

        # ----------------------------
        # 2. Subtitles (if requested)
        # ----------------------------
        if "subtitle" in prompt.lower():
            subtitle_path = generate_subtitles(prompt, duration)
            working_path = add_subtitles(working_path, subtitle_path)

        # ----------------------------
        # 3. (Optional) AI enhancement
        # ----------------------------
        # You can send working_path to AI provider here later

        return {
            "filename": os.path.basename(working_path),
            "path": working_path
        }

    # --------------------------------------------------
    # Headers
    # --------------------------------------------------
    def _headers(self):
        return {
            "Authorization": f"Bearer {current_app.config.get('RUNWAY_API_KEY')}",
            "Content-Type": "application/json"
        }


# Route
#  → video_service
#    → provider.generate()
#      → mode-specific method
#        → submit job
#        → poll
#        → download
