from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from model_loader import SentimentModel
from logger_setup import logger


class GraphState(TypedDict):
    input_text: str
    prediction: Optional[str]
    confidence: Optional[float]
    final_decision: Optional[str]
    fallback_invoked: bool

class ClassificationDAG:
    """
    Builds and compiles the self-healing LangGraph DAG.
    """
    def __init__(self, model: SentimentModel):
        self.model = model
        self.confidence_threshold = 0.90 # Define the confidence threshold here. Kept it high for easy testing of the fallback logic.


    # ... (inside the SentimentModel class)
    def predict_primary(self, text: str) -> dict:
        """
        Runs a prediction using the primary model.
        Since top_k=1, the result is a list with one item, which we directly access.
        """
        result_list = self.primary_classifier(text)[0]
        
        top_prediction = result_list[0]
        
        return {
            "prediction": self.label_map[top_prediction['label']],
            "confidence": top_prediction['score']
        }
    

    # ... (inside the ClassificationDAG class)
    def run_inference(self, state: GraphState) -> dict:
        """ 
        Runs the primary model inference by calling the model's prediction method.
        """
        logger.info("--- INFERENCE (Primary Model) ---")
        input_text = state['input_text']
        
        result = self.model.predict_primary(input_text)
        print(f"  Prediction: '{result['prediction']}' | Confidence: {result['confidence']:.2%}")
        logger.info(f"  Prediction: '{result['prediction']}' | Confidence: {result['confidence']:.2%}")
        
        # The result dictionary already has the keys we need for the state.
        return {
            "prediction": result['prediction'],
            "confidence": result['confidence'],
            "fallback_invoked": False
        }


    def run_fallback_with_human_in_loop(state: GraphState):
        """ Handles the fallback logic when the primary model's confidence is low. This method prompts the user for"""
        logger.info("\n--- FALLBACK (Human Verification) ---") 
        question = f"  The model is not confident in its prediction of '{state['prediction']}'.\n  Was your review negative? (yes/no): "
        
        while True:
            user_response = input(question).strip().lower()
            if user_response in ["yes", "no"]:
                break
            logger.warning("  Invalid input. Please enter 'yes' or 'no'.")

        final_decision = "Negative" if user_response == "yes" else "Positive"

        logger.info(f"  User clarified. Final Decision: {final_decision}")
        return {"final_decision": final_decision, "fallback_invoked": True}


    def run_fallback_with_zero_shot(self, state: GraphState) -> dict:
        """ Handles the fallback logic using a zero-shot model when the primary model's confidence is low."""
        logger.info("\n--- FALLBACK (Zero-Shot Model) ---")
        print("  Primary model confidence was low. Consulting backup model...")
        logger.info("  Primary model confidence was low. Consulting backup model...")
        input_text = state['input_text']

        candidate_labels = ["Positive", "Negative"]

        # The zero-shot pipeline returns one dictionary.
        # The results are already sorted by score.
        result = self.model.fallback_classifier(input_text, candidate_labels=candidate_labels)

        # The highest-scoring label is the first one in the 'labels' list.
        final_decision = result['labels'][0]
        confidence = result['scores'][0]

        print(f" Backup Model Prediction: '{final_decision}' | Confidence: {confidence:.2%}")
        logger.info(f" Backup Model Prediction: '{final_decision}' | Confidence: {confidence:.2%}")

        return {
            "final_decision": final_decision,
            "fallback_invoked": True
        }

    def set_final_decision(self, state: GraphState) -> dict:
        """ Sets the final decision based on the model's prediction and confidence."""
        logger.info("\n--- ACCEPTING ---")
        logger.info(" Confidence is high. Final decision matches model prediction.")
        final_decision = state['prediction']
        return {"final_decision": final_decision}


    def check_confidence(self, state: GraphState) -> str:
        """ Checks the confidence of the model's prediction and decides whether to ask the user or accept the prediction."""
        logger.info("\n--- CONFIDENCE CHECK ---")
        if state['confidence'] < self.confidence_threshold:
            logger.info(f" Confidence {state['confidence']:.2%} is below threshold. Triggering fallback.")
            return "ask_user" # route_name to fall back
        else:
            logger.info(f" Confidence {state['confidence']:.2%} is high. Accepting prediction.")
            return "accept_prediction"


    def build_graph(self):
        workflow = StateGraph(GraphState)

        workflow.add_node("inference", self.run_inference)
        # workflow.add_node("fallback", self.run_fallback_with_human)
        workflow.add_node("fallback", self.run_fallback_with_zero_shot)
        workflow.add_node("accept", self.set_final_decision)

        workflow.set_entry_point("inference")

        workflow.add_conditional_edges(
            "inference",
            self.check_confidence,
            {
                "ask_user": "fallback",
                "accept_prediction": "accept",
            }
        )
        
        workflow.add_edge("fallback", END)
        workflow.add_edge("accept", END)

        logger.info("LangGraph compiled.")
        return workflow.compile()