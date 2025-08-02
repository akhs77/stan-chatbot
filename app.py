import os
import re
import google.generativeai as genai
from flask import Flask, request, jsonify
from style import enhance_prompt
from dotenv import load_dotenv
from guard import needs_safe_response, get_safe_response
from persona import get_persona_context
# from flask import send_from_directory
from flask import render_template
from emotion import detect_emotion
from memory import (
    get_user_profile, save_chat, get_chat_history,
    handle_fact_contradiction, save_user_fact, get_user_facts
)

def extract_fact(user_message):
    """Extract simple facts like name, location, favorite color."""
    patterns = {
        "name": r"my name is (\w+)",
        "location": r"i live in (\w+)",
        "favorite_color": r"my favorite color is (\w+)"
    }
    msg = user_message.lower()
    for key, pattern in patterns.items():
        match = re.search(pattern, msg)
        if match:
            return key, match.group(1)
    return None, None

# Load env variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize Flask
app = Flask(__name__)
model = genai.GenerativeModel('gemini-1.5-flash')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_id = data.get('user_id')
    user_message = data.get('message')

    if not user_id or not user_message:
        return jsonify({"error": "user_id and message required"}), 400
    
    # Hallucination check
    if needs_safe_response(user_message):
        bot_response = get_safe_response()
        save_chat(user_id, user_message, bot_response)
        return jsonify({
            "user_id": user_id,
            "emotion_detected": "neutral",
            "response": bot_response,
            "context_used": []
        })
    
    key, value = extract_fact(user_message)
    if key and value:
        contradiction_msg = handle_fact_contradiction(user_id, key, value)
        if contradiction_msg:
            save_chat(user_id, user_message, contradiction_msg)
            return jsonify({
                "user_id": user_id,
                "response": contradiction_msg,
                "context_used": get_chat_history(user_id)
            })
        else:
            save_user_fact(user_id, key, value)
            
     # Detect user emotion
    emotion = detect_emotion(user_message)

    # Retrieve previous chats for context
    history = get_chat_history(user_id)
    context_text = "\n".join([f"User: {h['user']}\nBot: {h['bot']}" for h in history])

     # Persona context
    persona_context = get_persona_context()

    # Construct prompt with context
    # prompt = f"{context_text}\nUser: {user_message}\nBot:"
    # Modify system prompt with emotional context
    # emotion_context = f"The user seems {emotion}. Respond empathetically if needed."

    # Build final prompt
    base_prompt = f"{persona_context}\nThe user seems {emotion}.\n{context_text}\nUser: {user_message}\nBot:"
    final_prompt = enhance_prompt(base_prompt)
    
    try:
        response = model.generate_content(final_prompt)
        bot_response = response.text

        # Save chat to DB
        save_chat(user_id, user_message, bot_response)

        return jsonify({
            "user_id": user_id,
            "emotion_detected": emotion,
            # "persona_used": persona_context,
            "response": bot_response,
            "context_used": history
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def health():
    return "Chatbot server with memory is running."

@app.route('/chat-ui')
def chat_ui():
    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

# Ensure the app runs with the correct host and portgit