import google.generativeai as genai
import logging
import re
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class ChatHandler:
    def __init__(self):
        self.api_key = "AIzaSyAswEuyhZaI01rPiLN18pR0G672ivdMTZw"
        self.context = ""
        self.page_sections: Dict[str, str] = {}
        self.initialize_gemini()

    def initialize_gemini(self):
        """Initialize the Gemini API client"""
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def initialize_context(self, website_content: str):
        """
        Process and organize website content for better context handling.
        Breaks down content into searchable sections and maintains a map of pages.
        """
        self.context = website_content
        # Split content into sections based on delimiter
        sections = re.split(r'\n=+\n', website_content)
        for section in sections:
            if section.strip():
                # Extract page title and URL if present
                title_match = re.search(r'Page:\s*(.+?)\n', section)
                url_match = re.search(r'URL:\s*(.+?)\n', section)

                if title_match:
                    title = title_match.group(1).strip()
                    self.page_sections[title] = section.strip()
                    logger.debug(f"Added content section for page: {title}")

    def find_relevant_sections(self, query: str) -> str:
        """Find most relevant content sections for the query using keyword matching."""
        if not query:
            return self.page_sections.get('Home', '')

        relevant_content = []
        query_terms = set(query.lower().split())

        # Score each section based on term matches
        scored_sections = []
        for title, content in self.page_sections.items():
            score = 0
            content_lower = content.lower()

            # Score based on title matches
            if any(term in title.lower() for term in query_terms):
                score += 5

            # Score based on content matches
            for term in query_terms:
                score += content_lower.count(term)

            if score > 0:
                scored_sections.append((score, content))

        # Sort by relevance score and take top 3
        scored_sections.sort(reverse=True)
        relevant_content = [content for _, content in scored_sections[:3]]

        # If no matches found, include home page as fallback
        if not relevant_content and 'Home' in self.page_sections:
            relevant_content.append(self.page_sections['Home'])

        return "\n\n".join(relevant_content)

    def get_response(self, user_message: str) -> str:
        """Generate a response using Gemini API with relevant context"""
        try:
            # Find relevant content sections for the query
            relevant_content = self.find_relevant_sections(user_message)

            prompt = f"""
            You are a knowledgeable assistant for the website www.thevermafamily.org. Your purpose is to help users understand and navigate the website's content and features.

            Here is the relevant website content for answering the user's question:
            {relevant_content}

            Additional Guidelines:
            1. Answer based on the website content provided above
            2. If mentioning a specific page or section, include its URL if available
            3. For navigation questions, provide clear step-by-step directions
            4. If information isn't in the content, say so clearly and offer to help with other topics
            5. Use a friendly, professional tone
            6. If relevant, mention related pages or sections the user might find helpful

            User Question: {user_message}

            Please provide a detailed, accurate response based on the website content:
            """

            response = self.model.generate_content(prompt)
            return response.text

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "I apologize, but I'm having trouble generating a response right now. Please try again later."