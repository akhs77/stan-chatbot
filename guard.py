def needs_safe_response(user_message: str) -> bool:
    """Check if the user's question might cause hallucination."""
    triggers = [
        "did you see me", "what do i look like", "remember last week",
        "can you read my mind", "did you watch", "what was the secret"
    ]
    msg = user_message.lower()
    return any(trigger in msg for trigger in triggers)

def get_safe_response():
    """Return a grounded, safe response."""
    safe_responses = [
        "Hmm, I wish I could, but I don’t have the ability to see or remember events outside our chat!",
        "I only know what you share with me here, but I’m happy to imagine things together! 😄",
        "I don’t have that information, but tell me more and I’ll join the fun."
    ]
    import random
    return random.choice(safe_responses)
