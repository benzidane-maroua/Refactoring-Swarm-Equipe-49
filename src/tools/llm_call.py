# import os
# import google.generativeai as genai


# def call_llm(prompt: str, model: str = "gemini-2.0-flash") -> str:
#     """
   
#     Sends a prompt to Gemini and returns raw text.
#     """

#     api_key = os.getenv("GOOGLE_API_KEY")
#     if not api_key:
#         raise RuntimeError("GOOGLE_API_KEY not set in environment")

#     genai.configure(api_key=api_key)

#     llm = genai.GenerativeModel(model)

#     try:
#        response = llm.generate_content(prompt) 
#     except Exception as e:
#         raise RuntimeError(f"Gemini API call failed: {e}") from e

#     # Defensive check
#     if not response or not hasattr(response, "text"):
#         raise RuntimeError("Empty response from Gemini")



#     return response.text

import ollama

def call_llm(prompt: str, model: str = "deepseek-coder:6.7b") -> str:
    """
    Call a local LLM via Ollama.
    No internet. No API keys. No quota.
    """
    try:
        response = ollama.chat(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response["message"]["content"].strip()
    except Exception as e:
        raise RuntimeError(f"Local LLM call failed: {e}") from e

