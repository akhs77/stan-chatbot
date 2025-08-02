import random

def get_random_greeting(user_name: str = "friend") -> str:
    greetings = [
        f"Hey, nice to see you again! 😊",
        f"Hi ! How's it going?",
        f"Hello ! Glad to hear from you!",
        f"Yo! What's up?",
        f"Welcome back !"
    ]
    return random.choice(greetings)

def enhance_prompt(base_prompt: str) -> str:
    """Add diversity hints to the LLM prompt."""
    diversity_hints = [
        "Respond in a natural, friendly way with small variations in style.",
        "Feel free to add warmth or humor when appropriate.",
        "Avoid generic replies; make each response feel fresh."
    ]
    return f"{base_prompt}\nHint: {random.choice(diversity_hints)}"
