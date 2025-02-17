import google.generativeai as genai
import logging
import re
from typing import Optional, Dict
from googletrans import Translator
from langdetect import detect

logger = logging.getLogger(__name__)

class ChatHandler:
    def __init__(self):
        self.api_key = "AIzaSyAswEuyhZaI01rPiLN18pR0G672ivdMTZw"
        self.context = ""
        self.page_sections: Dict[str, str] = {}
        self.translator = Translator()
        self.initialize_gemini()

    def initialize_gemini(self):
        """Initialize the Gemini API client"""
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')

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

    def translate_text(self, text: str, target_lang: str) -> str:
        """Translate text to target language if needed."""
        try:
            if not text or target_lang == 'en':
                return text

            translated = self.translator.translate(text, dest=target_lang)
            return translated.text
        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            return text

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

    def get_response(self, user_message: str, target_lang: str = 'en') -> str:
        """Generate a response using Gemini API with relevant context and translation"""
        try:
            # Detect input language and translate to English if needed
            detected_lang = detect(user_message)
            if detected_lang != 'en':
                translated_query = self.translate_text(user_message, 'en')
            else:
                translated_query = user_message

            # Find relevant content sections for the query
            relevant_content = self.find_relevant_sections(translated_query)

            prompt = f"""
            You are a TVF bot for the Verma Family website. Your purpose is to help users understand and navigate the website's content and features.

            Here is the relevant website content for answering the user's question:
            {relevant_content}

            Additional Guidelines:
            1. Answer based on the website content provided above
            2. When mentioning URLs, format them as proper markdown links: [Link Text](URL)
            3. Use single asterisks for italic text: *italic*
            4. Use double asterisks for bold text: **bold**
            5. For lists, use proper markdown:
               - Use * for unordered lists
               - Use 1. 2. 3. for ordered lists
            6. Keep paragraphs properly spaced
            7. Use a friendly, professional tone
            8. When mentioning specific pages, always include their URLs as clickable links

            User Question: {translated_query}

            Please provide a detailed, accurate response using proper markdown formatting:
            """

            response = self.model.generate_content(prompt)
            response_text = response.text

            # Translate response if needed
            if target_lang != 'en':
                response_text = self.translate_text(response_text, target_lang)

            return response_text

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            error_messages = {
                'en': "I apologize, but I'm having trouble generating a response right now. Please try again later.",
                'hi': "क्षमा करें, मैं अभी जवाब नहीं दे पा रहा हूं। कृपया बाद में पुनः प्रयास करें।",
                'es': "Lo siento, pero tengo problemas para generar una respuesta ahora. Por favor, inténtalo de nuevo más tarde.",
                'fr': "Je suis désolé, mais j'ai du mal à générer une réponse pour le moment. Veuillez réessayer plus tard.",
                'de': "Es tut mir leid, aber ich habe momentan Probleme, eine Antwort zu generieren. Bitte versuchen Sie es später erneut."
            }
            return error_messages.get(target_lang, error_messages['en'])