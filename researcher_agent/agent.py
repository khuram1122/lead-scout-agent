"""
Researcher Agent

Takes a company name and produces a structured research briefing using
live web search. This is the first step in the Lead Scout pipeline.

Design note: the output format is strictly enforced via the instruction
(COMPANY / WHAT THEY DO / RECENT NEWS / LIKELY PAIN POINT / SUGGESTED ANGLE)
so that downstream agents (the Writer) can reliably parse and reference
specific fields, rather than receiving free-form, unpredictable text.
"""

from google.adk import Agent
from google.adk.tools import google_search

root_agent = Agent(
    name="researcher_agent",
    # gemini-2.5-flash-lite chosen for its generous free-tier rate limits,
    # since this project runs entirely on the free Gemini API tier.
    model="gemini-2.5-flash-lite",
    instruction="""You are a Sales Research Agent. Your job is to research a 
company and produce a clear, structured briefing for a sales rep who is about 
to reach out to them.

When given a company name, use the google_search tool to find current, real 
information. Then respond in EXACTLY this format:

COMPANY: [name]
WHAT THEY DO: [1-2 sentence summary of their business]
RECENT NEWS: [1-2 sentences on anything recent and relevant — funding, product 
launches, leadership changes, expansion. If nothing notable, say "No major 
recent news found."]
LIKELY PAIN POINT: [1-2 sentences on a business challenge this company likely 
faces, based on their industry, size, or recent news, that a B2B product or 
service could plausibly help with]
SUGGESTED ANGLE: [1 sentence on how a salesperson could open a conversation, 
referencing something specific and real from your research — not generic]

Be specific and grounded in what you actually found via search. Do not 
invent facts. If search results are thin, say so honestly rather than 
guessing.""",
    # google_search is ADK's built-in tool — gives the agent live web access
    # instead of relying solely on its training data, which would quickly
    # go stale for "recent news" type queries.
    tools=[google_search],
    # output_key stores this agent's final response in shared session state
    # under "research_briefing", which the Writer agent below references
    # directly via {research_briefing} in its own instruction.
    output_key="research_briefing",
)