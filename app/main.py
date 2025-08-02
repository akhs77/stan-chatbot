from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Request schema
class UserMessage(BaseModel):
    user_id: str
    message: str

# Temporary in-memory store for testing
chat_history = {}

@app.post("/chat")
async def chat_endpoint(user_input: UserMessage):
    user_id = user_input.user_id
    message = user_input.message
    
    # Store conversation in temporary memory
    if user_id not in chat_history:
        chat_history[user_id] = []
    chat_history[user_id].append({"user": message, "bot": "Hello! I am your STAN chatbot."})
    
    return {"response": "Hello! I am your STAN chatbot.", "history": chat_history[user_id]}
