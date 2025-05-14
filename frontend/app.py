import gradio as gr
import requests
import os

API_URL = "http://127.0.0.1:8002"

def generate_branding(camp_name, camp_desc, logo_file, brand_colors):
    print("Starting branding generation...")
    # 1. Create campaign
    camp_resp = requests.post(f"{API_URL}/campaigns/", json={"name": camp_name, "description": camp_desc})
    print("Campaign creation response:", camp_resp.status_code, camp_resp.text)
    if camp_resp.status_code != 200:
        return "Failed to create campaign.", "", "", "", "", "", None, "", None
    campaign_id = camp_resp.json()["id"]
    logo_path = None
    # 2. Upload logo if provided
    if logo_file is not None:
        mime_type = getattr(logo_file, 'mime_type', 'application/octet-stream')
        file_name = getattr(logo_file, "name", "uploaded_logo")
        file_bytes = None
        if hasattr(logo_file, "read"):
            file_bytes = logo_file.read()
            logo_file.seek(0)
        elif hasattr(logo_file, "value"):
            file_bytes = logo_file.value
        elif isinstance(logo_file, bytes):
            file_bytes = logo_file
        elif isinstance(logo_file, str) and os.path.exists(logo_file):
            with open(logo_file, "rb") as f:
                file_bytes = f.read()
        else:
            print("Invalid logo file type (unhandled type):", type(logo_file))
            return "Invalid logo file type.", "", "", "", "", "", None, "", None
        files = {"file": (file_name, file_bytes, mime_type)}
        upload_resp = requests.post(f"{API_URL}/campaigns/{campaign_id}/upload_logo", files=files)
        print("Logo upload response:", upload_resp.status_code, upload_resp.text)
        if upload_resp.status_code != 200:
            return f"Failed to upload logo: {upload_resp.text}", "", "", "", "", "", None, "", None
        # Get the saved logo path from the backend response
        logo_path = upload_resp.json().get("logo_url")
    # 3. Set brand colors if provided
    if brand_colors:
        brandkit_resp = requests.put(f"{API_URL}/campaigns/{campaign_id}/brand_kit", json={"brand_colors": brand_colors})
        print("Brand kit update response:", brandkit_resp.status_code, brandkit_resp.text)
    # 4. Generate content
    content_resp = requests.post(f"{API_URL}/campaigns/{campaign_id}/generate_content")
    print("Content generation response:", content_resp.status_code, content_resp.text)
    if content_resp.status_code != 200:
        return "Failed to generate content.", "", "", "", "", "", None, "", logo_path
    content = content_resp.json()
    # 5. Generate visual
    visual_resp = requests.post(f"{API_URL}/campaigns/{campaign_id}/generate_visual")
    print("Visual generation response:", visual_resp.status_code, visual_resp.text)
    if visual_resp.status_code == 200:
        visual_data = visual_resp.json()
        image_url = visual_data["image_url"]
        prompt = visual_data["prompt"]
    else:
        image_url = None
        prompt = ""
    print("Branding generation complete.")
    return "Branding generated!", content["social_post"], content["ad_copy"], content["email_campaign"], content["tagline"], content["product_description"], image_url, prompt, logo_path

def main():
    with gr.Blocks(theme=gr.themes.Base(), css="body { background: #18181b; color: #fff; }") as demo:
        gr.Markdown("# brandkit")
        gr.Markdown("Enter your campaign details, upload a logo, set brand colors, and generate all your branding content and visuals in one click!")
        camp_name = gr.Textbox(label="Campaign Name", placeholder="Enter campaign name")
        camp_desc = gr.Textbox(label="Campaign Description", placeholder="Enter campaign description")
        logo_file = gr.File(label="Upload Logo (optional)")
        brand_colors = gr.Textbox(label="Brand Colors (comma-separated hex codes, optional)")
        generate_btn = gr.Button("Generate Branding")
        gen_msg = gr.Markdown(visible=False)
        social_post = gr.Textbox(label="Social Post", interactive=False)
        ad_copy = gr.Textbox(label="Ad Copy", interactive=False)
        email_campaign = gr.Textbox(label="Email Campaign", interactive=False)
        tagline = gr.Textbox(label="Tagline", interactive=False)
        product_desc = gr.Textbox(label="Product Description", interactive=False)
        visual_image = gr.Image(label="Generated Visual", interactive=False)
        visual_prompt = gr.Textbox(label="Prompt Used", interactive=False)
        logo_display = gr.Image(label="Uploaded Logo", interactive=False)
        generate_btn.click(
            generate_branding,
            inputs=[camp_name, camp_desc, logo_file, brand_colors],
            outputs=[gen_msg, social_post, ad_copy, email_campaign, tagline, product_desc, visual_image, visual_prompt, logo_display]
        )
    demo.launch()

if __name__ == "__main__":
    main() 