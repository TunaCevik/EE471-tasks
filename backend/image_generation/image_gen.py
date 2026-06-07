import os
import requests
import torch
from diffusers import StableDiffusionPipeline
import io

# =========================================================================
# TOGGLE THIS VARIABLE TO SWITCH BETWEEN CLOUD AND LOCAL GENERATION
# =========================================================================
# True  -> Uses Pollinations.ai (Instant, Free, 0GB VRAM)
# False -> Uses Local GTX 1650 (Slower, requires 4GB VRAM)
USE_CLOUD_API = False

image_pipe = None

def init_image_gen():
    if USE_CLOUD_API:
        print("Loading Image Generation Model... [CLOUD MODE: Pollinations.ai]")
    else:
        global image_pipe
        print("Loading Image Generation Model... [LOCAL GPU MODE: stabilityai/sd-turbo]")
        # Using float32 avoids the NaN/black image bug on older GTX 16xx GPUs
        dtype = torch.float32
        image_pipe = StableDiffusionPipeline.from_pretrained(
            "stabilityai/sd-turbo", 
            torch_dtype=dtype,
            safety_checker=None
        )
        if torch.cuda.is_available():
            image_pipe = image_pipe.to("cuda")
            image_pipe.enable_attention_slicing()

def generate_image_from_prompt(prompt: str) -> bytes:
    if USE_CLOUD_API:
        # --------------------------------------------------
        # CLOUD WAY (Pollinations.ai)
        # --------------------------------------------------
        safe_prompt = prompt.strip().replace(" ", "%20")
        url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=512&height=512&nologo=true"
        
        print(f"Fetching image from cloud API: {url}")
        response = requests.get(url)
        
        if response.status_code == 200:
            return response.content
        else:
            raise Exception(f"Cloud API failed with status code: {response.status_code}")
            
    else:
        # --------------------------------------------------
        # LOCAL WAY (Stable Diffusion on GPU)
        # --------------------------------------------------
        if image_pipe is None:
            init_image_gen()
            if image_pipe is None:
                raise RuntimeError("Failed to initialize image pipeline")
            
        # Using SD-Turbo with 1 step and 0.0 guidance scale (Takes 5-10s on GTX 1650 Ti)
        image = image_pipe(prompt, num_inference_steps=1, guidance_scale=0.0).images[0]
        
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        return img_byte_arr.getvalue()
