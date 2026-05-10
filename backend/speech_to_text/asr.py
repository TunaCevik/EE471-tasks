import torch
from transformers import pipeline
import os

asr_pipeline = None

def init_asr():
    global asr_pipeline
    device = 0 if torch.cuda.is_available() else -1
    print("Loading Speech-to-Text Model...")
    asr_pipeline = pipeline(
        "automatic-speech-recognition", 
        model="openai/whisper-tiny", 
        device=device
    )

def transcribe(audio_path: str) -> str:
    if asr_pipeline is None:
        init_asr()
        if asr_pipeline is None:
            raise RuntimeError("Failed to initialize asr pipeline")

    result = asr_pipeline(audio_path)
    return result["text"]
