from flask import current_app
from app.services.video_generation.providers.mock_provider import MockVideoProvider
from app.services.video_generation.providers.runway_provider import RunwayVideoProvider


def get_video_provider():
    provider = current_app.config.get("VIDEO_PROVIDER", "mock")

    if provider == "runway":
        return RunwayVideoProvider()

    return MockVideoProvider()

