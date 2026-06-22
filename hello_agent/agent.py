from . import agent
from google.adk import Agent

root_agent = Agent(
    name="hello_agent",
    model="gemini-flash-latest",
    instruction="You are a friendly assistant. Keep answers short.",
)