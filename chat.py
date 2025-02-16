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
            As a helpful chatbot for the website, use the following context to answer the user's question.
            If you don't find relevant information in the context, provide a general helpful response.
            
            Context:
            {self.context}
            
            User Question: {user_message}
            """
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "I apologize, but I'm having trouble generating a response right now. Please try again later."
