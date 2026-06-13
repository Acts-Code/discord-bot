import aiohttp
import os

OPENROUTER_API_KEY = os.getenv("AI_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


async def ask_ai(user_id: int, question: str):

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://discord.com",
        "X-Title": "Actor Bot"
    }

    payload = {
        "model": "meta-llama/llama-3.3-70b-instruct:free",
        "messages": [
            {"role": "system", "content": "You are Actor AI, a helpful Discord assistant."},
            {"role": "user", "content": question}
        ]
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(OPENROUTER_URL, json=payload, headers=headers) as resp:
            data = await resp.json()

            try:
                return data["choices"][0]["message"]["content"]
            except:
                return "⚠️ AI error: no response"
async def ask_code(user_id: int, prompt: str):

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://discord.com",
        "X-Title": "Actor Bot"
    }

    payload = {
        "model": "nvidia/nemotron-3-ultra-550b-a55b:free",
        "messages": [
            {
                "role": "system",
                "content": "You are a senior programmer. Output ONLY clean code. No explanation."
            },
            {"role": "user", "content": prompt}
        ]
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(OPENROUTER_URL, json=payload, headers=headers) as resp:
            data = await resp.json()

            try:
                return data["choices"][0]["message"]["content"]
            except:
                return "⚠️ Code AI error"
