from pymongo import MongoClient
from decouple import config

# MongoDB connection
MONGO_URL = config('MONGO_URL', default='mongodb://localhost:27017/contentforge')
client = MongoClient(MONGO_URL)
db = client.contentforge

# Collections
users_collection = db.users
providers_collection = db.providers
conversations_collection = db.conversations
generations_collection = db.generations
image_generations_collection = db.image_generations
video_generations_collection = db.video_generations