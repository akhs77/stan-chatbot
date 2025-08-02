import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Connect to MongoDB
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["stan_chatbot_db"]  # database
users = db["users"]             # collection for user data

def get_user_profile(user_id):
    """Retrieve user profile or create one if not exists."""
    user = users.find_one({"user_id": user_id})
    if not user:
        user = {"user_id": user_id, "preferences": {}, "history": []}
        users.insert_one(user)
    return user

def save_chat(user_id, user_message, bot_response):
    """Save chat history to MongoDB."""
    users.update_one(
        {"user_id": user_id},
        {"$push": {"history": {"user": user_message, "bot": bot_response}}}
    )

def get_chat_history(user_id, limit=5):
    """Retrieve last N messages for context."""
    user = get_user_profile(user_id)
    return user.get("history", [])[-limit:]

def save_user_fact(user_id, key, value):
    """Save or update a user fact."""
    users.update_one(
        {"user_id": user_id},
        {"$set": {f"facts.{key}": value}},
        upsert=True
    )

def get_user_facts(user_id):
    """Retrieve stored facts for the user."""
    user = users.find_one({"user_id": user_id})
    return user.get("facts", {}) if user else {}

def handle_fact_contradiction(user_id, key, new_value):
    """Check for contradictions and respond accordingly."""
    facts = get_user_facts(user_id)
    if key in facts and facts[key] != new_value:
        # Contradiction detected
        return f"Earlier, you mentioned your {key} was {facts[key]}. Did it change to {new_value}?"
    else:
        # No contradiction
        save_user_fact(user_id, key, new_value)
        return None