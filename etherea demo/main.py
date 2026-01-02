# main.py
# Etherea — CLI desktop-first starter with EI-aware avatar behavior
# Refined for OpenAI integration and full advanced demo
import os
import asyncio
import random
import json
import re
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

from etherea_demo.etherea_ai import ask_ai  # keep key only inside this file

# -----------------------
# Config
# -----------------------
MAX_HISTORY = 400
CONTEXT_WINDOW = 6
HISTORY_FILENAME = "etherea_history.json"

# -----------------------
# Emotion / EI utilities
# -----------------------
POSITIVE = {"great", "good", "awesome", "nice", "well done", "perfect", "love", "yay", "congrats", "congratulations"}
NEGATIVE = {"sad", "angry", "hate", "bad", "frustrat", "fail", "sorry", "problem", "error", "stuck"}
FOCUS = {"focus", "task", "concentrate", "deadline", "priority", "plan", "schedule", "todo", "work"}
QUESTION_WORDS = {"why", "how", "what", "when", "where", "who", "which"}

def word_in_text(wordset, text: str) -> bool:
    for w in wordset:
        pattern = r"\b" + re.escape(w) + r"\b"
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

def detect_emotion_from_text(text: str) -> Dict[str, Any]:
    t = text.strip()
    score = 0.5
    polarity = "neutral"
    intent = "comment"
    if word_in_text(POSITIVE, t):
        polarity = "positive"
        score = 0.8
    elif word_in_text(NEGATIVE, t):
        polarity = "negative"
        score = 0.8
    if re.match(r"^\s*(?:" + "|".join(re.escape(q) for q in QUESTION_WORDS) + r")\b", t, re.IGNORECASE) or t.endswith("?"):
        intent = "question"
        score = max(score, 0.6)
    elif word_in_text(FOCUS, t):
        intent = "focus"
        score = max(score, 0.6)
    if t.endswith("!") or t.endswith("?"):
        score = min(1.0, score + 0.05)
    return {"polarity": polarity, "intent": intent, "score": round(score, 2)}

# -----------------------
# Avatar class
# -----------------------
class Avatar:
    def __init__(self, name: str):
        self.name = name
        self.mood = "neutral"
        self.last_response = ""
        self.last_emotion = {}

    def react(self, ai_message: str, user_mode: str, user_state: Dict[str, float]):
        emo = detect_emotion_from_text(ai_message)
        self.last_emotion = emo
        # define full emotional range dynamically
        moods = ["neutral","happy","joyful","pleasant","focused","interested","curious","playful","thoughtful","analytical","concerned","gentle","supportive","encouraging","motivated"]
        base_mood = random.choice(moods)
        self.mood = base_mood
        self.last_response = ai_message
        print(f"[{self.name} | {self.mood}]: {ai_message}")

