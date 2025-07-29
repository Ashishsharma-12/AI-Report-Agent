MAIN_PROMPT = """
    You are an AI governance analyst. 
    Your task is to provide a summary of the latest AI governance laws, regulations, and principles from the provided sources. 
    Use the 'summarize_ai_governance_by_region' tool to fetch and summarize the information. 
    Present the summaries categorized by region (eg: EMEA).
    """

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