
import os
import re
import uuid
import textwrap

from PIL import Image, ImageDraw, ImageFont, ImageOps
from gtts import gTTS
from moviepy.editor import (
    ImageClip,
    AudioFileClip,
    concatenate_videoclips,
)


# --------------------------------------------------
# PILLOW COMPATIBILITY FIX
# --------------------------------------------------

# MoviePy 1.x expects Image.ANTIALIAS.
# Pillow 10+ removed it, so provide the modern equivalent.
if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.Resampling.LANCZOS


# --------------------------------------------------
# VIDEO CONFIGURATION
# --------------------------------------------------

VIDEO_SIZE = {
    "9:16": (720, 1280),
    "16:9": (1280, 720),
    "1:1": (900, 900),
}


# --------------------------------------------------
# MARKETING SCRIPT GENERATION
# --------------------------------------------------

def build_script(product_name, description, benefits, cta):
    """Create a promotional script from the supplied product details."""

    benefit_list = [
        item.strip(" •-*")
        for item in re.split(r"[\n,;]+", benefits or "")
        if item.strip(" •-*")
    ]

    hook = "Meet " + product_name.strip() + "!"

    product_description = description.strip().rstrip(".!?")

    benefit_sentence = ""
    if benefit_list:
        benefit_sentence = (
            " Key features include "
            + ", ".join(benefit_list[:4])
            + "."
        )

    call_to_action = (cta or "Shop now").strip().rstrip(".")

    return (
        hook
        + " Looking for a product that fits your needs? "
        + product_description
        + "."
        + benefit_sentence
        + " "
        + call_to_action
        + " today!"
    )


# --------------------------------------------------
# FONT LOADING
# --------------------------------------------------

def load_font(size, bold=False):
    """Load a suitable font on Windows, Linux, or macOS."""

    if os.name == "nt":
        candidates = [
            "C:/Windows/Fonts/arialbd.ttf" if bold
            else "C:/Windows/Fonts/arial.ttf",
        ]
    else:
        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
            if bold else
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",

            "/Library/Fonts/Arial Bold.ttf" if bold
            else "/Library/Fonts/Arial.ttf",
        ]

    for font_path in candidates:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size=size)
            except OSError:
                continue

    return ImageFont.load_default()


# --------------------------------------------------
# IMAGE PREPROCESSING
# --------------------------------------------------

def fit_and_crop(image_path, size):
    """Resize and crop an image to the selected video dimensions."""

    with Image.open(image_path) as original:
        image = ImageOps.exif_transpose(original).convert("RGB")

    return ImageOps.fit(
        image,
        size,
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.5),
    )


# --------------------------------------------------
# TEXT OVERLAY AND SCENE CREATION
# --------------------------------------------------

def make_scene(image_path, size, heading, body, output_path):
    """Create a promotional image frame with readable text overlays."""

    image = fit_and_crop(image_path, size).convert("RGBA")
    width, height = size

    # Create a transparent overlay for the dark gradient.
    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    gradient_top = int(height * 0.52)

    for y in range(gradient_top, height):
        alpha = int(
            190 * (y - gradient_top)
            / max(1, height - gradient_top)
        )

        draw.line(
            (0, y, width, y),
            fill=(0, 0, 0, alpha),
        )

    image = Image.alpha_composite(image, overlay)
    draw = ImageDraw.Draw(image)

    heading_font = load_font(
        max(28, int(width * 0.065)),
        bold=True,
    )

    body_font = load_font(
        max(20, int(width * 0.035))
    )

    margin = int(width * 0.07)

    heading_width = max(
        15,
        int(width / max(1, heading_font.size * 0.55)),
    )

    body_width = max(
        20,
        int(width / max(1, body_font.size * 0.55)),
    )

    heading_lines = textwrap.wrap(
        heading or "",
        width=heading_width,
    )

    body_lines = textwrap.wrap(
        body or "",
        width=body_width,
    )

    y = int(height * 0.64)

    # Draw heading.
    for line in heading_lines[:3]:
        draw.text(
            (margin, y),
            line,
            font=heading_font,
            fill=(255, 255, 255, 255),
            stroke_width=1,
            stroke_fill=(0, 0, 0, 180),
        )

        y += int(heading_font.size * 1.2)

    y += int(body_font.size * 0.5)

    # Draw description or call to action.
    for line in body_lines[:5]:
        draw.text(
            (margin, y),
            line,
            font=body_font,
            fill=(255, 255, 255, 255),
            stroke_width=1,
            stroke_fill=(0, 0, 0, 160),
        )

        y += int(body_font.size * 1.35)

    image.convert("RGB").save(
        output_path,
        quality=94,
    )

    return output_path


