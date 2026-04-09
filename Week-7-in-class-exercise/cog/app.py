import os
import base64
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# This allows us to point to the Cog container when using Docker Compose
# If running locally without Compose, it defaults to localhost
MODEL_API_URL = os.environ.get('MODEL_API_URL', 'http://localhost:5000/predictions')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/classify', methods=['POST'])
def classify_cat():
    if 'cat_image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
        
    file = request.files['cat_image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        # Convert the uploaded image to a base64 Data URI
        base64_encoded = base64.b64encode(file.read()).decode('utf-8')
        mime_type = file.mimetype
        data_uri = f"data:{mime_type};base64,{base64_encoded}"
        
        # Format the payload exactly how the Cog API expects it
        payload = {
            "input": {
                "image": data_uri
            }
        }
        
        # Send the request to the Cog model
        response = requests.post(MODEL_API_URL, json=payload)
        response.raise_for_status() # Raise an exception for bad status codes
        
        # Return the model's predictions to the frontend
        return jsonify(response.json())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)