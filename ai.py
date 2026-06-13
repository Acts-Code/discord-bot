import os
import aiohttp

OPENROUTER_API_KEY = os.getenv("AI_API_KEY")

API_URL = "https://openrouter.ai/api/v1/chat/completions"


HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
}


async def ask_ai(user_id: int, prompt: str):
    return await _call_model(
        model="meta-llama/llama-3.3-70b-instruct:free",
        prompt=prompt
    )


async def ask_code(user_id: int, prompt: str):
    return await _call_model(
        model="nvidia/nemotron-3-ultra-550b-a55b:free",
        prompt=prompt
    )


async def _call_model(model: str, prompt: str):
    if not OPENROUTER_API_KEY:
        return "❌ Missing OPENROUTER_API_KEY"

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant. Keep responses clear and useful."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 800
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(API_URL, json=payload, headers=HEADERS) as resp:
                data = await resp.json()

                # Debug print (VERY IMPORTANT)
                print("OPENROUTER RESPONSE:", data)

                return data["choices"][0]["message"]["content"]

    except Exception as e:
        print("OPENROUTER ERROR:", e)
        return f"⚠️ API error: {e}"
