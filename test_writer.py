from dotenv import load_dotenv
load_dotenv()
import asyncio
from google.adk.runners import InMemoryRunner
from writer_agent.agent import root_agent
from google.genai import types

briefing = """COMPANY: Notion
WHAT THEY DO: Notion is an all-in-one workspace and productivity application that combines note-taking, knowledge management, data organization, and project and task tracking into a single, customizable platform.
RECENT NEWS: Notion recently launched a developer platform featuring "Notion Workers" for building automated workflows and connecting external data, aiming to position its workspace as programmable infrastructure for AI-enabled work. They also launched Notion Mail in April 2025, following their acquisition of Skiff.
LIKELY PAIN POINT: As Notion grows and integrates more complex features like AI agents and a developer platform, users may experience a steeper learning curve and find it challenging to manage and organize their workspaces effectively, especially those who are not deeply technical.
SUGGESTED ANGLE: Given Notion's recent expansion into a programmable AI workspace with features like Notion Workers, I was curious if your team is exploring ways to automate workflows or integrate custom code directly within your Notion environment to enhance productivity."""

async def main():
    runner = InMemoryRunner(agent=root_agent, app_name="test_app")
    session = await runner.session_service.create_session(
        app_name="test_app", user_id="test_user"
    )
    content = types.Content(role="user", parts=[types.Part(text=briefing)])

    async for event in runner.run_async(
        user_id="test_user", session_id=session.id, new_message=content
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(part.text)

asyncio.run(main())