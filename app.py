from flask import Flask, render_template, request, send_file, jsonify
import os
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

# Load environment variables (e.g., SPEECH_KEY, SPEECH_REGION)
load_dotenv()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/tts', methods=['POST'])
def text_to_speech():
    data = request.json
    text = data.get('text')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
        
    try:
        speech_key = os.environ.get('SPEECH_KEY')
        speech_region = os.environ.get('SPEECH_REGION')
        if not speech_key or not speech_region:
            return jsonify({'error': 'Azure credentials are not configured properly.'}), 500

        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
        
        # Save to buffer/file to return audio directly
        temp_filename = "temp_output.wav"
        audio_config = speechsdk.audio.AudioOutputConfig(filename=temp_filename)
        
        speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
        
        result = speech_synthesizer.speak_text_async(text).get()
        
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            return send_file(temp_filename, mimetype="audio/wav", as_attachment=False)
        else:
            return jsonify({'error': f"Speech synthesis canceled. Reason: {result.reason}"}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
