import os
import re
import google.generativeai as genai
from flask import Flask, request, jsonify, render_template
from style import enhance_prompt
from dotenv import load_dotenv
from guard import needs_safe_response, get_safe_response
from persona import get_persona_context
from emotion import detect_emotion
from flask_cors import CORS
from memory import (
    get_user_profile, save_chat, get_chat_history,
    handle_fact_contradiction, save_user_fact, get_user_facts
)

# ----------- FACT EXTRACTION -----------
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

# ----------- CONFIGURATION -----------
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

app = Flask(__name__)
CORS(app)
model = genai.GenerativeModel('gemini-1.5-flash')

# ----------- CHAT ENDPOINT -----------
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_id = data.get('user_id')
    user_message = data.get('message')

    if not user_id or not user_message:
        return jsonify({"error": "user_id and message required"}), 400

    # ✅ Hallucination Guard
    if needs_safe_response(user_message):
        bot_response = get_safe_response()
        save_chat(user_id, user_message, bot_response)
        return jsonify({
            "user_id": user_id,
            "emotion_detected": "neutral",
            "response": bot_response,
            "context_used": []
        })

    # ✅ Fact Extraction & Contradiction Handling
    key, value = extract_fact(user_message)
    if key and value:
        contradiction_msg = handle_fact_contradiction(user_id, key, value)
        if contradiction_msg:
            # Ask user to confirm the change
            save_chat(user_id, user_message, contradiction_msg)
            return jsonify({
                "user_id": user_id,
                "response": contradiction_msg,
                "context_used": get_chat_history(user_id)
            })
        else:
            # Save new fact and acknowledge update
            save_user_fact(user_id, key, value)
            update_msg = f"Got it! I'll remember your {key} is now {value}."
            save_chat(user_id, user_message, update_msg)

    # ✅ Emotion Detection
    emotion = detect_emotion(user_message)

    # ✅ Retrieve Context
    history = get_chat_history(user_id)
    context_text = "\n".join([f"User: {h['user']}\nBot: {h['bot']}" for h in history])

    # ✅ Persona Context
    persona_context = get_persona_context()

    # ✅ Build Final Prompt
    base_prompt = f"{persona_context}\nThe user seems {emotion}.\n{context_text}\nUser: {user_message}\nBot:"
    final_prompt = enhance_prompt(base_prompt) or base_prompt
    print("DEBUG FINAL PROMPT:", final_prompt)

    # ✅ Ensure Prompt is not Empty
    if not final_prompt.strip():
        final_prompt = user_message

    try:
        # ✅ Render-Safe Gemini Call
        response = model.generate_content([{"role": "user", "parts": [final_prompt]}])
        bot_response = response.text

        # ✅ Save Chat to DB
        save_chat(user_id, user_message, bot_response)

        return jsonify({
            "user_id": user_id,
            "emotion_detected": emotion,
            "response": bot_response,
            "context_used": history
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ----------- ROUTES -----------
@app.route('/')
def health():
    return "Chatbot server with memory is running."

@app.route('/chat-ui')
def chat_ui():
    return render_template('index.html')

# ----------- MAIN -----------
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
