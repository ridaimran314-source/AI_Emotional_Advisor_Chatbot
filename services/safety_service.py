"""Crisis detection and safety response handling."""

CRISIS_KEYWORDS = [
    "suicide",
    "kill myself",
    "self harm",
    "self-harm",
    "hurt myself",
    "end my life",
    "harm someone",
    "want to die",
    "going to die",
    "cut myself",
    "overdose",
    "no reason to live",
]

CRISIS_RESPONSE = (
    "I'm really glad you reached out, and I want you to know you're not alone. "
    "What you're feeling sounds very serious, and you deserve immediate support "
    "from someone who can help right now.\n\n"
    "Please contact your local emergency services or a crisis helpline immediately. "
    "If you're in the United States, you can call or text 988 (Suicide & Crisis Lifeline). "
    "If you're elsewhere, search for your local emergency number or crisis line.\n\n"
    "If you can, please reach out to a trusted family member, friend, or neighbor right now. "
    "If you're near anything that could hurt you or someone else, please move to a safer place if you can.\n\n"
    "I'm here to listen, but this situation needs real human support as soon as possible. "
    "Will you try to contact someone you trust or call a helpline right now?"
)


def detect_crisis(message: str) -> bool:
    """Return True if the message contains crisis-related keywords."""
    normalized = message.lower().strip()
    return any(keyword in normalized for keyword in CRISIS_KEYWORDS)


def get_crisis_response() -> str:
    """Return the predefined safety response for crisis situations."""
    return CRISIS_RESPONSE
