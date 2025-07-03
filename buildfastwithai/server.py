import mcp
from mcp.server.fastmcp import FastMCP
from educhain_engine import Engine_G
from typing import Optional

engine = Engine_G()

mcp = FastMCP(
    name="Educhain Engine",
    description="A server using EduChain to create educational content.",
    version="0.1.0"
)


@mcp.tool()
def generate_mcq_questions(topic: str, number_of_question: Optional[int], custom_intruction: Optional[str]): 
    """
    Create multiple-choice questions based on the given topic. 
    Args: 
        topic: The topic for which to create MCQs.
        num: The number of MCQs to create.
        custom_instruction: Optional custom instruction for the model.
    
    Returns: A json containing the MCQs and answers.
    """
    try: 
        questions = engine.create_mcq(
            topic=topic, 
            num_que=number_of_question, 
            custom_instruction=custom_intruction
        )
        return questions.model_dump_json(indent=2) 
    except Exception as e:
        print(f"Error generating questions: {e}")
        return "Sorry, an error occured while generating questions. Please try again later."
    
@mcp.tool()
def generate_lesson_plan(topic: str, grade_level: Optional[int] = None, custom_instruction: Optional[str] = None):
    """
    Create a lesson plan based on the given topic.
    Args:
        topic: The topic for which to create a lesson plan.
        grade_level: Optional grade level for the lesson plan.
        custom_instruction: Optional custom instruction for the model.

    Returns: A json containing the lesson plan.
    """
    try:
        lesson_plan = engine.create_leason_plan(
            topic=topic, 
            grade_level=grade_level, 
            custom_instruction=custom_instruction
        )
        return lesson_plan.model_dump_json(indent=2)
    except Exception as e:
        print(f"Error generating lesson plan: {e}")
        return "Sorry, an error occured while generating the lesson plan. Please try again later."
    
@mcp.tool()
def generate_flashcards(topic: str, number_of_flashcards: Optional[int] = 1, custom_instruction: Optional[str] = None):
    """
    Create flashcards based on the given topic.
    Args:
        topic: The topic for which to create flashcards.
        num_flashcards: The number of flashcards to create.
        custom_instruction: Optional custom instruction for the model.

    Returns: A json containing the flashcards.
    """
    try:
        flashcards = engine.create_flashcards(
            topic=topic, 
            num_flashcards=number_of_flashcards, 
            custom_instruction=custom_instruction
        )
        return flashcards.model_dump_json(indent=2)
    except Exception as e:
        print(f"Error generating flashcards: {e}")
        return "Sorry, an error occured while generating flashcards. Please try again later."



if __name__ == "__main__":
    mcp.run()