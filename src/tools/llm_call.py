import os
import google.generativeai as genai


def call_llm(prompt: str, model: str = "gemini-2.5-flash") -> str:
    """
    Generic LLM call utility (Toolsmith role).
    Sends a prompt to Gemini and returns raw text.
    """

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set in environment")

    genai.configure(api_key=api_key)

    llm = genai.GenerativeModel(model)

    try:
       response = llm.generate_content(prompt, timeout=40) 
    except Exception as e:
        raise RuntimeError(f"Gemini API call failed: {e}") from e

    # Defensive check
    if not response or not hasattr(response, "text"):
        raise RuntimeError("Empty response from Gemini")

    return response.text