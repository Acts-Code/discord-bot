import os
import json
from openai import OpenAI
import firebase_admin
from firebase_admin import credentials

# ================= FIREBASE =================
firebase_json = json.loads(os.getenv("FIREBASE_CREDENTIALS"))

cred = credentials.Certificate(firebase_json)

# prevent double initialization crash on Railway
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

from firebase_admin import firestore
db = firestore.client()

# ================= OPENROUTER =================
client = OpenAI(
    api_key=os.getenv("AI_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

MODEL = "meta-llama/llama-3.1-8b-instruct"

# ================= MEMORY =================
def get_memory(user_id):
    ref = db.collection("memory").document(str(user_id))
    doc = ref.get()

    if doc.exists:
        return doc.to_dict().get("messages", [])
    return []

def save_memory(user_id, messages):
    db.collection("memory").document(str(user_id)).set({
        "messages": messages[-15:]
    })

# ================= AI FUNCTION =================
async def ask_ai(user_id, prompt):

    history = get_memory(user_id)
    history.append({"role": "user", "content": prompt})

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

        history.append({"role": "assistant", "content": reply})
        save_memory(user_id, history)

        return reply

    except Exception as e:
        print("AI ERROR:", e)
        return "⚠️ AI error. Please try again."
