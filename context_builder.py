# context_builder.py

def summarize_history(llm, chat_history: list) -> str:
    """Summarize earlier messages using the LLM."""
    if len(chat_history) <= 2:
        return ""

    older_turns = chat_history[:-2]
    summary_input = "\n".join([
        f"User: {h['user']}\nAssistant: {h['assistant']}"
        for h in older_turns
    ])

    prompt = f"""
Summarize the following conversation between a user and an assistant.
Only include key topics or decisions.

{summary_input}
"""
    try:
        summary = llm.invoke(prompt)
        return summary.strip()
    except Exception as e:
        return f"(⚠️ Could not summarize: {e})"


def format_recent_turns(chat_history: list, limit: int = 3) -> str:
    """Format recent chat history turns for inclusion in prompt."""
    recent_turns = chat_history[-limit:]
    return "\n\n".join([
        f"User: {h['user']}\nAssistant: {h['assistant']}"
        for h in recent_turns
    ])
