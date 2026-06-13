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

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 800
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL, json=payload, headers=HEADERS) as resp:
            data = await resp.json()

            print("OPENROUTER RESPONSE:", data)

            # ✅ HANDLE RATE LIMIT
            if "error" in data:
                err = data["error"]

                if err.get("code") == 429:
                    wait = err.get("metadata", {}).get("retry_after_seconds", 5)
                    return f"⏳ AI is busy. Try again in {wait}s."

                return f"❌ AI Error: {err.get('message')}"

            if "choices" not in data or not data["choices"]:
                return "❌ No response from AI."

            return data["choices"][0]["message"]["content"]
