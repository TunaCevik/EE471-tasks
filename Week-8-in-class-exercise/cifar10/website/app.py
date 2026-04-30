import os
import requests
from flask import Flask, request, render_template, jsonify
import base64

app = Flask(__name__)

# Cog containers URIs
BASE_MODEL_URL = os.environ.get("BASE_MODEL_URL", "http://base-model:5000/predictions")
OPTIMIZED_MODEL_URL = os.environ.get("OPTIMIZED_MODEL_URL", "http://optimized-model:5000/predictions")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "file" not in request.files:
            return jsonify({"error": "No file part"}), 400
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"error": "No selected file"}), 400
            
        file_content = file.read()
        encoded_image = base64.b64encode(file_content).decode("utf-8")
        data_uri = f"data:{file.content_type};base64,{encoded_image}"

        base_result = {}
        try:
            resp1 = requests.post(BASE_MODEL_URL, json={"input": {"image": data_uri}}, timeout=10)
            if resp1.status_code == 200:
                base_result = resp1.json().get("output", {})
            else:
                base_result = {"error": f"Base Model error {resp1.status_code}"}
        except Exception as e:
            base_result = {"error": str(e)}

        optimized_result = {}
        try:
            resp2 = requests.post(OPTIMIZED_MODEL_URL, json={"input": {"image": data_uri}}, timeout=10)
            if resp2.status_code == 200:
                optimized_result = resp2.json().get("output", {})
            else:
                optimized_result = {"error": f"Optimized Model error {resp2.status_code}"}
        except Exception as e:
            optimized_result = {"error": str(e)}

        return jsonify({
            "base": base_result,
            "optimized": optimized_result,
            "image": data_uri
        })
        
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
