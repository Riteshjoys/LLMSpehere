import os
from decouple import config

# Database
MONGO_URL = config('MONGO_URL', default='mongodb://localhost:27017')

# API Keys
OPENAI_API_KEY = config('OPENAI_API_KEY', default='')
FAL_API_KEY = config('FAL_API_KEY', default='')
LUMA_API_KEY = config('LUMA_API_KEY', default='')
PIKA_API_KEY = config('PIKA_API_KEY', default='')
GROQ_API_KEY = config('GROQ_API_KEY', default='')
ELEVENLABS_API_KEY = config('ELEVENLABS_API_KEY', default='')
ANTHROPIC_API_KEY = config('ANTHROPIC_API_KEY', default='')
GOOGLE_API_KEY = config('GOOGLE_API_KEY', default='')
STABILITY_API_KEY = config('STABILITY_API_KEY', default='')

# Set fal.ai API key
if FAL_API_KEY:
    os.environ["FAL_KEY"] = FAL_API_KEY