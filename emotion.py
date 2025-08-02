def detect_emotion(user_message: str) -> str:
    """Simple rule-based emotion detection."""
    msg = user_message.lower()
    
    if any(word in msg for word in ["sad", "depressed", "unhappy", "down"]):
        return "sad"
    elif any(word in msg for word in ["angry", "mad", "furious", "annoyed"]):
        return "angry"
    elif any(word in msg for word in ["happy", "great", "awesome", "excited"]):
        return "happy"
    elif any(word in msg for word in ["love", "thanks", "grateful"]):
        return "positive"
    else:
        return "neutral"
