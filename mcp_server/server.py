import csv
import os
from datetime import datetime
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("lead_scout_crm")

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
            "PENDING REVIEW",
        ])

    return f"Saved lead record for '{company}' to CRM. Status: PENDING REVIEW (not sent — awaiting human approval)."


if __name__ == "__main__":
    mcp.run()