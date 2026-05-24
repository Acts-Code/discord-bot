import os
import json
from openai import OpenAI
from firebase import db
# ================= OPENROUTER =================
client = OpenAI(
    api_key=os.getenv("AI_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

MODEL = "meta-llama/llama-3.1-8b-instruct"

# ================= SETTINGS =================
MAX_CHAT_MEMORY = 15
MAX_FACTS = 25

# ================= CHAT MEMORY =================
def get_chat_memory(user_id):
    ref = db.collection("memory").document(str(user_id))
    doc = ref.get()

    if doc.exists:
        return doc.to_dict().get("messages", [])

    return []


def save_chat_memory(user_id, messages):
    db.collection("memory").document(str(user_id)).set({
        "messages": messages[-MAX_CHAT_MEMORY:]
    })


# ================= USER PROFILE =================
def get_user_profile(user_id):

    ref = db.collection("profiles").document(str(user_id))
    doc = ref.get()

    if doc.exists:
        return doc.to_dict()

    return {
        "name": None,
        "mood": "neutral",
        "facts": [],
        "habits": {},
        "relationship_level": 0,
        "summary": ""
    }


def update_user_profile(user_id, updates):

    db.collection("profiles").document(str(user_id)).set(
        updates,
        merge=True
    )


# ================= MEMORY AI EXTRACTION =================
def ai_extract_memory(prompt, profile):

    facts = profile.get("facts", [])
    habits = profile.get("habits", {})
    mood = profile.get("mood", "neutral")
    relationship = profile.get("relationship_level", 0)
    name = profile.get("name")

    text = prompt.lower()

    updates = {}

    # ===== NAME =====
    if "my name is" in text:
        try:
            extracted = text.split("my name is")[1].strip().split(" ")[0]
            updates["name"] = extracted.capitalize()
        except:
            pass

    # ===== MOOD =====
    mood_map = {
        "happy": ["happy", "great", "awesome", "good"],
        "sad": ["sad", "depressed", "down"],
        "angry": ["angry", "mad", "annoyed"],
        "tired": ["tired", "sleepy", "exhausted"]
    }

    for mood_name, keywords in mood_map.items():
        if any(word in text for word in keywords):
            mood = mood_name

    updates["mood"] = mood

    # ===== HABITS =====
    habit_keywords = {
        "gaming": ["game", "gaming", "valorant", "minecraft", "roblox"],
        "studying": ["study", "homework", "exam", "school"],
        "music": ["music", "song", "sing"],
        "coding": ["code", "python", "discord bot", "programming"]
    }

    for habit, keywords in habit_keywords.items():
        if any(word in text for word in keywords):
            habits[habit] = habits.get(habit, 0) + 1

    updates["habits"] = habits

    # ===== FACT STORAGE =====
    if (
        len(prompt) < 120
        and prompt not in facts
        and len(facts) < MAX_FACTS
    ):
        facts.append(prompt)

    updates["facts"] = facts

    # ===== RELATIONSHIP LEVEL =====
    relationship += 1
    updates["relationship_level"] = relationship

    # ===== MEMORY SUMMARY =====
    top_habit = "none"

    if habits:
        top_habit = max(habits, key=habits.get)

    summary = (
        f"User name: {updates.get('name', name)} | "
        f"Mood: {mood} | "
        f"Favorite activity: {top_habit} | "
        f"Relationship level: {relationship}"
    )

    updates["summary"] = summary

    return updates


# ================= SYSTEM PROMPT =================
def build_system_prompt(profile):

    return {
        "role": "system",
        "content": (
            "You are Actor, an advanced Discord AI assistant.\n"
            "You remember users long-term.\n"
            "You adapt to their personality, mood, and habits.\n"
            "Speak naturally and casually.\n"
            "Do NOT sound robotic.\n\n"

            f"User Profile Summary:\n"
            f"{profile.get('summary', '')}\n\n"

            f"Known Facts:\n"
            f"{profile.get('facts', [])}\n\n"

            f"Habits:\n"
            f"{profile.get('habits', {})}\n\n"

            f"Current Mood:\n"
            f"{profile.get('mood', 'neutral')}\n"
        )
    }


# ================= MAIN AI FUNCTION =================
async def ask_ai(user_id, prompt):

    try:

        # ===== LOAD DATA =====
        history = get_chat_memory(user_id)
        profile = get_user_profile(user_id)

        # ===== ADD USER MESSAGE =====
        history.append({
            "role": "user",
            "content": prompt
        })

        # ===== AI REQUEST =====
        messages = [
            build_system_prompt(profile),
            *history
        ]

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=500,
            temperature=0.8
        )

        reply = response.choices[0].message.content

        # ===== SAVE CHAT =====
        history.append({
            "role": "assistant",
            "content": reply
        })

        save_chat_memory(user_id, history)

        # ===== UPDATE LONG-TERM MEMORY =====
        updates = ai_extract_memory(prompt, profile)

        update_user_profile(user_id, updates)

        return reply

    except Exception as e:
        print("AI ERROR:", e)
        return "⚠️ Actor brain overloaded right now."
