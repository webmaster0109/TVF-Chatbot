import google.generativeai as genai
import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)

class ChatHandler:
    def __init__(self):
        self.api_key = "AIzaSyAswEuyhZaI01rPiLN18pR0G672ivdMTZw"
        self.context = ""
        self.page_sections = {}
        self.initialize_gemini()

    def initialize_gemini(self):
        """Initialize the Gemini API client"""
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def initialize_context(self, website_content: str):
        """
        Process and organize website content for better context handling.
        Breaks down content into searchable sections.
        """
        self.context = website_content
        # Split content into sections based on delimiter
        sections = re.split(r'\n=+\n', website_content)
        for section in sections:
            if section.strip():
                # Extract page title if present
                title_match = re.search(r'Page:\s*(.+?)\n', section)
                if title_match:
                    title = title_match.group(1).strip()
                    self.page_sections[title] = section.strip()

    def find_relevant_sections(self, query: str) -> str:
        """Find most relevant content sections for the query."""
        relevant_content = []
        query_terms = set(query.lower().split())

        for title, content in self.page_sections.items():
            # Simple relevance check - can be improved with better algorithms
            if any(term in content.lower() for term in query_terms):
                relevant_content.append(content)

        # If no specific sections found, use main page content
        if not relevant_content and 'Home' in self.page_sections:
            relevant_content.append(self.page_sections['Home'])

        return "\n\n".join(relevant_content[:3])  # Limit to top 3 most relevant sections

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