import gradio as gr
import os
import time
from dotenv import load_dotenv
from app.rag_engine import generate_response
from app.voice_synthesis import text_to_speech

# Load local .env only when not in Hugging Face
if not os.getenv("HF_SPACE_ID"):
    load_dotenv()

def process_query(api_key, message, history=None):
    """
    Process user query with provided API key
    """
    if not api_key:
        return "Enter your OpenAI API key", None
    
    os.environ["OPENAI_API_KEY"] = api_key
    
    start_time = time.time()
    try:
        response, references = generate_response(message)
    except Exception as e:
        return f"Hata oluştu: {str(e)}", None
    
    try:
        audio_path = text_to_speech(response)
    except Exception as e:
        print(f"Error in voice generation: {str(e)}")
        audio_path = None
    
    proc_time = time.time() - start_time
    metrics = f"\n\n⏱️ Response time: {proc_time:.1f}s"
    
    full_response = f"{response}{references}{metrics}"
    
    return full_response, audio_path

# Hugging Face compatible Interface
hf_interface = gr.Interface(
    fn=lambda api_key, message: process_query(api_key, message),
    inputs=[
        gr.Textbox(label="Your OpenAI API Key", type="password", 
                  placeholder="sk-...", lines=1),
        gr.Textbox(label="Submit your question", placeholder="Ask your question about leadership...")
    ],
    outputs=[
        gr.Textbox(label="Response"),
        gr.Audio(label="Audio Response", autoplay=True)
    ],
    title="📝 Leadership Coach AI",
    description="""AI assistant that provides leadership coaching with expert knowledge.

**You must use your own OpenAI API key.**

[Click to get API key](https://platform.openai.com/api-keys)"""
)

with gr.Blocks() as chat_interface:
    gr.Markdown("# 📝 Leadership Coach AI")
    
    api_key = gr.Textbox(label="Your OpenAI API Key", type="password", 
                         placeholder="sk-...", lines=1)
    
    with gr.Row():
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(label="Chatbot")
            msg = gr.Textbox(label="Submit your question", placeholder="Ask your question about leadership...")
            submit_btn = gr.Button("Send")
        
        with gr.Column(scale=1):
            voice = gr.Audio(label="Audio Response", autoplay=True)
    
    def chat_respond(api_key, message, chat_history):
        response, audio = process_query(api_key, message)
        chat_history.append((message, response))
        return chat_history, audio, ""
    
    submit_btn.click(
        chat_respond,
        inputs=[api_key, msg, chatbot],
        outputs=[chatbot, voice, msg]
    )
    
    msg.submit(
        chat_respond,
        inputs=[api_key, msg, chatbot],
        outputs=[chatbot, voice, msg]
    )

if os.getenv("HF_SPACE_ID"):
    app = hf_interface
else:
    app = chat_interface

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860)