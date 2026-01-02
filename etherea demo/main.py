# main.py — Etherea Starter (Full Desktop-First Version) 🚀🖤

import os
import asyncio
from etherea_ai import ask_ai  # Our AI module
from datetime import datetime
import random

# -------- Workspace & Avatar Setup --------
class Avatar:
    def __init__(self, name):
        self.name = name
        self.mood = "neutral"  # moods: neutral, happy, focused, confused
        self.last_response = ""

    def react(self, message):
        """
        Simple mood reaction logic (can be expanded with EI signals)
        """
        moods = ["happy", "focused", "curious", "thinking"]
        self.mood = random.choice(moods)
        self.last_response = message
        print(f"[{self.name} | {self.mood}]: {message}")


class Workspace:
    """
    Core workspace: floating panels, adaptive UI, avatar interactions
    """
    def __init__(self):
        self.avatars = [Avatar("Aureth"), Avatar("Lumina")]
        self.history = []

    async def send_to_ai(self, prompt):
        """
        Sends prompt to AI and returns response
        """
        self.history.append({"user": prompt, "timestamp": datetime.now()})
        response = await asyncio.to_thread(ask_ai, prompt)
        self.history.append({"AI": response, "timestamp": datetime.now()})
        return response

    async def user_input(self, prompt):
        """
        Handles user input, AI response, and avatar reactions
        """
        response = await self.send_to_ai(prompt)

        # Send AI response to avatars for reaction
        for avatar in self.avatars:
            avatar.react(response)

        # Return AI text for logging or UI
        return response

# -------- Main Program Loop --------
async def main():
    ws = Workspace()
    print("🌌 Welcome to Etherea — The Living Workspace")
    print("Type 'exit' to close the session.\n")

    while True:
        user_prompt = input("You: ")
        if user_prompt.lower() in ["exit", "quit"]:
            print("🛑 Closing Etherea. See you next time!")
            break

        ai_text = await ws.user_input(user_prompt)
        print(f"\n[AI Output]: {ai_text}\n")

# -------- Entry Point --------
if __name__ == "__main__":
    asyncio.run(main())
