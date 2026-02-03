def build_image_scenes(images, base_prompt):
    """
    Convert multiple images into scene-based prompts.
    """

    scenes = []

    for index, img in enumerate(images, start=1):
        scenes.append({
            "scene": index,
            "prompt": f"""
Scene {index}:
Animate this image with smooth natural motion.
Maintain visual consistency and cinematic lighting.
Base style:
{base_prompt}
""",
            "image": img
        })

    return scenes
