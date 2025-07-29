from google.adk.agents import LlmAgent
from google.adk.tools import google_search
from google.genai import types
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner 
import logging
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)    

def extract_text_from_url(url: str) -> str:
    """Extracts text from a given URL.
    
    Args:
        url (str): The URL to extract text from.
    
    Returns:
        str: The extracted text.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = [p.get_text() for p in soup.find_all("p")]
        logger.info(f"Scraped {url}") 
        return " ".join(paragraphs)
          
    except requests.RequestException as e:
        logger.error(f"Error scraping {url}: {e}")
        return f"Error scraping {url}: {e}"

SearchAgent = LlmAgent(
    name="SearchAgent",
    description="An agent that searches for information using Google Search.",
    instruction="Search for information using the available functions",
    tools=[extract_text_from_url, google_search],
    model='gemini-2.5-flash'
)

APP_NAME = 'Search App'
USER_ID = 'searchmaster'
SESSION_ID = 'searchmaster-Session1'

session_service = InMemorySessionService()
session = session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
logger.info(f"Created session: {session}")

runner = Runner(
    agent = SearchAgent,
    session_service = session_service,
    app_name=APP_NAME, 
)
logger.info(f"Created runner: {runner}")

async def call_searchagent_async(query: str, runner, user_id, session_id):
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

async def run_search(query:str) -> str:
    """Runs the search agent to answer the user's query."""
    return await call_searchagent_async(query, runner, USER_ID, SESSION_ID)