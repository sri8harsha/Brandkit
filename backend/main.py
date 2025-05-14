import os
import openai
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional, Dict
from dotenv import load_dotenv
import shutil

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# In-memory campaign store
campaigns: Dict[int, dict] = {}
campaign_counter = 1

class CampaignCreate(BaseModel):
    name: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    brand_colors: Optional[str] = None

class CampaignResponse(CampaignCreate):
    id: int

@app.post("/campaigns/", response_model=CampaignResponse)
def create_campaign(campaign: CampaignCreate):
    global campaign_counter
    campaign_id = campaign_counter
    campaign_counter += 1
    data = campaign.dict()
    data["id"] = campaign_id
    campaigns[campaign_id] = data
    return data

@app.get("/campaigns/{campaign_id}", response_model=CampaignResponse)
def get_campaign(campaign_id: int):
    if campaign_id not in campaigns:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaigns[campaign_id]

@app.put("/campaigns/{campaign_id}/brand_kit", response_model=CampaignResponse)
def update_brand_kit(campaign_id: int, brand_kit: CampaignCreate):
    if campaign_id not in campaigns:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if brand_kit.logo_url is not None:
        campaigns[campaign_id]["logo_url"] = brand_kit.logo_url
    if brand_kit.brand_colors is not None:
        campaigns[campaign_id]["brand_colors"] = brand_kit.brand_colors
    return campaigns[campaign_id]

@app.post("/campaigns/{campaign_id}/upload_logo", response_model=CampaignResponse)
def upload_logo(campaign_id: int, file: UploadFile = File(...)):
    if campaign_id not in campaigns:
        raise HTTPException(status_code=404, detail="Campaign not found")
    os.makedirs("static/logos", exist_ok=True)
    # Use only the filename, not the full path
    safe_filename = os.path.basename(file.filename)
    file_location = f"static/logos/campaign_{campaign_id}_{safe_filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    campaigns[campaign_id]["logo_url"] = file_location
    return campaigns[campaign_id]

@app.post("/campaigns/{campaign_id}/generate_content")
def generate_content(campaign_id: int):
    if campaign_id not in campaigns:
        raise HTTPException(status_code=404, detail="Campaign not found")
    camp = campaigns[campaign_id]
    name = camp["name"]
    description = camp.get("description", "")
    def ask_openai(prompt):
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a marketing expert."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    social_post = ask_openai(f"Write a catchy social media post for a campaign called '{name}'. Description: {description}")
    ad_copy = ask_openai(f"Write a short ad copy for a campaign called '{name}'. Description: {description}")
    email_campaign = ask_openai(f"Write a marketing email for a campaign called '{name}'. Description: {description}")
    tagline = ask_openai(f"Suggest a tagline for a campaign called '{name}'. Description: {description}")
    product_description = ask_openai(f"Write a product description for a campaign called '{name}'. Description: {description}")
    return {
        "social_post": social_post,
        "ad_copy": ad_copy,
        "email_campaign": email_campaign,
        "tagline": tagline,
        "product_description": product_description
    }

@app.post("/campaigns/{campaign_id}/generate_visual")
def generate_visual(campaign_id: int):
    if campaign_id not in campaigns:
        raise HTTPException(status_code=404, detail="Campaign not found")
    camp = campaigns[campaign_id]
    name = camp["name"]
    description = camp.get("description", "")
    prompt = f"Create a professional marketing visual for a campaign called '{name}'. Description: {description}. Use a clean, modern style."
    image_response = openai.images.generate(
        model="dall-e-3",
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    image_url = image_response.data[0].url
    return {"image_url": image_url, "prompt": prompt}

@app.get("/")
def root():
    return {"message": "AI Branding Tool Minimal Backend is running!"} 