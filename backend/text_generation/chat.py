import torch
from transformers import pipeline

chat_pipeline = None

def init_chat():
    global chat_pipeline
    device = 0 if torch.cuda.is_available() else -1
    print("Loading Text Generation Model...")
    chat_pipeline = pipeline(
        "text-generation",
        model="HuggingFaceTB/SmolLM2-360M-Instruct",
        device=device
    )

def generate_chat_reply(history: str, message: str) -> str:
    if chat_pipeline is None:
        init_chat()
        if chat_pipeline is None:
            raise RuntimeError("Failed to initialize chat pipeline")
    
    prompt = f"{history}\nYOU: {message}\nMUNCH:"
    
    result = chat_pipeline(
        prompt,
        max_new_tokens=50,
        do_sample=True,
        temperature=0.7,
        top_p=0.9
    )
    
    generated_text = result[0]['generated_text']
    reply = generated_text[len(prompt):].strip()
    reply = reply.split('\n')[0]  # Just take the first line to avoid rambling
    
    return reply
