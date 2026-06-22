from dotenv import load_dotenv
load_dotenv()

import asyncio
import sys
import time
from google.adk.runners import InMemoryRunner
from orchestrator_agent.agent import root_agent
from google.genai import types
from google.genai.errors import ServerError

company_name = sys.argv[1] if len(sys.argv) > 1 else "Stripe"

MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 20


async def run_pipeline():
    runner = InMemoryRunner(agent=root_agent, app_name="test_app")
    session = await runner.session_service.create_session(
        app_name="test_app", user_id="test_user"
    )
    content = types.Content(role="user", parts=[types.Part(text=company_name)])

    async for event in runner.run_async(
        user_id="test_user", session_id=session.id, new_message=content
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(f"--- {event.author} ---")
                    print(part.text)
                    print()


async def main():
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            await run_pipeline()
            return
        except ServerError as e:
            print(f"[Attempt {attempt}/{MAX_RETRIES}] Server busy (503). "
                  f"Retrying in {RETRY_DELAY_SECONDS}s...")
            if attempt == MAX_RETRIES:
                print("Max retries reached. Google's servers are likely "
                      "under heavy load. Try again in a few minutes.")
                raise
            time.sleep(RETRY_DELAY_SECONDS)

asyncio.run(main())