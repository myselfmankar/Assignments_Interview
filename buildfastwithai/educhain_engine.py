
from dotenv import load_dotenv
from educhain import Educhain, LLMConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Optional

import os

class Engine_G():
    def __init__(self):
        """Initialize the Educhain engine with Google Gemini model."""
        self.client = None
        load_dotenv()
        gemini_api_key =os.getenv("GOOGLE_API_KEY")
        if gemini_api_key:
            gemini_flash = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                api_key=gemini_api_key
            )
            gemini_config = LLMConfig(custom_model=gemini_flash)
            self.client = Educhain(gemini_config)
        else:
            raise ValueError("GOOGLE_API_KEY not found in environment variables.")


    def create_mcq(self, topic: str, num_que: Optional[int] = 5, custom_instruction: Optional[str] = "Focus on fundamental concepts"):
        """
        Create multiple-choice questions based on the given topic.
        Return: A object containing the MCQs.
        """
        try: 
            questions = self.client.qna_engine.generate_questions(
                topic=topic,
                num=num_que, 
                custom_instruction=custom_instruction
            )
            return questions
        except Exception as e:
            return f"Error generating questions: {e}"
    

    def create_leason_plan(self, topic: str, grade_level: Optional[int] = None ,custom_instruction: Optional[str] = None):
        """
        Create a lesson plan based on the given topic.
        Return: A object containing the lesson plan.
        """
        try:
            lesson_plan = self.client.content_engine.create_lesson_plan(
                topic="Python Programming",
                custom_instruction=custom_instruction,
                grade_level=grade_level
            )
            return lesson_plan
        except Exception as e:
            return f"Error generating lesson plan: {e}"
        
    def create_flashcards(self, topic: str, num_flashcards: Optional[int] = 1, custom_instruction: Optional[str] = "Focus on key concepts"):
        """
        Create flashcards based on the given topic.
        Return: A object containing the flashcards.
        """
        try:
            flashcards = self.client.content_engine.generate_flashcards(
                topic=topic,
                num=num_flashcards,
                custom_instruction=custom_instruction
            )
            return flashcards
        except Exception as e:
            return f"Error generating flashcards: {e}"
        
