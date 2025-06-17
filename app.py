import os
import time

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from PIL import Image

from litter_model import predict_litter
from pose_model import predict as predict_pose

app = Flask(__name__)
CORS(app)

THRESHOLD = 60.0

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/ping')
def ping():
    start = time.time()
    duration = round(time.time() - start, 4)
    return render_template('ping.html', delay=duration)

@app.route('/fib')
def cpu_task():
    def fib(n):
        return fib(n - 1) + fib(n - 2) if n > 1 else n
    start = time.time()
    result = fib(30)
    duration = round(time.time() - start, 4)
    return render_template('fib.html', result=result, duration=duration)




@app.route("/predict", methods=["GET"])
def predict_combined():
    try:
        cpu_start = time.process_time()
        wall_start = time.time()

        pose_image_path = os.path.join("images", "image1.jpg")
        litter_image_path = os.path.join("images", "image2.jpg")


        if not os.path.exists(pose_image_path):
            return render_template("error.html", error=f"File not found: {pose_image_path}"), 404
        if not os.path.exists(litter_image_path):
            return render_template("error.html", error=f"File not found: {litter_image_path}"), 404


        with open(pose_image_path, "rb") as f1:
            image1 = f1.read()
        pose_result = predict_pose(image1)
        if pose_result.get("probability", 0) < THRESHOLD:
            pose_result = {"class": "No chicken detected", "probability": 0.0}

        with open(litter_image_path, "rb") as f2:
            image2 = f2.read()
        litter_result = predict_litter(image2)
        if litter_result.get("probability", 0) < THRESHOLD:
            litter_result = {"class": "No litter detected", "probability": 0.0}

        cpu_duration = round(time.process_time() - cpu_start, 4)
        wall_duration = round(time.time() - wall_start, 4)

        

        return render_template("predict.html",
                               pose=pose_result,
                               litter=litter_result,
                               cpu_time=cpu_duration,
                               wall_time=wall_duration)

    except Exception as e:
        return render_template("error.html", error=str(e)), 500

@app.route("/convert", methods=["GET"])
def convert_image():
    cpu_start = time.process_time()
    wall_start = time.time()

    INPUT_PATH = os.path.join("images", "image.jpg")
    OUTPUT_PATH = os.path.join("images", "output.jpg")

    if not os.path.exists(INPUT_PATH):
        return render_template("error.html", error="File not found: images/image.jpg"), 404


    if os.path.exists(OUTPUT_PATH):
        os.remove(OUTPUT_PATH)

    try:

        image = Image.open(INPUT_PATH).convert("L")
        image.save(OUTPUT_PATH)


        import shutil
        shutil.copy(OUTPUT_PATH, os.path.join("static", "output.jpg"))

        cpu_duration = round(time.process_time() - cpu_start, 4)
        wall_duration = round(time.time() - wall_start, 4)

        return render_template("convert.html",
                               cpu_time=cpu_duration,
                               wall_time=wall_duration)
    except Exception as e:
        return render_template("error.html", error=f"Image conversion failed: {str(e)}"), 500

@app.route("/debug")
def debug():
    info = {
        "cwd": os.getcwd(),
        "input_exists": os.path.exists("images/image.jpg"),
        "output_exists": os.path.exists("images/output.jpg"),
        "convert_template": os.path.exists("templates/convert.html"),
        "error_template": os.path.exists("templates/error.html"),
        "model_image1": os.path.exits("images/image1.jpg"),
        "model_image2": os.path.exits("images/image2.jpg"),
    }
    return jsonify(info)


@app.route("/healthz")
def health_check():
    return "OK", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
