"""
Etherea Agent — Terminal Version
MIT Licensed
Run in terminal or Jupyter: python etherea_agent.py
"""

# ---- Install dependencies if not yet installed ----
# pip install openai langchain wikipedia-api tiktoken

from langchain.llms import OpenAI
from langchain.agents import initialize_agent, Tool
from langchain.utilities import WikipediaAPIWrapper
import os

# ---- Basic Config ----
# Set your OpenAI API key or any other LLM key here
os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"

# ---- Define Tools ----
wiki = WikipediaAPIWrapper()

tools = [
    Tool(
        name="Wikipedia",
        func=wiki.run,
        description="Search Wikipedia for information",
    ),
]

# ---- Initialize LLM and Agent ----
llm = OpenAI(temperature=0.7)
agent = initialize_agent(
    tools,
    llm,
    agent="zero-shot-react-description",
    verbose=True
)

# ---- Terminal Chat Loop ----
print("\n🌟 Etherea Terminal Agent — type 'quit' to exit 🌟\n")
while True:
    user_input = input("You: ")
    if user_input.lower() in ["quit", "exit"]:
        print("Etherea: Goodbye! 👋")
        break

    try:
        response = agent.run(user_input)
        print(f"Etherea: {response}\n")
    except Exception as e:
        print(f"Etherea encountered an error: {e}\n")
