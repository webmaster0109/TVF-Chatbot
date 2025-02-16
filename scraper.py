import trafilatura
import logging

logger = logging.getLogger(__name__)

def get_website_content(url: str) -> str:
    """
    Extracts and processes content from the website using trafilatura.
    Returns processed text content suitable for the chatbot context.
    """
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded is None:
            raise Exception("Failed to fetch website content")
        
        text = trafilatura.extract(downloaded)
        if text is None:
            raise Exception("Failed to extract text content")
        
        return text
    except Exception as e:
        logger.error(f"Error scraping website: {str(e)}")
        return ""
