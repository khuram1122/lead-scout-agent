"""
Lead Scout — Streamlit UI

A simple front end for the Lead Scout multi-agent pipeline. Enter a company
name, and the app runs the full Research -> Write -> Save pipeline, then
displays the research briefing and draft email for human review.

Nothing is ever sent automatically. Every result is saved to leads_crm.csv
with status PENDING REVIEW.
"""

from dotenv import load_dotenv
load_dotenv()

import asyncio
import os
import time
import streamlit as st
from google.adk.runners import InMemoryRunner
from google.genai import types
from google.genai.errors import ServerError

from orchestrator_agent.agent import root_agent

# Path to the CRM file, same one save_lead_record writes to (see
# mcp_server/server.py). Defined here too so the download button can read
# it directly, regardless of whether the app is running locally or on
# Streamlit Cloud.
CRM_FILE_PATH = os.path.join(os.path.dirname(__file__), "leads_crm.csv")

MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 20


async def run_pipeline(company_name: str):
    """Runs the full orchestrator pipeline for one company and returns the
    research briefing and draft email as separate strings, plus the saver
    agent's confirmation message."""
    runner = InMemoryRunner(agent=root_agent, app_name="lead_scout_app")
    session = await runner.session_service.create_session(
        app_name="lead_scout_app", user_id="ui_user"
    )
    content = types.Content(role="user", parts=[types.Part(text=company_name)])

    research_text = ""
    email_text = ""
    save_confirmation = ""

    async for event in runner.run_async(
        user_id="ui_user", session_id=session.id, new_message=content
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if not part.text:
                    continue
                if event.author == "researcher_agent":
                    research_text = part.text
                elif event.author == "writer_agent":
                    email_text = part.text
                elif event.author == "saver_agent":
                    save_confirmation = part.text

    return research_text, email_text, save_confirmation


def run_pipeline_with_retry(company_name: str):
    """Sync wrapper with retry-on-503 logic, for use inside Streamlit."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return asyncio.run(run_pipeline(company_name))
        except ServerError:
            if attempt == MAX_RETRIES:
                raise
            time.sleep(RETRY_DELAY_SECONDS)


st.set_page_config(page_title="Lead Scout", page_icon="🔍", layout="centered")

st.title("🔍 Lead Scout")
st.caption(
    "AI sales research & outreach agent — enter a company name to generate "
    "a grounded research briefing and a personalized outreach email."
)

with st.form("lead_form"):
    company_name = st.text_input(
        "Company name",
        placeholder="e.g. Stripe, Notion, Zapier",
    )
    submitted = st.form_submit_button("Research & Draft")

if submitted:
    if not company_name.strip():
        st.warning("Enter a company name first.")
    else:
        with st.spinner(f"Researching {company_name} and drafting outreach..."):
            try:
                research, email, confirmation = run_pipeline_with_retry(
                    company_name.strip()
                )
            except ServerError:
                st.error(
                    "Google's servers are temporarily overloaded. Please "
                    "wait a minute and try again."
                )
                st.stop()
            except Exception as e:
                if "RESOURCE_EXHAUSTED" in str(e):
                    st.error(
                        "Daily API quota reached on the free tier. This "
                        "resets at midnight Pacific Time. Please try again "
                        "later."
                    )
                else:
                    st.error(f"Something went wrong: {e}")
                st.stop()

        st.success("Done — review the results below before sending anything.")

        st.subheader("📋 Research Briefing")
        st.text(research)

        st.subheader("✉️ Draft Outreach Email")
        st.text(email)

        st.subheader("💾 CRM Status")
        st.info(confirmation or "Saved to leads_crm.csv — status: PENDING REVIEW")

        st.caption(
            "Nothing has been sent. This draft is saved for human review."
        )

        # Offer the CRM file as a direct download right after a successful
        # run, since the record was just added to it.
        if os.path.isfile(CRM_FILE_PATH):
            with open(CRM_FILE_PATH, "rb") as f:
                st.download_button(
                    label="⬇️ Download CRM tracker (leads_crm.csv)",
                    data=f,
                    file_name="leads_crm.csv",
                    mime="text/csv",
                )

st.divider()

# Standalone download section — lets anyone (including judges trying the
# live deployed app) pull the current CRM tracker at any time, even
# without running a new search first.
st.subheader("📂 View All Saved Leads")
if os.path.isfile(CRM_FILE_PATH):
    with open(CRM_FILE_PATH, "rb") as f:
        crm_bytes = f.read()
    st.download_button(
        label="⬇️ Download full CRM tracker (leads_crm.csv)",
        data=crm_bytes,
        file_name="leads_crm.csv",
        mime="text/csv",
        key="standalone_download",
    )
else:
    st.caption("No leads saved yet on this instance. Research a company above to get started.")

st.caption(
    "Lead Scout never sends emails automatically — every result requires "
    "human approval before outreach."
)
