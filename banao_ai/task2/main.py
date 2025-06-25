import os
from model_loader import SentimentModel
from graph_builder import ClassificationDAG
from logger_setup import logger
from dotenv import load_dotenv


# to enable-disable logging shown in console
import logging
logging.disable(logging.CRITICAL)  # Disable all logging except critical errors
# logging.disable(logging.NOTSET)    # Enable all logging if required later

load_dotenv()
if not os.getenv("HUGGING_FACE_HUB_TOKEN"):
    logger.error(" Error: HUGGING_FACE_HUB_TOKEN not found.")
    logger.error(" Please create a .env file and add your Hugging Face token.")
    exit()

# --- Configuration ---
HUB_MODEL_ID = "myselfmankar/distilbert-base-sst2-lora" # custom fine-tuned model
FALLBACK_MODEL = "facebook/bart-large-mnli"             # A popular zero-shot model

def run_cli():
    """
    The main Command-Line Interface loop for the application.
    """

    model = SentimentModel(
        model_hub_id=HUB_MODEL_ID,
        fallback_model_name=FALLBACK_MODEL    
    )
    dag_builder = ClassificationDAG(model=model)
    app = dag_builder.build_graph()

    # Start the user interaction loop
    print("\n--- Self-Healing Classification CLI ---")
    
    while True:
        user_input = input("\nInput: ")
        print("Enter a movie review, or type 'quit' to exit.")

        if user_input.lower() == 'quit':
            break
        
        logger.info(f"User Input: '{user_input}'")
        final_state = app.invoke({"input_text": user_input})
        
        # Log the final state of the DAG
        logger.info("--- FINAL OUTPUT ---")
        logger.info(f"Reviewed Text: '{final_state['input_text']}'")
        logger.info(f"Final Label: {final_state['final_decision']}")
        if final_state['fallback_invoked']:
            logger.warning("Final decision was corrected via fallback mechanism.")


        # Also print a clean version for the user
        print("\n" + "="*50)
        print("--- Final Output ---")
        print(f"  Final Label: {final_state['final_decision']}")
        print("="*50)


if __name__ == "__main__":
    run_cli()