# --------------------------------------------------
# MAIN VIDEO GENERATION FUNCTION
# --------------------------------------------------

def create_marketing_video(
    product_name,
    description,
    benefits,
    cta,
    image_paths,
    output_dir,
    aspect_ratio="9:16",
    language="en",
):
    """
    Generate a promotional MP4 from product images and text.

    Returns:
        Dictionary containing the generated filename and script.
    """

    if not product_name or not product_name.strip():
        raise ValueError("Please provide a product name.")

    if not description or not description.strip():
        raise ValueError("Please provide a product description.")

    if not image_paths:
        raise ValueError("Upload at least one product image.")

    if aspect_ratio not in VIDEO_SIZE:
        aspect_ratio = "9:16"

    # Validate image files before starting.
    for image_path in image_paths:
        if not os.path.isfile(image_path):
            raise FileNotFoundError(
                "Image file not found: " + str(image_path)
            )

    os.makedirs(output_dir, exist_ok=True)

    job_id = uuid.uuid4().hex[:10]
    width_height = VIDEO_SIZE[aspect_ratio]

    script = build_script(
        product_name,
        description,
        benefits,
        cta,
    )

    audio_path = os.path.join(
        output_dir,
        job_id + "_voice.mp3",
    )

    temp_images = []
    clips = []
    audio_clip = None
    video = None

    try:
        # ------------------------------------------
        # 1. Generate voice narration
        # ------------------------------------------

        try:
            gTTS(
                text=script,
                lang=language,
            ).save(audio_path)

            audio_clip = AudioFileClip(audio_path)

        except Exception as error:
            print(
                "Narration unavailable; generating "
                "video without audio:",
                error,
            )

            audio_clip = None

        # ------------------------------------------
        # 2. Prepare promotional scenes
        # ------------------------------------------

        scene_texts = [
            (
                product_name,
                description,
            ),
            (
                "Why choose " + product_name + "?",
                benefits or description,
            ),
            (
                "Get yours today!",
                cta or "Shop now",
            ),
        ]

        scene_duration = 4

        for index, (heading, body) in enumerate(scene_texts):

            # Reuse the last image if fewer than 3 images exist.
            source = image_paths[
                min(index, len(image_paths) - 1)
            ]

            frame_path = os.path.join(
                output_dir,
                job_id + "_scene_" + str(index) + ".jpg",
            )

            make_scene(
                source,
                width_height,
                heading,
                body,
                frame_path,
            )

            temp_images.append(frame_path)

            # Create a scene clip.
            clip = ImageClip(frame_path).set_duration(
                scene_duration
            )

            clips.append(clip)

        # ------------------------------------------
        # 3. Combine the scenes
        # ------------------------------------------

        video = concatenate_videoclips(
            clips,
            method="compose",
        )

        # ------------------------------------------
        # 4. Add narration and synchronize duration
        # ------------------------------------------

        if audio_clip is not None:

            if audio_clip.duration > video.duration:
                # Extend the final scene to fit narration.
                extra_duration = (
                    audio_clip.duration - video.duration
                )

                clips[-1] = clips[-1].set_duration(
                    scene_duration + extra_duration
                )

                video.close()

                video = concatenate_videoclips(
                    clips,
                    method="compose",
                )

            elif audio_clip.duration < video.duration:
                # Avoid audio extending beyond the video.
                audio_clip = audio_clip.set_duration(
                    video.duration
                )

            video = video.set_audio(audio_clip)

        # ------------------------------------------
        # 5. Export the final MP4
        # ------------------------------------------

        filename = job_id + "_marketing_video.mp4"

        output_path = os.path.join(
            output_dir,
            filename,
        )

        video.write_videofile(
            output_path,
            fps=24,
            codec="libx264",
            audio_codec=(
                "aac" if audio_clip is not None else None
            ),
            preset="medium",
            threads=2,
            logger=None,
        )

        print("Video generated successfully:", output_path)

        return {
            "filename": filename,
            "script": script,
        }

    finally:
        # ------------------------------------------
        # 6. Release resources and clean temporary files
        # ------------------------------------------

        if video is not None:
            try:
                video.close()
            except Exception:
                pass

        for clip in clips:
            try:
                clip.close()
            except Exception:
                pass

        if audio_clip is not None:
            try:
                audio_clip.close()
            except Exception:
                pass

        for path in temp_images:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except OSError:
                pass

        try:
            if os.path.exists(audio_path):
                os.remove(audio_path)
        except OSError:
            pass
