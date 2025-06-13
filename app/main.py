import time
import gradio as gr
from rag_engine import generate_response
from voice_synthesis import text_to_speech


def respond(message, chat_history):
    """
        Process user question and return text and audio response
    """
    start_time = time.time()
    response, references = generate_response(message)
    
    audio_path = text_to_speech(response) 
    
    proc_time = time.time() - start_time
    metrics = f"\n\n⏱️ Response time: {proc_time:.1f}s"
    
    full_response = f"{response}{references}{metrics}"
    
    chat_history.append((message, full_response))
    
    return chat_history, gr.Audio(audio_path) if audio_path else None

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 📝 Leadership Coach AI")
    
    with gr.Row():
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(height=500)
            msg = gr.Textbox(label="Submit your question", placeholder="Ask your question about leadership...")
            submit_btn = gr.Button("Send")
        
        with gr.Column(scale=1):
            voice = gr.Audio(autoplay=True, interactive=False, label="Audio Response")
    
    submit_btn.click(
        fn=respond,
        inputs=[msg, chatbot],
        outputs=[chatbot, voice]
    )
    
    msg.submit(
        fn=respond,
        inputs=[msg, chatbot],
        outputs=[chatbot, voice]
    )

if __name__ == "__main__":
     demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True  # Enables temporary public sharing
    )
   #demo.launch(server_name="0.0.0.0", server_port=7860)
