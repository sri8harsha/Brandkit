# Brandkit

AI-powered branding tool. Instantly generate marketing content, visuals, and manage your brand kit.

## Features

- Campaign creation
- Logo upload and display
- AI-generated content (OpenAI GPT-4)
- AI-generated visuals (DALL·E 3)
- Simple Gradio UI

## Setup

1. Clone the repo:
   ```
   git clone https://github.com/YOUR_USERNAME/brandkit.git
   cd brandkit
   ```
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. **Create a `.env` file in the root directory with your own OpenAI API key:**
   ```
   OPENAI_API_KEY=your_openai_key_here
   ```
   - **Never share your API key or commit it to the repo.**
   - The `.env` file is included in `.gitignore` for your safety.
4. Start the backend:
   ```
   uvicorn backend.main:app --reload --port 8002
   ```
5. Start the frontend:
   ```
   python frontend/app.py
   ```

## Usage

- Open [http://localhost:7860](http://localhost:7860) in your browser.
- Enter campaign details, upload a logo, and generate your brand kit!

## Security

- Your OpenAI API key is required for AI features. **Do not share or commit your key.**
- Uploaded logos and temporary files are ignored by git for privacy and cleanliness. 
