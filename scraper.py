import trafilatura
import logging
from urllib.parse import urljoin
import re

logger = logging.getLogger(__name__)

def get_website_content(base_url: str) -> str:
    """
    Extracts and processes content from the website using trafilatura.
    Returns processed text content suitable for the chatbot context.
    """
    try:
        # Get main page content
        downloaded = trafilatura.fetch_url(base_url)
        if downloaded is None:
            raise Exception("Failed to fetch website content")

        main_content = trafilatura.extract(downloaded, include_links=True, include_images=True, include_formatting=True)
        if main_content is None:
            raise Exception("Failed to extract text content")

        # Extract and follow internal links
        links = trafilatura.extract_metadata(downloaded).get('links', [])
        all_content = [f"Main Page Content:\n{main_content}\n"]

        # Process internal links
        for link in links:
            if link.startswith('/') or base_url in link:
                try:
                    full_url = urljoin(base_url, link)
                    sub_content = trafilatura.fetch_url(full_url)
                    if sub_content:
                        extracted = trafilatura.extract(sub_content, include_links=True, include_images=True)
                        if extracted:
                            page_name = link.rstrip('/').split('/')[-1] or 'home'
                            page_name = re.sub(r'[-_]', ' ', page_name).title()
                            all_content.append(f"\n{page_name} Page Content:\n{extracted}")
                except Exception as e:
                    logger.warning(f"Error processing link {link}: {str(e)}")
                    continue

        return "\n\n".join(all_content)
    except Exception as e:
        logger.error(f"Error scraping website: {str(e)}")
        return ""