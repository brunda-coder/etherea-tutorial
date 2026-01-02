# main.py
# Etherea — CLI desktop-first starter with EI-aware avatar behavior
# Revised: errors fixed and small refinements added.
# - safer emotion detection (word boundaries / regex)
# - conversation window (last N messages included in AI prompt)
# - echo toggle implemented (/echo on|off)
# - history trimming (max size) to avoid huge JSON
# - clearer nudge probability logic
# - robust handling if etherea_ai.ask_ai is async (detects and wraps)
# Copy-paste-ready. Run as before.

import os
import asyncio
import random
import json
import re
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

# -----------------------
# Config
# -----------------------
MAX_HISTORY = 400           # global cap for saved history records
CONTEXT_WINDOW = 6          # number of last role messages to include in AI prompt
HISTORY_FILENAME = "etherea_history.json"

# -----------------------
# Attempt to import AI backend (expected: ask_ai(prompt: str) -> str OR async def)
# If unavailable, provide a safe fallback so this file runs with no errors.
# -----------------------
_HAS_REMOTE_AI = False
_ASK_AI_IS_ASYNC = False

try:
    from etherea_ai import ask_ai  # type: ignore
    _HAS_REMOTE_AI = True
    # detect if ask_ai is coroutine function
    try:
        import inspect

        _ASK_AI_IS_ASYNC = inspect.iscoroutinefunction(ask_ai)
    except Exception:
        _ASK_AI_IS_ASYNC = False
except Exception:
    _HAS_REMOTE_AI = False

    def ask_ai(prompt: str) -> str:
        """
        Fallback local 'AI' — simple echo + small heuristics so the system behaves
        (Keeps the app running if etherea_ai isn't wired yet.)
        """
        prompt_clean = re.sub(r"\s+", " ", prompt).strip()
        if len(prompt_clean) == 0:
            return "Hmm — I didn't get anything. Try asking a clear question!"
        if "help" in prompt_clean.lower():
            return (
                "I'm running locally in fallback mode. Commands: /mode /status /save /help /echo. "
                "Ask me about tasks, or change mode for different behavior."
            )
        if any(k in prompt_clean.lower() for k in ("todo", "plan", "task", "steps")):
            return "Here's a short plan: 1) Define the task 2) Break it into steps 3) Execute the first step."
        # default echo with small transformation
        snippet = prompt_clean[:240]
        return f"[local-mock] I heard: \"{snippet}\" — replace with real etherea_ai.ask_ai for full behavior."

# -----------------------
# Utilities: improved text-based EI / sentiment detection (no ML)
# -----------------------
POSITIVE = {"great", "good", "awesome", "nice", "well done", "perfect", "love", "yay", "congrats", "congratulations"}
NEGATIVE = {"sad", "angry", "hate", "bad", "frustrat", "fail", "sorry", "problem", "error", "stuck"}
FOCUS = {"focus", "task", "concentrate", "deadline", "priority", "plan", "schedule", "todo", "work"}
QUESTION_WORDS = {"why", "how", "what", "when", "where", "who", "which"}


def word_in_text(wordset, text: str) -> bool:
    """Return True if any whole word from wordset appears in text (word boundary aware)."""
    for w in wordset:
        # escape and ensure word boundary
        pattern = r"\b" + re.escape(w) + r"\b"
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def detect_emotion_from_text(text: str) -> Dict[str, Any]:
    """
    Rule-based detection returning:
    - polarity: 'positive'|'negative'|'neutral'
    - intent: 'question'|'focus'|'comment'
    - score: float confidence 0..1
    """
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

    # question detection via leading question words or trailing question mark
    if re.match(r"^\s*(?:" + "|".join(re.escape(q) for q in QUESTION_WORDS) + r")\b", t, re.IGNORECASE) or t.endswith("?"):
        intent = "question"
        score = max(score, 0.6)
    elif word_in_text(FOCUS, t):
        intent = "focus"
        score = max(score, 0.6)

    # punctuation hint
    if t.endswith("!"):
        score = min(1.0, score + 0.05)
    if t.endswith("?"):
        score = min(1.0, score + 0.05)

    return {"polarity": polarity, "intent": intent, "score": round(score, 2)}


