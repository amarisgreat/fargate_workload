import time
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from pose_model import predict as predict_pose
from litter_model import predict_litter
import os

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

        with open(r"images/image1.jpg", "rb") as f1:
            image1 = f1.read()
        pose_result = predict_pose(image1)
        if pose_result.get("probability", 0) < THRESHOLD:
            pose_result = {"class": "No chicken detected", "probability": 0.0}

        with open(r"images/image2.jpg", "rb") as f2:
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

    except FileNotFoundError as fnf_error:
        return render_template("error.html", error=f"File not found: {fnf_error}"), 404
    except Exception as e:
        return render_template("error.html", error=str(e)), 500



# @app.route("/predict", methods=["GET"])
# def predict_combined():
#     try:

#         with open(r"images/image1.jpg", "rb") as f1:
#             image1 = f1.read()
#         pose_result = predict_pose(image1)
#         if pose_result.get("probability", 0) < THRESHOLD:
#             pose_result = {"class": "No chicken detected", "probability": 0.0}


#         with open(r"images/image2.jpg", "rb") as f2:
#             image2 = f2.read()
#         litter_result = predict_litter(image2)
#         if litter_result.get("probability", 0) < THRESHOLD:
#             litter_result = {"class": "No litter detected", "probability": 0.0}

#         return jsonify({
#             "pose_prediction": pose_result,
#             "litter_prediction": litter_result
#         })

#     except FileNotFoundError as fnf_error:
#         return jsonify({"error": f"File not found: {fnf_error}"}), 404
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500




@app.route("/healthz")
def health_check():
    return "OK", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
