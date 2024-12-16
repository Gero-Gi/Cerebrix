
from  ..types import MessageRole

def format_message_for_token_count(message: str, type: MessageRole) -> str:
    """
    Formats a message for token counting by adding a prefix to the message based on the message role.
    """
    if type == MessageRole.HUMAN:
        return f"Human: {message}"
    elif type == MessageRole.AI:
        return f"AI: {message}"
    elif type == MessageRole.SUMMARIZER or type == MessageRole.SYSTEM:
        return f"System: {message}"
    else:
        return message