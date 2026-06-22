from dotenv import load_dotenv
load_dotenv()

import asyncio
from google.adk.runners import InMemoryRunner
from orchestrator_agent.agent import root_agent
from google.genai import types

company_name = "Stripe"

async def main():
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

asyncio.run(main())