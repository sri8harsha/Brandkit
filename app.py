import os
import gradio as gr
from openai import OpenAI
from PIL import Image
import io
import base64
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def process_campaign_description(description, brand_name, brand_colors, image_style):
    """
    Process the campaign description and generate marketing content and a DALL-E 3 image
    """
    try:
        # Create a prompt for GPT-4
        prompt = f"""
        Create a marketing campaign based on the following description:
        Description: {description}
        Brand Name: {brand_name}
        Brand Colors: {brand_colors}
        Image Style: {image_style}
        
        Please provide:
        1. A catchy headline
        2. A brief marketing copy
        3. Key visual elements to include
        """

        # Get response from GPT-4
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a marketing expert helping to create campaign content."},
                {"role": "user", "content": prompt}
            ]
        )

        # Extract the generated content
        generated_content = response.choices[0].message.content

        # Compose an image prompt for DALL-E 3
        image_prompt = (
            f"{description} for {brand_name}. Use brand colors: {brand_colors}. "
            f"Style: {image_style}. High quality, professional marketing visual."
        )

        # Call OpenAI DALL-E 3 API
        image_response = client.images.generate(
            model="dall-e-3",
            prompt=image_prompt,
            n=1,
            size="1024x1024"
        )
        image_url = image_response.data[0].url

        # Download the image and convert to PIL
        img_data = requests.get(image_url).content
        image = Image.open(io.BytesIO(img_data))

        return generated_content, image

    except Exception as e:
        return f"Error: {str(e)}", None

# Create the Gradio interface
with gr.Blocks(title="AI Branding Tool") as demo:
    gr.Markdown("# AI Branding Tool")
    gr.Markdown("Generate marketing content and visuals using AI")
    
    with gr.Row():
        with gr.Column():
            description = gr.Textbox(
                label="Campaign Description",
                placeholder="Describe your marketing campaign in detail...",
                lines=5
            )
            brand_name = gr.Textbox(
                label="Brand Name",
                placeholder="Enter your brand name"
            )
            brand_colors = gr.Textbox(
                label="Brand Colors",
                placeholder="Enter your brand colors (e.g., #FF0000, #00FF00)"
            )
            image_style = gr.Dropdown(
                label="Image Style",
                choices=["Modern", "Vintage", "Minimalist", "Bold", "Professional"],
                value="Modern"
            )
            generate_btn = gr.Button("Generate Campaign")
        
        with gr.Column():
            output_text = gr.Textbox(
                label="Generated Content",
                lines=10
            )
            output_image = gr.Image(
                label="Generated Visual",
                type="pil"
            )
    
    generate_btn.click(
        fn=process_campaign_description,
        inputs=[description, brand_name, brand_colors, image_style],
        outputs=[output_text, output_image]
    )

if __name__ == "__main__":
    demo.launch() 