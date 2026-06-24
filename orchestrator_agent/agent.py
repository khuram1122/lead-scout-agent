"""
Orchestrator Agent

This is the heart of Lead Scout: a fixed three-step pipeline that takes a
single company name and produces a complete, logged lead record.

Design decision: SequentialAgent (rather than a single agent with multiple
tools, or a more dynamic multi-agent routing setup) was chosen because the
three steps — research, write, save — always happen in the same fixed
order, with each step strictly depending on the previous one's output.
There's no need for dynamic routing or agent-to-agent negotiation here,
so the simplest correct tool is a fixed sequence.

Data handoff mechanism: each sub-agent below uses `output_key` to write its
final response into shared session state. The next agent in the sequence
references that value directly in its own instruction text using
{placeholder} syntax (e.g. {research_briefing}). ADK resolves these
placeholders automatically before calling the model, so no manual
Python glue code is needed to pass data between agents.
"""

from google.adk import Agent
from google.adk.agents import SequentialAgent
from google.adk.tools import google_search
from mcp_server.server import save_lead_record

# --- Step 1: Researcher ---
# Researches the company via live web search and produces a structured
# briefing. See researcher_agent/agent.py for the standalone version with
# full comments on the output format design.
researcher = Agent(
    name="researcher_agent",
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
    tools=[google_search],
    output_key="research_briefing",
)

# --- Step 2: Writer ---
# Drafts the outreach email using ONLY the research briefing as input —
# {research_briefing} below is automatically filled in by ADK with
# whatever the researcher agent produced above.
writer = Agent(
    name="writer_agent",
    model="gemini-2.5-flash-lite",
    instruction="""You are a Sales Outreach Writer. You will be given a 
research briefing below:

{research_briefing}

Your job is to turn this briefing into a short, personalized cold outreach 
email. Follow these rules:

1. Subject line: short, specific, never generic ("Quick question" is banned; 
reference something real about the company instead).
2. Opening line: reference the RECENT NEWS or WHAT THEY DO specifically — 
prove you did your homework, don't open with "I hope this email finds you well."
3. Body: 2-3 sentences max. Connect the LIKELY PAIN POINT to a plausible way 
our product/service could help. Do not invent specific product names or 
claims — stay general (e.g. "a tool like ours" or "solutions in this space") 
since you don't know what the sender actually sells.
4. Close: one clear, low-pressure call to action (e.g. asking for 15 minutes, 
not demanding a meeting).
5. Total email length: under 120 words.
6. Tone: confident, respectful, human — not salesy or robotic.

Respond in EXACTLY this format:

SUBJECT: [subject line]
EMAIL:
[full email body, including greeting and sign-off placeholder like 
"Best, [Your Name]"]
""",
    output_key="draft_email",
)

# --- Step 3: Saver ---
# Logs the completed lead to the CRM via a custom tool (save_lead_record).
# SECURITY DESIGN: this agent never sends anything — the tool it calls
# only writes a row to a CSV with status "PENDING REVIEW". A human must
# read and approve every record before any real outreach happens. This is
# an intentional safety boundary, not a missing feature.
saver = Agent(
    name="saver_agent",
    model="gemini-2.5-flash-lite",
    instruction="""You will be given a company's research briefing and a 
draft email below:

RESEARCH:
{research_briefing}

DRAFT EMAIL:
{draft_email}

Call the save_lead_record tool with these exact values: the company name 
(extract it from the COMPANY: field in the research), the full research 
briefing text, and the full draft email text. After calling the tool, 
simply repeat back its confirmation message to the user.""",
    tools=[save_lead_record],
)

# The full pipeline: always runs researcher -> writer -> saver, in that
# fixed order, with state automatically flowing between them.
root_agent = SequentialAgent(
    name="lead_scout_orchestrator",
    sub_agents=[researcher, writer, saver],
)