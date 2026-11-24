# CourseCraft AI — YouTube Course Builder

A personal web app prototype that helps you turn a learning topic into a structured course outline and topic-specific YouTube searches.

## Requirements
- Python 3.10 or newer
- Internet connection for installing packages and opening YouTube search links

## Run on Windows

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL printed in the terminal (usually http://localhost:8501).

## Current capabilities
- Course topic, level, duration and goal form
- Starter module outline
- YouTube search links for each lesson topic
- Session-only lesson progress tracker

## Important
This is the first working frontend prototype. It does **not** yet use an AI model to generate the syllabus or the YouTube API to retrieve and rank individual videos. Those are the next development milestones.

Keep API keys in `.env`, never commit `.env` to GitHub.
