import google.generativeai as genai
import logging

logger = logging.getLogger(__name__)

class ChatHandler:
    def __init__(self):
        self.api_key = "AIzaSyAswEuyhZaI01rPiLN18pR0G672ivdMTZw"
        self.context = ""
        self.initialize_gemini()

    def initialize_gemini(self):
        """Initialize the Gemini API client"""
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def initialize_context(self, website_content: str):
        """Set the website content as context for the chatbot"""
        self.context = website_content

    def get_response(self, user_message: str) -> str:
        """Generate a response using Gemini API"""
        try:
            prompt = f"""
            You are a helpful and knowledgeable assistant for the website www.thevermafamily.org. Your purpose is to help users understand and navigate the website's content and features.

            Use the following website content to answer user questions accurately and comprehensively. If the information is available in the content, provide specific details and direct quotes when relevant. If asked about navigation, refer to specific sections or pages.

            Website Content:
            {self.context}

            Important Guidelines:
            1. If the information is in the content, provide detailed, accurate answers
            2. If asked about a specific page or section, mention its location on the website
            3. For navigation questions, provide clear directions
            4. If information isn't available, politely say so and offer to help with other aspects
            5. Keep responses friendly and professional

            User Question: {user_message}

            Please provide a helpful, accurate response based on the website content above:
            """

            response = self.model.generate_content(prompt)
            return response.text

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "I apologize, but I'm having trouble generating a response right now. Please try again later."