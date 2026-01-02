# main.py
# Etherea — Full Demo Desktop-First CLI + Floating EI Avatar with TTS
# Revised to integrate Avatar GUI dynamically, advanced EI, full emotion range.

import asyncio
from datetime import datetime
import random
from typing import List, Dict
import sys
from PyQt5.QtWidgets import QApplication
from avatar import AvatarGUI

# -----------------------
# Mock / fallback AI backend (replace with etherea_ai.ask_ai if available)
# -----------------------
def ask_ai(prompt: str) -> str:
    """
    Fallback AI for demo purposes — returns dynamic, varied responses
    to avoid repetitive / robotic outputs.
    """
    responses = [
        "I see! Let's try approaching it from another angle.",
        "Interesting… what do you think would happen next?",
        "Hmm… I think focusing on one thing at a time could help.",
        "Absolutely! Keep going, you’re doing great.",
        "Let's take a moment to breathe and reflect.",
        "Curious question! Let's explore it together.",
        "I understand… let's adjust our approach slightly.",
        "Yes! That's a very good observation.",
        "Let's imagine a scenario to understand it better."
    ]
    return random.choice(responses)

# -----------------------
# Workspace with Avatars
# -----------------------
class Workspace:
    def __init__(self, avatars: List[AvatarGUI]):
        self.avatars = avatars
        self.history: List[Dict] = []
        self.user_mode = "guided"  # default mode
        self.user_state = {"focus": 0.6, "stress": 0.2}

    async def user_input(self, prompt: str):
        # store user input
        self.history.append({"role": "user", "text": prompt, "ts": datetime.utcnow().isoformat()})

        # call AI
        ai_text = await asyncio.to_thread(ask_ai, prompt)

        # store AI response
        self.history.append({"role": "AI", "text": ai_text, "ts": datetime.utcnow().isoformat()})

        # react avatars
        for avatar in self.avatars:
            avatar.react(ai_text, self.user_state)

        return ai_text

    def maybe_nudge(self):
        """Optional adaptive tips / nudges"""
        P_NUDGE = 0.2
        if random.random() < P_NUDGE:
            stress = self.user_state.get("stress",0)
            if stress>0.5:
                print("🧘 Suggestion: Take a short breathing break to reset focus.")
            else:
                print("💡 Tip: Ask the avatar for a motivational insight!")

# -----------------------
# Main interactive loop
# -----------------------
async def main_loop(ws: Workspace):
    print("🌌 Welcome to Etherea — Full Demo (CLI + Floating Avatar)")
    print("Type '/help' for commands. Press Ctrl+C to exit.\n")

    while True:
        try:
            user_prompt = input("You: ").strip()
            if not user_prompt:
                continue
            cmd = user_prompt.lower().split()[0]

            # exit
            if cmd in ("/exit","exit","quit","/quit"):
                print("🛑 Closing Etherea. See you next time!")
                break

            # help
            if cmd == "/help":
                print(
                    "Commands:\n"
                    "  /mode children|professional|guided - change experience mode\n"
                    "  /status    - show avatars & workspace status\n"
                    "  /history   - show conversation history\n"
                    "  /nudge     - trigger optional tips\n"
                    "  exit       - quit demo"
                )
                continue

            # mode switch
            if cmd == "/mode":
                parts = user_prompt.split()
                if len(parts)>=2 and parts[1] in {"children","professional","guided"}:
                    ws.user_mode = parts[1]
                    print(f"⚙️ Mode changed to {ws.user_mode}")
                else:
                    print("Usage: /mode children|professional|guided")
                continue

            # status
            if cmd == "/status":
                for a in ws.avatars:
                    print(f"Avatar {a.name}: Mood={a.mood}, Complex={a.complex_emotion}")
                continue

            # history
            if cmd == "/history":
                print("--- Conversation History ---")
                for h in ws.history[-10:]:
                    role = h['role']
                    text = h['text']
                    print(f"[{role}] {text}")
                print("----------------------------")
                continue

            # nudge
            if cmd == "/nudge":
                ws.maybe_nudge()
                continue

            # normal input
            ai_text = await ws.user_input(user_prompt)
            print(f"\n[AI Output]: {ai_text}\n")

        except KeyboardInterrupt:
            print("\n🛑 Interrupted. Closing Etherea...")
            break

# -----------------------
# Entry point
# -----------------------
def main():
    app = QApplication(sys.argv)

    # Create avatars
    avatars = [
        AvatarGUI(name="Aureth", image_path="avatar.gif"),
        AvatarGUI(name="Lumina", image_path="avatar.gif")
    ]

    ws = Workspace(avatars)

    loop = asyncio.get_event_loop()
    loop.create_task(main_loop(ws))
    sys.exit(app.exec_())

if __name__=="__main__":
    main()
