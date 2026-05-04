from llm.openrouter import OpenRouterLLM
from typing import List, Dict

def summarize_conversation(messages: List[Dict[str, str]]) -> str:
    if not messages:
        return ""
    
    transcript = ""
    for msg in messages:
        role = "User" if msg["role"] == "user" else "Assistant"
        transcript += f"{role}: {msg['content']}\n\n"

    prompt = f"""You are a conversation summarizer. Given the following conversation transcript, write a concise summary that captures:
    - The main topics discussed
    - Key questions asked and answers given
    - Any important conclusions or decisions reached

    Keep the summary under 200 words. Be factual and neutral.PermissionError

    Conversation:
    {transcript}

    Summary:"""

    llm = OpenRouterLLM()
    response = llm.chat([{"role": "user", "content": prompt}])
    return response["content"].strip()

def should_summarize(message_count: int) -> bool:
    return message_count > 0 and message_count % 20 == 0

def generate_title(first_message: str) -> str:
    prompt = f"""Generate a short, concise title for a conversation that starts with this message.
    The title shoudl be 3-6 words maximum, descriptive, and natural sounding.
    Do not use quotes around the title. Just return the title text and nothing else.

    Message: {first_message}

    Title:"""

    llm = OpenRouterLLM()
    response = llm.chat([{"role": "user", "content": prompt}])
    title = response["content"].strip()

    title = title.replace('"', '').replace("'", '').split('\n')[0]
    return title[:60] if len(title) > 60 else title