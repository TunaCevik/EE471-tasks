from flask import Flask, render_template, request, send_file, jsonify
import os
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

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
            return jsonify({'error': 'Azure credentials missing.'}), 500

        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
        temp_filename = "temp_tts_output.wav"
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


@app.route('/api/stt', methods=['POST'])
def speech_to_text():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
        
    audio_file = request.files['audio']
    temp_filename = "temp_stt_input.wav"
    audio_file.save(temp_filename)
    
    try:
        speech_key = os.environ.get('SPEECH_KEY')
        speech_region = os.environ.get('SPEECH_REGION')
        if not speech_key or not speech_region:
            return jsonify({'error': 'Azure credentials missing.'}), 500

        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)
        audio_config = speechsdk.audio.AudioConfig(filename=temp_filename)
        
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
        
        result = speech_recognizer.recognize_once_async().get()
        
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            return jsonify({'text': result.text})
        elif result.reason == speechsdk.ResultReason.NoMatch:
            return jsonify({'error': 'No speech could be recognized.'}), 400
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            return jsonify({'error': f'Speech Recognition canceled: {cancellation_details.reason}. Error details: {cancellation_details.error_details}'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
