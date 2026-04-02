from flask import Flask, render_template
import os
from dotenv import load_dotenv

# Load environment variables (e.g., SPEECH_KEY, SPEECH_REGION)
load_dotenv()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
