# RacharlaGPT AI Movie Studio

New Python/Streamlit implementation built from zero. Old projects are NOT used as implementation sources; only their requested analytics/monetization configuration was collected.

## Features
- Idea/script → editable storyboard → real MP4
- Gemini image generation and photo transformation via REST API
- Poster maker
- Character/reference images
- Auto Fit / Fill-Crop / Stretch / X-Y / rotation
- Music upload or generated music
- Captions
- Video → MP3 and video trim
- Feature carousel and RacharlaGPT product links
- Privacy/terms/AI disclosure/advertising information cards
- Optional AdSense and Monetag integration switches

## Run
1. Install Python dependencies.
2. Ensure FFmpeg is installed and available as `ffmpeg`.
3. Copy `.env.example` to your deployment secrets/environment.
4. Set `GEMINI_API_KEY` only if you want Gemini generation.
5. Run `streamlit run app.py`.

## Monetization
Monetization is disabled by default. The exact legacy Monetag references are in `MONETAG_CONFIG_REFERENCE.txt`. Review current provider rules before enabling. AdSense placement must remain clearly distinguishable from navigation and interactive controls.
