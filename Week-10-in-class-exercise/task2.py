import gradio as gr
from transformers import pipeline
import gc

class HFPipelineManager:
    def __init__(self):
        pass

    def run_task(self, task: str, model_name: str, text_input: str = None, 
                 media_input=None, extra_input: str = None) -> str:
        try:
            print(f"Loading {model_name} for {task}")
            
            # 1. Load the model fresh
            if task in ["translation", "summarization"]:
                pipe = pipeline("text-generation", model=model_name, device=-1)
            elif task in ["ner"]:
                pipe = pipeline("ner", aggregation_strategy="simple", device=-1)
            else:
                pipe = pipeline(task, model=model_name, device=-1)

            # Variable to store our result before we delete the model
            final_output = ""

            # 2. Execute the task
            if task == "sentiment-analysis":
                result = pipe(text_input)
                final_output = f"Label: {result[0]['label']} | Score: {result[0]['score']:.4f}"

            elif task == "zero-shot-classification":
                labels = [label.strip() for label in extra_input.split(",")]
                result = pipe(text_input, candidate_labels=labels)
                final_output = f"Top Prediction: {result['labels'][0]} | Score: {result['scores'][0]:.4f}"

            elif task == "text-generation":
                result = pipe(text_input, max_new_tokens=50)
                final_output = result[0]['generated_text']

            elif task == "fill-mask":
                result = pipe(text_input)
                final_output = f"Top Prediction: {result[0]['sequence']} (Score: {result[0]['score']:.4f})"

            elif task == "ner":
                results = pipe(text_input)
                formatted = [f"{r['word']} ({r['entity_group']})" for r in results]
                final_output = ", ".join(formatted) if formatted else "No entities found."

            elif task == "question-answering":
                result = pipe(question=text_input, context=extra_input)
                final_output = f"Answer: {result['answer']} | Confidence: {result['score']:.4f}"

            elif task == "summarization":
                prompt = f"Summarize:\n\n{text_input}\n\nSummary:"
                result = pipe(prompt, max_new_tokens=60)
                final_output = result[0]['generated_text'].replace(prompt, "").strip()

            elif task == "translation":
                prompt = f"English: {text_input}\nSpanish translation:"
                result = pipe(prompt, max_new_tokens=60)
                final_output = result[0]['generated_text'].replace(prompt, "").strip()

            elif task == "image-classification":
                if media_input is None: return "Error: Please upload an image."
                result = pipe(media_input)
                final_output = f"Label: {result[0]['label']} | Score: {result[0]['score']:.4f}"

            elif task == "automatic-speech-recognition":
                if media_input is None: return "Error: Please upload audio."
                result = pipe(media_input)
                final_output = result['text']

            else:
                final_output = "Task not implemented yet."

            del pipe

            # 4. Return the saved result
            return final_output

        except Exception as e:
            print("Exception occured")


# ==========================================
# PART 2: The Gradio Frontend Interface
# ==========================================

hf_manager = HFPipelineManager()

TASK_MODELS = {
    "sentiment-analysis": "distilbert/distilbert-base-uncased-finetuned-sst-2-english",
    "zero-shot-classification": "facebook/bart-large-mnli",
    "text-generation": "openai-community/gpt2",
    "fill-mask": "distilbert/distilroberta-base",
    "ner": "dbmdz/bert-large-cased-finetuned-conll03-english",
    "question-answering": "deepset/roberta-base-squad2",
    "summarization": "HuggingFaceTB/SmolLM-135M-Instruct",
    "translation": "HuggingFaceTB/SmolLM-135M-Instruct",
    "image-classification": "google/vit-base-patch16-224",
    "automatic-speech-recognition": "openai/whisper-tiny.en"
}

def process_gui_request(task_choice, custom_model, text_in, context_in, image_in, audio_in):
    model_to_use = custom_model if custom_model else TASK_MODELS[task_choice]
    
    media = image_in if task_choice == "image-classification" else audio_in if task_choice == "automatic-speech-recognition" else None
    
    return hf_manager.run_task(
        task=task_choice,
        model_name=model_to_use,
        text_input=text_in,
        media_input=media,
        extra_input=context_in
    )

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# Hugging Face Multi-Task Interface (Memory Efficient)")
    
    with gr.Row():
        with gr.Column(scale=1):
            task_dropdown = gr.Dropdown(choices=list(TASK_MODELS.keys()), value="sentiment-analysis", label="Select Task")
            model_input = gr.Textbox(placeholder="Leave blank for default model...", label="Custom Model Override (Optional)")
            
            gr.Markdown("### Input Data")
            text_box = gr.Textbox(lines=3, label="Main Text Input")
            context_box = gr.Textbox(lines=2, label="Secondary Text")
            
            gr.Markdown("### Media Inputs")
            image_box = gr.Image(type="filepath", label="Image Input")
            audio_box = gr.Audio(type="filepath", label="Audio Input")
            
            submit_btn = gr.Button("Run Model", variant="primary")
            
        with gr.Column(scale=1):
            output_box = gr.Textbox(lines=10, label="Output / Result")

    submit_btn.click(
        fn=process_gui_request,
        inputs=[task_dropdown, model_input, text_box, context_box, image_box, audio_box],
        outputs=output_box
    )

if __name__ == "__main__":
    demo.launch()