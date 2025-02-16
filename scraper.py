import trafilatura
import logging
from urllib.parse import urljoin, urlparse
import re
import time
from typing import Set, Dict, List

logger = logging.getLogger(__name__)

def is_internal_link(base_url: str, link: str) -> bool:
    """Check if a link is internal to the website."""
    base_domain = urlparse(base_url).netloc
    link_domain = urlparse(link).netloc
    return not link_domain or base_domain in link_domain

def clean_page_name(url: str) -> str:
    """Convert URL to readable page name."""
    path = urlparse(url).path.strip('/')
    name = path.split('/')[-1] if path else 'Home'
    return re.sub(r'[-_]', ' ', name).title() or 'Home'

def get_website_content(base_url: str, max_pages: int = 100) -> str:
    """
    Recursively extracts content from the website and its subdomains.

    Args:
        base_url: The main website URL
        max_pages: Maximum number of pages to crawl

    Returns:
        Structured content from all pages
    """
    try:
        visited_urls: Set[str] = set()
        to_visit: List[str] = [base_url]
        content_sections: Dict[str, str] = {}

        while to_visit and len(visited_urls) < max_pages:
            current_url = to_visit.pop(0)
            if current_url in visited_urls:
                continue

            logger.info(f"Processing page: {current_url}")

            try:
                # Add delay to prevent overwhelming the server
                time.sleep(1)

                # Download and extract content
                downloaded = trafilatura.fetch_url(current_url)
                if not downloaded:
                    continue

                # Extract main content with all features enabled
                content = trafilatura.extract(
                    downloaded,
                    include_links=True,
                    include_images=True,
                    include_formatting=True,
                    with_metadata=True
                )

                if not content:
                    continue

                # Extract metadata
                metadata = trafilatura.extract_metadata(downloaded)
                title = metadata.title if metadata else clean_page_name(current_url)

                # Store content with metadata
                page_content = f"""
                Page: {title}
                URL: {current_url}

                Content:
                {content}
                """
                content_sections[title] = page_content

                # Extract and process new links
                if metadata and metadata.get('links'):
                    new_links = metadata.get('links', [])
                    for link in new_links:
                        if isinstance(link, str) and is_internal_link(base_url, link):
                            full_url = urljoin(base_url, link)
                            if full_url not in visited_urls:
                                to_visit.append(full_url)

                visited_urls.add(current_url)

            except Exception as e:
                logger.warning(f"Error processing {current_url}: {str(e)}")
                continue

        # Combine all content sections
        website_content = "\n\n=== WEBSITE CONTENT SECTIONS ===\n\n"
        for title, content in content_sections.items():
            website_content += f"\n{'='*50}\n{content}\n"

        return website_content

    except Exception as e:
        logger.error(f"Error scraping website: {str(e)}")
        return ""