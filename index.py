import google.generativeai as genai
import gradio as gr

def generate_prompt(have_formula, language):
    if have_formula == 'Yes':
        prompt = f"""
        You are an AI specialized in recognizing hand-written text and mathematical formulas.
        - Extract the handwritten text from the image, ensuring accurate recognition.
        - Correct any grammar mistakes in {language}.
        - Format **math expressions** using **LaTeX inside Markdown**.
        - **DO NOT replace LaTeX expressions with symbols** (e.g., use `\sqrt{{x}}` instead of `√x`).
        - Use:
            - **Inline math**: `$E = mc^2$`
            - **Block math**: `$$\int_0^1 x^2 dx$$`
            - **Fractions**: `\frac{{a}}{{b}}`
            - **Square roots**: `\sqrt{{x}}`
        - **Do NOT add hidden characters or extra spaces in LaTeX expressions.**
        - Return the result in a structured Markdown format, with no additional explanations or introductions.
        """
    elif have_formula == 'No':
        prompt = f"""
        You are an AI specialized in recognizing and processing handwritten text.
        - Extract the handwritten text from the image, ensuring accurate recognition.
        - Correct any grammar mistakes in {language}.
        - Format the output using **Markdown syntax** for better readability.
        - Return the result in a structured Markdown format, with no additional explanations or introductions.
        """
 
    return prompt

def recognize_formula(api_key, language, type_of_text, *images):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")
    prompt = generate_prompt(type_of_text, language)
    
    stream = model.generate_content(
        contents= [prompt] + [image for image in images if image],
        stream=True
    )
    response = ""
               
    for chunk in stream:
        if chunk.text:
            response +=chunk.text
        yield response

    response = response.replace("```", '').replace("```markdown", '').replace('markdown','')
    with open('result.md', "w", encoding="utf-8") as file:
        file.write(response)

with gr.Blocks(title="Handwriting Recognition") as view:
    gr.Markdown("# Handwriting Recognition Tool")
    gr.Markdown("Upload 5 images and provide your API key for processing.")
    with gr.Row():
        with gr.Column():
            # API Key input
            api_key_input = gr.Textbox(
                label="Gemini API key:",
                placeholder="Enter your API key here...",
                type="password"
            )

            language = gr.Dropdown(
                choices=["English", "Vietnamese"],
                label="Language"
            )

            have_formula = gr.Dropdown(
                choices=["Yes", "No"],
                label="Have formula?"
            )
            
            # Create image inputs programmatically
            NUM_IMAGES = 5
            with gr.Row():
                image_inputs = [
                    gr.Image(label=f"Image {i+1}", type="pil")
                    for i in range(NUM_IMAGES)
                ]
        
            # Submit button
            submit_btn = gr.Button("Submit", variant="primary")
        with gr.Column():
            # Output markdown
            gr.Markdown("Response")
            output_markdown = gr.Markdown(label="Response", container=True, show_label=True )
    # Set up the event handler with unpacked image inputs
    submit_btn.click(
        fn=recognize_formula,
        inputs=[api_key_input, language, have_formula, *image_inputs],
        outputs=output_markdown
    )
if __name__ == '__main__':  
    view.launch(share=True)