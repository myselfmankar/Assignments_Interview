from collections import deque

class ChatMemory:
    """
    Manages conversation history and builds a structured prompt for Flan-T5.
    """
    def __init__(self, window_size=3):
        self.history = deque(maxlen=window_size)

    def add_message(self, user_input, bot_response):
        """Adds a new user/bot to the history."""
        self.history.append((user_input, bot_response))

    def build_prompt(self, current_question):
        """Builds a prompt with clear context and question labels."""
        if not self.history:
            return f"question: {current_question}"

        context = ""
        for user_q, bot_a in self.history:
            context += f'The user previously asked "{user_q}" and the bot replied "{bot_a}". '
        
        return f"context: {context.strip()} question: {current_question}"