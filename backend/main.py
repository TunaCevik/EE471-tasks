import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "speech_to_text"))
sys.path.append(os.path.join(os.path.dirname(__file__), "text_generation"))
sys.path.append(os.path.join(os.path.dirname(__file__), "image_generation"))

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
import uvicorn
from speech_to_text import asr
from image_generation import image_gen
from text_generation import chat

app = FastAPI(title="RoboMunch API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    # Pre-load models
    asr.init_asr()
    chat.init_chat()
    image_gen.init_image_gen()

@app.post("/api/speech-to-text")
async def speech_to_text(audio: UploadFile = File(...)):
    try:
        audio_data = await audio.read()
        temp_audio_path = "temp_audio.wav"
        with open(temp_audio_path, "wb") as f:
            f.write(audio_data)
        
        text = asr.transcribe(temp_audio_path)
        
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
            
        return {"text": text}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/api/chat")
def chat_endpoint(message: str = Form(...), history: str = Form("")):
    try:
        reply = chat.generate_chat_reply(history, message)
        return {"reply": reply}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/api/generate-image")
def generate_image(prompt: str = Form(...)):
    try:
        img_bytes = image_gen.generate_image_from_prompt(prompt)
        return Response(content=img_bytes, media_type="image/png")
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
