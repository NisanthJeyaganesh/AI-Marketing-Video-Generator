import os
import uuid
from flask import Flask, render_template, request, send_from_directory, flash, redirect, url_for
from werkzeug.utils import secure_filename
from video_generator import create_marketing_video

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "outputs")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change-this-in-production")
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024  # 20 MB per request


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET", "POST"])
def index():
    video_url = None
    script_preview = None

    if request.method == "POST":
        product_name = request.form.get("product_name", "").strip()
        description = request.form.get("description", "").strip()
        benefits = request.form.get("benefits", "").strip()
        cta = request.form.get("cta", "Shop now").strip() or "Shop now"
        aspect_ratio = request.form.get("aspect_ratio", "9:16")
        language = request.form.get("language", "en")

        if not product_name or not description:
            flash("Please enter a product name and description.", "error")
            return redirect(url_for("index"))

        uploaded = request.files.getlist("images")
        image_paths = []
        for item in uploaded:
            if item and item.filename:
                if not allowed_file(item.filename):
                    flash("Use PNG, JPG, JPEG, or WEBP images.", "error")
                    return redirect(url_for("index"))
                safe_name = secure_filename(item.filename)
                unique_name = f"{uuid.uuid4().hex}_{safe_name}"
                path = os.path.join(UPLOAD_FOLDER, unique_name)
                item.save(path)
                image_paths.append(path)

        if not image_paths:
            flash("Upload at least one product image.", "error")
            return redirect(url_for("index"))

        try:
            result = create_marketing_video(
                product_name=product_name,
                description=description,
                benefits=benefits,
                cta=cta,
                image_paths=image_paths,
                output_dir=OUTPUT_FOLDER,
                aspect_ratio=aspect_ratio,
                language=language,
            )
            video_url = url_for("download_video", filename=result["filename"])
            script_preview = result["script"]
        except Exception as exc:
            app.logger.exception("Video generation failed")
            flash(f"Video generation failed: {exc}", "error")

    return render_template("index.html", video_url=video_url, script_preview=script_preview)


@app.route("/outputs/<path:filename>")
def download_video(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