# -----------------------
# Avatar: reacts to AI messages using EI signals
# -----------------------
class Avatar:
    def __init__(self, name: str):
        self.name = name
        self.mood = "neutral"  # neutral, happy, focused, curious, thoughtful, concerned
        self.last_response = ""
        self.last_emotion = {}

    def react(self, ai_message: str, user_mode: str, user_state: Dict[str, float]) -> None:
        """
        Sets mood based on content and mode, prints a textual reaction.
        Hook points for TTS/animation can call these events.
        """
        emo = detect_emotion_from_text(ai_message)
        self.last_emotion = emo

        # base mood from detected polarity/intent
        if emo["polarity"] == "positive":
            base_mood = "happy"
        elif emo["intent"] == "focus":
            base_mood = "focused"
        elif emo["intent"] == "question":
            base_mood = "curious"
        elif emo["polarity"] == "negative":
            base_mood = "concerned"
        else:
            base_mood = "thoughtful"

        # adjust mood slightly depending on user_mode
        if user_mode == "children":
            mood_map = {
                "happy": "joyful",
                "focused": "interested",
                "curious": "playful",
                "concerned": "gentle",
                "thoughtful": "calm",
            }
            self.mood = mood_map.get(base_mood, base_mood)
        elif user_mode == "professional":
            mood_map = {
                "happy": "pleasant",
                "focused": "focused",
                "curious": "inquisitive",
                "concerned": "attentive",
                "thoughtful": "analytical",
            }
            self.mood = mood_map.get(base_mood, base_mood)
        else:
            self.mood = base_mood

        # small influence of user_state stress
        stress = float(user_state.get("stress", 0.0))
        if stress > 0.6 and self.mood in {"happy", "joyful", "pleasant"}:
            self.mood = "gentle"

        self.last_response = ai_message
        # textual output that frontends or TTS can consume
        print(f"[{self.name} | {self.mood}]: {ai_message}")


# -----------------------
# Workspace: holds avatars, history and orchestrates AI calls
# -----------------------
class Workspace:
    def __init__(self, avatars: List[Avatar]):
        self.avatars = avatars
        self.history: List[Dict[str, Any]] = []
        self.echo_system_prompt = False  # toggled by /echo on|off

    def _trim_history(self) -> None:
        """Trim history to MAX_HISTORY newest entries to avoid unbounded growth."""
        if len(self.history) > MAX_HISTORY:
            excess = len(self.history) - MAX_HISTORY
            self.history = self.history[excess:]

    def _build_context_snippet(self) -> str:
        """
        Build a short conversation window from history for inclusion in system prompt.
        Uses the last CONTEXT_WINDOW user/AI pairs (or as many as available).
        """
        if not self.history:
            return ""
        # take last CONTEXT_WINDOW*2 entries approx (user+AI)
        window = self.history[-CONTEXT_WINDOW * 2 :]
        snippets = []
        for entry in window:
            role = entry.get("role", "user")
            text = entry.get("text", "")
            ts = entry.get("ts", "")
            # keep it short
            text_short = text if len(text) <= 600 else text[-600:]
            snippets.append(f"{role.upper()} ({ts}): {text_short}")
        return "\n".join(snippets)

    async def send_to_ai(self, prompt: str, user_mode: str, user_state: Dict[str, float]) -> str:
        """
        Prepare context + prompt, call ask_ai (sync or async), store history, and return response.
        """
        mode_personas = {
            "children": (
                "You are a friendly, playful assistant for children. Use simple language, short sentences, and cheerful encouragement. Keep explanations fun and safe."
            ),
            "professional": (
                "You are a concise, practical assistant for professionals. Prioritize clarity, action steps, and brief summaries. Offer suggestions and keep emotional language measured."
            ),
            "guided": (
                "You are a helpful, friendly assistant for general users. Explain things clearly, offer gentle guidance, and ask clarifying questions when needed."
            ),
        }
        persona = mode_personas.get(user_mode, mode_personas["guided"])
        state_text = f"User state: focus={user_state.get('focus', 0.5):.2f}, stress={user_state.get('stress', 0.5):.2f}."
        system_prompt = f"{persona}\n{state_text}\nRespond to the user's message below:\n"

        # include context snippet
        context_snippet = self._build_context_snippet()
        if context_snippet:
            system_prompt += "\nRecent conversation:\n" + context_snippet + "\n\n"

        full_prompt = system_prompt + prompt

        # optionally echo system prompt for debugging
        if self.echo_system_prompt:
            print("---- SYSTEM PROMPT (echo) ----")
            print(system_prompt)
            print("---- END SYSTEM PROMPT ----")

        # store user message
        self.history.append({"role": "user", "text": prompt, "ts": datetime.utcnow().isoformat()})
        self._trim_history()

        # call AI, handle sync or async ask_ai
        try:
            if _HAS_REMOTE_AI and _ASK_AI_IS_ASYNC:
                ai_response = await ask_ai(full_prompt)  # type: ignore
            else:
                ai_response = await asyncio.to_thread(ask_ai, full_prompt)
        except Exception as e:
            ai_response = f"[error] AI backend failure: {e}. Check etherea_ai module."

        # store AI message
        self.history.append({"role": "AI", "text": ai_response, "ts": datetime.utcnow().isoformat()})
        self._trim_history()
        return ai_response

    async def user_input(self, prompt: str, user_mode: str, user_state: Dict[str, float]) -> str:
        """
        Full loop: call AI, route AI response to avatars, and optionally print nudges.
        """
        ai_text = await self.send_to_ai(prompt, user_mode, user_state)

        # Avatar reactions
        for avatar in self.avatars:
            avatar.react(ai_text, user_mode, user_state)

        # Nudges / adaptive suggestions
        self.maybe_nudge(user_mode, user_state)

        return ai_text

    def maybe_nudge(self, user_mode: str, user_state: Dict[str, float]) -> None:
        """
        Occasionally print a helpful suggestion based on mode or state.
        Probability controlled by P_NUDGE.
        """
        P_NUDGE = 0.22
        if random.random() >= P_NUDGE:
            return

        if user_mode == "professional":
            print("💡 Tip: You seem focused — consider a 25/5 Pomodoro cycle. Want me to set a reminder? (use /help)")
        elif user_mode == "children":
            print("🎨 Fun idea: Ask the avatar for a 1-minute drawing prompt!")
        else:
            stress = float(user_state.get("stress", 0.0))
            if stress > 0.6:
                print("🧘 Suggestion: You've been tense — a 60-second breathing break can help.")
            else:
                print("✨ Quick tip: You can type '/mode' to change experience modes anytime.")

    def save_history(self, filename: str = HISTORY_FILENAME) -> None:
        try:
            # ensure folder exists
            Path(filename).parent.mkdir(parents=True, exist_ok=True)
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
            print(f"✅ History saved to {filename} ({len(self.history)} records).")
        except Exception as e:
            print(f"❌ Failed to save history: {e}")

    def status(self) -> None:
        print("---- Workspace status ----")
        print(f"Avatars: {[a.name + ':' + a.mood for a in self.avatars]}")
        print(f"History entries: {len(self.history)}")
        print(f"Echo system prompt: {self.echo_system_prompt}")
        print("--------------------------")


