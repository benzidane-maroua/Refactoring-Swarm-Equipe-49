import ollama

def call_llm(prompt: str, model: str = "deepseek-coder:6.7b") -> str:
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

