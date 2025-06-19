from load_model import load_model
from chat_memory import ChatMemory

def main():
    """
    The main orchestration loop for the chatbot application.
    """
    print("Local Chatbot (type /exit to quit)\n")
    
    generator = load_model()
    if generator is None:
        return


    memory = ChatMemory(window_size=3)

    while True:
        try:
            user_input = input("User: ")
        except (KeyboardInterrupt, EOFError):
            # Handle Ctrl+C or Ctrl+D gracefully as an exit command
            print("\nExiting chatbot. Goodbye!")
            break

        if user_input.strip().lower() == "/exit":
            print("Exiting chatbot. Goodbye!")
            break

        prompt = memory.build_prompt(user_input)

        try:
            outputs = generator(prompt, max_length=50, max_new_tokens=None)
            bot_response = outputs[0]['generated_text'].strip()
            
            # A check for an empty response
            if not bot_response:
                bot_response = "I'm not sure how to respond to that."

            print(f"Bot: {bot_response}")
            memory.add_message(user_input, bot_response)

        except Exception as e:
            print(f"An error occurred during generation: {e}")

if __name__ == "__main__":
    main()