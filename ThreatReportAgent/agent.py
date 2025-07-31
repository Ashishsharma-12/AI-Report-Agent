import os
from dotenv import load_dotenv, find_dotenv
import asyncio
from .utils.utils import get_urls_by_region, extract_text_from_urls
from .utils.prompt import MAIN_PROMPT
from google.adk.agents import LlmAgent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner 
from google.genai import types
import logging

# Load environment variables
load_dotenv(find_dotenv())

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the summarisation model
model = os.getenv("MODEL_NAME")

# Define the AI Agent
root_agent = LlmAgent(
    name="ThreatReportAgent",
    description="An agent that provides summaries of AI governance policies from various websites, categorized by region.",
    instruction=MAIN_PROMPT,
    tools=[get_urls_by_region, extract_text_from_urls],
    model='gemini-2.5-flash'
)
logger.info(f"Created agent: {root_agent}")
APP_NAME = 'Threat Report App'
USER_ID = 'Alpha1'
SESSION_ID = 'Alpha1-Session1'

session_service = InMemorySessionService()
session = session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
logger.info(f"Created session: {session}")

runner = Runner(
    agent = root_agent,
    session_service = session_service,
    app_name=APP_NAME, 
)
logger.info(f"Created runner: {runner}")

async def call_agent_async(query: str, runner, user_id, session_id):
  """Sends a query to the agent and prints the final response.
  
  Args:
    query (str): The user's query.
    runner (Runner): The runner object.
    user_id (str): The user ID.
    session_id (str): The session ID.

  Returns:
    str: The final response from the agent.
  """
  print(f"\n>>> User Query: {query}")

  # Prepare the user's message in ADK format
  content = types.Content(role='user', parts=[types.Part(text=query)])

  final_response_text = "Agent did not produce a final response." # Default

  # Key Concept: run_async executes the agent logic and yields Events.
  # We iterate through events to find the final answer.
  async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
      # You can uncomment the line below to see *all* events during execution
      print(f"  [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}, Content: {event.content}")

      # Key Concept: is_final_response() marks the concluding message for the turn.
      if event.is_final_response():
          if event.content and event.content.parts:
             # Assuming text response in the first part
             final_response_text = event.content.parts[0].text
          elif event.actions and event.actions.escalate: # Handle potential errors/escalations
             final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
          # Add more checks here if needed (e.g., specific error codes)
          break # Stop processing events once the final response is found

  print(f"<<< Agent Response: {final_response_text}")
  return final_response_text

def orchestrate(query) -> str:
    """Orchestrate the agent to answer the user's query.
    
    Args:
        query (str): The user's query.
    """
    return asyncio.run(call_agent_async(query, runner, USER_ID, SESSION_ID))


if __name__ == "__main__":
    response = orchestrate("What are the latest AI governance laws in the UK region?")
    print(response)

    