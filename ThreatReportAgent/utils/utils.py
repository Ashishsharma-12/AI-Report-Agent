from typing import List, Dict
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

# Sample list of websites to monitor
WEBSITE_LIST = [
    "https://ec.europa.eu/commission/presscorner/detail/en/ip_21_1682",
    "https://www.gov.uk/government/publications/ai-regulation-a-pro-innovation-approach",
]

# Region tags based on source URL for filtering
REGION_MAP = {
    "europa.eu": "EMEA",
    "gov.uk": "UK",
    "parliament.uk": "UK"
}

def get_urls_by_region(region: str) -> List[str]:
    """Gets a list of URLs for a given region.

    Args:
        region (str): The region to get URLs for (e.g., 'UK', 'EMEA').

    Returns:
        List[str]: A list of URLs for the given region.
    """
    urls = []
    for url in WEBSITE_LIST:
        domain = ".".join(urlparse(url).netloc.split('.')[-2:])
        if REGION_MAP.get(domain) == region:
            urls.append(url)
    return urls

# Extract text from URLs
def extract_text_from_urls(url_list:List[str]) -> Dict[str, str]:
    ''' 
    Extracts text from URL

    Args:
        url_list (List[str]): List of URLs to extract text from.

    Returns:
        Dict[str, str]: Dictionary of URLs and their extracted text.
    '''

    extracted_texts = {}

    for url in url_list:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Raise exception for bad status codes

            soup = BeautifulSoup(response.text, 'html.parser')

            # Remove script and style elements
            for script_or_style in soup(['script', 'style']):
                script_or_style.decompose()

            # Extract visible text
            text = soup.get_text(separator='\n')
            lines = [line.strip() for line in text.splitlines()]
            text = '\n'.join(line for line in lines if line)

            extracted_texts[url] = text

        except Exception as e:
            extracted_texts[url] = f"Error: {e}"

    return extracted_texts


if __name__ == "__main__":
    urls = get_urls_by_region("UK")
    texts = extract_text_from_urls(urls)
    print(texts)
    