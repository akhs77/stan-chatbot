import random

def get_random_greeting(user_name: str = "friend") -> str:
    greetings = [
        f"Hey, nice to see you again!",
        f"Hi! How's it going?",
        f"Hello! Glad to hear from you!",
        f"Yo! What's up?",
        f"Welcome back!",
        f"Good to see you!",
        f"How have you been?",
        f"What brings you here today?"
    ]
    return random.choice(greetings)

def enhance_prompt(base_prompt: str) -> str:
    """Add diversity hints to the LLM prompt."""
    diversity_hints = [
        "Respond naturally and conversationally. Vary your response style and don't use the same patterns repeatedly.",
        "Be friendly but not overly cheerful. Match the user's energy level and tone.",
        "Avoid ending every response the same way. Sometimes be casual, sometimes more thoughtful.",
        "Use emojis sparingly and only when they feel natural to the conversation context.",
        "Keep responses fresh and avoid repetitive endings or phrases."
    ]
    return f"{base_prompt}\nInstructions: {random.choice(diversity_hints)}"