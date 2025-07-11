import os
from pymongo import MongoClient
from utils.config import MONGO_URL

# MongoDB client and database
client = MongoClient(MONGO_URL)
db = client.contentforge

# Collections
users_collection = db.users
providers_collection = db.providers
conversations_collection = db.conversations
generations_collection = db.generations
image_generations_collection = db.image_generations
video_generations_collection = db.video_generations
code_generations_collection = db.code_generations
social_media_generations_collection = db.social_media_generations