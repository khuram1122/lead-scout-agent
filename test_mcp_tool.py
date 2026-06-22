from mcp_server.server import save_lead_record

result = save_lead_record(
    company="Test Company",
    research_briefing="COMPANY: Test Company\nWHAT THEY DO: Testing things.",
    draft_email="SUBJECT: Test\nEMAIL:\nHi, this is a test.",
)

print(result)