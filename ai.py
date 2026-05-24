import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from openai import OpenAI

# ================= FIREBASE SAFE INIT =================
if not firebase_admin._apps:

    firebase_json = json.loads(os.getenv("FIREBASE_CREDENTIALS"))
    cred = credentials.Certificate(firebase_json)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ================= OPENROUTER AI =================
client = OpenAI(
    api_key=os.getenv("AI_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

MODEL = "meta-llama/llama-3.1-8b-instruct"

# ================= MEMORY SYSTEM =================
def get_memory(user_id):
    doc = db.collection("memory").document(str(user_id)).get()

    if doc.exists:
        return doc.to_dict().get("messages", [])

    return []

def save_memory(user_id, messages):
    db.collection("memory").document(str(user_id)).set({
        "messages": messages[-15:]
    })

# ================= MAIN AI FUNCTION =================
async def ask_ai(user_id, prompt):

    history = get_memory(user_id)

    history.append({
        "role": "user",
        "content": prompt
    })

    try:
        response = client.chat.completions.create(
            model=MODEL,
            max_tokens=300,
            messages=[
                {"role": "system", "content": "You are Actor, a helpful Discord bot AI."},
                *history
            ]
        )

        reply = response.choices[0].message.content

        history.append({
            "role": "assistant",
            "content": reply
        })

        save_memory(user_id, history)

        return reply

    except Exception as e:
        print("AI ERROR:", e)
        return "⚠️ AI error. Try again later."
