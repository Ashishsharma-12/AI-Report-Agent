from dotenv import load_dotenv, find_dotenv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from typing import Dict, List
import logging
from .SearchAgent import run_search

# Load environment variables

load_dotenv(find_dotenv())

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample list of websites to monitor
WEBSITE_LIST = [
    "https://ec.europa.eu/commission/presscorner/detail/en/ip_21_1682",
    "https://www.gov.uk/government/publications/ai-regulation-a-pro-innovation-approach",
    "https://post.parliament.uk/artificial-intelligence-ethics-governance-and-regulation/"
]

# Region tags based on source URL for filtering
REGION_MAP = {
    "europa.eu": "EMEA",
    "gov.uk": "UK",
    "parliament.uk": "EMEA"
}

# Function to extract text from a given URL
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

# Function to summarize content using a generative model
async def summarize_content(content: str, region: str) -> str:
    """Summarizes content using a generative model.
    
    Args:
        content (str): The content to summarize.
        region (str): The region to summarize for.
    
    Returns:
        str: The summarized content.
    """
    prompt = f"""
    Summarise the key new AI governance laws, regulations, or principles relevant to the {region} region in the following text:

    {content}
    """
    try:
        response = await run_search(query=prompt)
        logger.info(f"Summarized content for {region}")
        return response
        
    except Exception as e:
        logger.error(f"Error summarizing content: {e}")
        return f"Error summarizing content: {e}"

# Function to summarize AI governance laws from a list of URLs, categorized by region
async def summarize_ai_governance_by_region() -> Dict[str, List[Dict[str, str]]]:
    """
    Summarizes new AI governance laws from a list of URLs, categorized by region.

    Returns:
        Dict[str, List[Dict[str, str]]]: A dictionary of summaries categorized by region.
    """
    summaries = {"EMEA": [], "UK": []}
    for url in WEBSITE_LIST:
        parsed_url = urlparse(url)
        domain = ".".join(parsed_url.netloc.split('.')[-2:])
        region = REGION_MAP.get(domain)

        if region:
            content = extract_text_from_url(url)
            if not content.startswith("Error"):
                summary = await summarize_content(content, region)
                summaries[region].append({
                    "source": url,
                    "summary": summary.strip()
                })
    logger.info("Summarized AI governance laws by region")
    return summaries