# -----------------------
# CLI main loop (text-only)
# -----------------------
async def main():
    print("🌌 Welcome to Etherea — The Living Workspace (CLI edition)\n")
    print("Choose your experience mode (you can change it later):")
    print("1 - Playful / Children")
    print("2 - Professional / Focused")
    print("3 - Guided / Friendly (default)")
    mode_choice = input("Enter 1, 2 or 3 (press Enter for default 3): ").strip()
    modes = {"1": "children", "2": "professional", "3": "guided", "": "guided"}
    user_mode = modes.get(mode_choice, "guided")
    print(f"✅ You selected '{user_mode}' mode. (Change anytime with /mode)\n")

    # lightweight user state (focus, stress)
    user_state = {"focus": 0.6, "stress": 0.2}

    # create workspace with two avatars
    ws = Workspace(avatars=[Avatar("Aureth"), Avatar("Lumina")])

    print("Type '/help' for commands. Type 'exit' or 'quit' to close.\n")

    try:
        while True:
            user_prompt = input("You: ").strip()
            if not user_prompt:
                continue

            cmd = user_prompt.split()[0].lower()

            # Exit
            if cmd in ("/exit", "exit", "quit", "/quit"):
                print("🛑 Closing Etherea. See you next time!")
                break

            # Help
            if cmd == "/help":
                print(
                    "Commands:\n"
                    "  /mode <children|professional|guided> - change experience mode\n"
                    "  /status    - show workspace status\n"
                    "  /save      - save conversation history to etherea_history.json\n"
                    "  /echo on|off - toggle echo of internal system prompts (useful for debugging)\n"
                    "  /help      - show this help text\n"
                    "Or type any normal message to talk with the AI."
                )
                continue

            # Mode switching
            if cmd == "/mode":
                parts = user_prompt.split()
                if len(parts) >= 2:
                    choice = parts[1].lower()
                    if choice in {"children", "professional", "guided"}:
                        user_mode = choice
                        print(f"⚙️ Mode changed to '{user_mode}'.")
                    else:
                        print("Usage: /mode children|professional|guided")
                else:
                    print("Select mode: 1 children, 2 professional, 3 guided")
                    c = input("Enter 1|2|3: ").strip()
                    user_mode = modes.get(c, user_mode)
                    print(f"⚙️ Mode changed to '{user_mode}'.")
                continue

            # Status
            if cmd == "/status":
                ws.status()
                continue

            # Save history
            if cmd == "/save":
                ws.save_history()
                continue

            # Echo toggle
            if cmd == "/echo":
                parts = user_prompt.split()
                if len(parts) >= 2:
                    val = parts[1].lower()
                    if val in {"on", "true", "1"}:
                        ws.echo_system_prompt = True
                        print("🗣️ System prompt echo: ON")
                    elif val in {"off", "false", "0"}:
                        ws.echo_system_prompt = False
                        print("🗣️ System prompt echo: OFF")
                    else:
                        print("Usage: /echo on|off")
                else:
                    print("Usage: /echo on|off")
                continue

            # Normal conversational input
            ai_text = await ws.user_input(user_prompt, user_mode, user_state)
            # Print AI output clearly
            print(f"\n[AI Output]: {ai_text}\n")

    except KeyboardInterrupt:
        print("\n🛑 Interrupted. Saving session history and exiting...")
        ws.save_history()
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        ws.save_history()


if __name__ == "__main__":
    asyncio.run(main())
