import math
import os
import threading
import time

import psutil
from flask import Flask, render_template
from flask_cors import CORS
from PIL import Image


app = Flask(__name__)
CORS(app)


startup_start_flask = time.time()



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


@app.route("/health")
def health_check():
    return "OK", 200


duration = round(time.time() - startup_start_flask, 10)

@app.route("/startup")
def startup_time():
    return render_template("startup.html", duration=duration)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
