from flask import Flask, request, render_template, send_file
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.editor import concatenate_videoclips
#from moviepy import concatenate_videoclips
import os
import random
import uuid

app = Flask(__name__)

# Directory structure
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

CATEGORIES = ["hook", "body1", "body2", "body3", "call_to_action"]

# Ensure directories exist
for category in CATEGORIES:
    os.makedirs(os.path.join(UPLOAD_DIR, category), exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Handle file uploads
        category = request.form.get("category")
        files = request.files.getlist("files")
        if category and files:
            for file in files:
                save_path = os.path.join(UPLOAD_DIR, category, file.filename)
                file.save(save_path)
        return "Files uploaded successfully!"
    return render_template("index.html", categories=CATEGORIES)

@app.route("/merge", methods=["POST"])
def merge_videos():
    try:
        num_videos = int(request.form.get("num_videos", 1))
        generated_files = []
        for i in range(num_videos):
            # Randomly select one file from each category
            selected_clips = []
            for category in CATEGORIES:
                folder = os.path.join(UPLOAD_DIR, category)
                files = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(('.mp4', '.avi', '.mov'))]
                if not files:
                    return f"Error: No videos found in {category} folder!", 400
                selected_clips.append(random.choice(files))

            # Load and concatenate video clips
            video_clips = [VideoFileClip(clip) for clip in selected_clips]
            final_clip = concatenate_videoclips(video_clips)

            # Save merged video
            output_filename = f"merged_video_{uuid.uuid4().hex[:8]}.mp4"
            output_path = os.path.join(OUTPUT_DIR, output_filename)
            final_clip.write_videofile(output_path, codec="libx264")

            # Close clips
            final_clip.close()
            for clip in video_clips:
                clip.close()

            generated_files.append(output_filename)

        return render_template("result.html", files=generated_files)
    except Exception as e:
        return f"Error: {e}", 500

@app.route("/download/<filename>")
def download_file(filename):
    file_path = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return "File not found!", 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Default to 5000 if PORT is not set
    app.run(host="0.0.0.0", port=port, debug=True)