# -----------------------
# Workspace class
# -----------------------
class Workspace:
    def __init__(self, avatars: List[Avatar]):
        self.avatars = avatars
        self.history: List[Dict[str, Any]] = []
        self.echo_system_prompt = False

    def _trim_history(self):
        if len(self.history) > MAX_HISTORY:
            self.history = self.history[-MAX_HISTORY:]

    def _build_context_snippet(self):
        if not self.history:
            return ""
        window = self.history[-CONTEXT_WINDOW*2:]
        snippets = []
        for entry in window:
            role = entry.get("role", "user")
            text = entry.get("text", "")
            ts = entry.get("ts", "")
            text_short = text if len(text) <= 600 else text[-600:]
            snippets.append(f"{role.upper()} ({ts}): {text_short}")
        return "\n".join(snippets)

    async def send_to_ai(self, prompt: str, user_mode: str, user_state: Dict[str, float]) -> str:
        persona_map = {
            "children": "Friendly playful assistant. Use simple language and short sentences.",
            "professional": "Concise practical assistant. Clear, brief, actionable.",
            "guided": "Helpful friendly assistant. Explain clearly and offer gentle guidance."
        }
        persona = persona_map.get(user_mode, persona_map["guided"])
        state_text = f"User state: focus={user_state.get('focus',0.5):.2f}, stress={user_state.get('stress',0.5):.2f}."
        system_prompt = f"{persona}\n{state_text}\nRespond to user below:\n"
        context_snippet = self._build_context_snippet()
        if context_snippet:
            system_prompt += "\nRecent conversation:\n" + context_snippet + "\n\n"
        full_prompt = system_prompt + prompt
        if self.echo_system_prompt:
            print("---- SYSTEM PROMPT ----")
            print(system_prompt)
            print("-----------------------")
        self.history.append({"role":"user","text":prompt,"ts":datetime.utcnow().isoformat()})
        self._trim_history()
        try:
            ai_response = await asyncio.to_thread(ask_ai, full_prompt)
        except Exception as e:
            ai_response = f"[error] AI failure: {e}"
        self.history.append({"role":"AI","text":ai_response,"ts":datetime.utcnow().isoformat()})
        self._trim_history()
        return ai_response

    async def user_input(self, prompt: str, user_mode: str, user_state: Dict[str, float]) -> str:
        ai_text = await self.send_to_ai(prompt, user_mode, user_state)
        for avatar in self.avatars:
            avatar.react(ai_text, user_mode, user_state)
        self.maybe_nudge(user_mode, user_state)
        return ai_text

    def maybe_nudge(self, user_mode: str, user_state: Dict[str,float]):
        if random.random() < 0.22:
            if user_mode=="professional":
                print("💡 Tip: Consider a 25/5 focus cycle.")
            elif user_mode=="children":
                print("🎨 Fun idea: Ask avatar for a 1-minute drawing prompt!")
            else:
                stress = float(user_state.get("stress",0.0))
                if stress>0.6:
                    print("🧘 Suggestion: Quick breathing break.")
                else:
                    print("✨ Tip: Type '/mode' to change experience mode anytime.")

    def save_history(self, filename: str = HISTORY_FILENAME):
        try:
            Path(filename).parent.mkdir(parents=True, exist_ok=True)
            with open(filename,"w",encoding="utf-8") as f:
                json.dump(self.history,f,indent=2,ensure_ascii=False)
            print(f"✅ History saved: {filename} ({len(self.history)} records)")
        except Exception as e:
            print(f"❌ Save failed: {e}")

    def status(self):
        print("---- Workspace status ----")
        print(f"Avatars: {[a.name+':'+a.mood for a in self.avatars]}")
        print(f"History entries: {len(self.history)}")
        print(f"Echo system prompt: {self.echo_system_prompt}")
        print("--------------------------")

# -----------------------
# CLI main loop
# -----------------------
async def main():
    print("🌌 Welcome to Etherea — The Living Workspace (CLI)\n")
    modes = {"1":"children","2":"professional","3":"guided","":"guided"}
    print("Choose experience mode: 1-Children, 2-Professional, 3-Guided(default)")
    mode_choice = input("Enter choice: ").strip()
    user_mode = modes.get(mode_choice,"guided")
    print(f"✅ Mode: {user_mode}\n")
    user_state = {"focus":0.6,"stress":0.2}
    ws = Workspace([Avatar("Aureth"),Avatar("Lumina")])
    print("Type '/help' for commands. Type 'exit' or 'quit' to close.\n")
    try:
        while True:
            user_prompt = input("You: ").strip()
            if not user_prompt:
                continue
            cmd = user_prompt.split()[0].lower()
            if cmd in ("/exit","exit","quit","/quit"):
                print("🛑 Closing Etherea. Bye!")
                break
            if cmd=="/help":
                print("Commands:\n  /mode <children|professional|guided>\n  /status\n  /save\n  /echo on|off\n  /help\nType any normal message to talk with AI.")
                continue
            if cmd=="/mode":
                parts=user_prompt.split()
                if len(parts)>=2 and parts[1].lower() in {"children","professional","guided"}:
                    user_mode=parts[1].lower()
                    print(f"⚙️ Mode changed to '{user_mode}'.")
                else:
                    print("Usage: /mode children|professional|guided")
                continue
            if cmd=="/status":
                ws.status()
                continue
            if cmd=="/save":
                ws.save_history()
                continue
            if cmd=="/echo":
                parts=user_prompt.split()
                if len(parts)>=2 and parts[1].lower() in {"on","off"}:
                    ws.echo_system_prompt = (parts[1].lower()=="on")
                    print(f"🗣️ System prompt echo: {parts[1].lower()}")
                else:
                    print("Usage: /echo on|off")
                continue
            ai_text = await ws.user_input(user_prompt,user_mode,user_state)
            print(f"\n[AI Output]: {ai_text}\n")
    except KeyboardInterrupt:
        print("\n🛑 Interrupted. Saving session history...")
        ws.save_history()
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        ws.save_history()

if __name__=="__main__":
    asyncio.run(main())
