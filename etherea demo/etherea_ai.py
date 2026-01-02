# etherea_ai.py — OpenAI integration for Etherea 🚀

import os
from openai import OpenAI

# Initialize client using your environment variable
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_ai(prompt: str) -> str:
    """
    Send a prompt to OpenAI and get the response text.
    """
    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt
        )
        # Return plain text
        return response.output_text
    except Exception as e:
        return f"Error: {str(e)}"
