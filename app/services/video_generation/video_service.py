from app.services.video_generation.provider_router import get_video_provider


def generate_video(
    *,
    mode: str,
    prompt: str,
    duration: int,
    input_files: dict
) -> dict:
    provider = get_video_provider()

    return provider.generate(
        mode=mode,
        prompt=prompt,
        duration=duration,
        input_files=input_files
    )
