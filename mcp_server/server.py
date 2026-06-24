"""
MCP-style Tool Server: save_lead_record

Defines a single tool that the Saver agent calls to log a completed lead
to a local CSV file, acting as a lightweight CRM tracker.

This follows the MCP (Model Context Protocol) pattern: the @mcp.tool()
decorator and the function's docstring together tell an agent what the
tool does and what arguments it needs, without the agent needing any
hardcoded knowledge of this file's internals.

SECURITY DESIGN: every record is saved with status "PENDING REVIEW" and
nothing in this codebase ever sends an email automatically. This is the
human-approval gate described in the project's security features — a
deliberate boundary, not an oversight.
"""

import csv
import os
from datetime import datetime
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("lead_scout_crm")

# CRM file lives one directory up from this file (the project root), so
# it's easy to find and open regardless of which script imports this tool.
CRM_FILE = os.path.join(os.path.dirname(__file__), "..", "leads_crm.csv")


@mcp.tool()
def save_lead_record(company: str, research_briefing: str, draft_email: str) -> str:
    """Saves a researched lead and its draft outreach email to the CRM 
    tracker (a local CSV file). This is the final step after research and 
    email drafting are complete. The record is saved as PENDING REVIEW — 
    no email is ever sent automatically; a human must review and approve 
    it first.

    Args:
        company: The name of the company that was researched.
        research_briefing: The full structured research output.
        draft_email: The full drafted outreach email (subject + body).

    Returns:
        A confirmation message including the row number saved.
    """
    # Only write the header row once — check before opening in append mode.
    file_exists = os.path.isfile(CRM_FILE)

    with open(CRM_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "timestamp", "company", "research_briefing",
                "draft_email", "status"
            ])
        writer.writerow([
            datetime.now().isoformat(timespec="seconds"),
            company,
            research_briefing,
            draft_email,
            # Hardcoded, not a parameter — this tool has no way to mark
            # something as "sent." That decision is reserved for a human
            # acting outside this codebase entirely.
            "PENDING REVIEW",
        ])

    return f"Saved lead record for '{company}' to CRM. Status: PENDING REVIEW (not sent — awaiting human approval)."


if __name__ == "__main__":
    # Allows this file to also run as a standalone MCP server process via
    # `python server.py`, separate from being imported as a tool directly
    # (which is how it's actually used in this project, via orchestrator
    # and app.py).
    mcp.run()