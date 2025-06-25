from transformers import pipeline
from logger_setup import logger


class SentimentModel:
    """
    A class to encapsulate the primary and fallback sentiment analysis models.
    """
    def __init__(self, model_hub_id: str, fallback_model_name: str):
        """
        Initializes the model loader.
        Args:
            model_hub_id: The ID of your fine-tuned model on the Hub.
            fallback_model_name: The name of the zero-shot model to use as a backup.
        """
        # --- Load Primary Fine-Tuned Model ---
        try:
            logger.info(f"Loading primary model from '{model_hub_id}'...")
            self.primary_classifier = pipeline(
                "text-classification",
                model=model_hub_id,
                # return_all_scores=True
                top_k=1  # 0 => all lable, 1 => best label
            )
            self.label_map = {"LABEL_0": "Negative", "LABEL_1": "Positive"}
            logger.info("Primary model loaded successfully.")
        except Exception as e:
            logger.error(f" Error loading primary model. Ensure you have run 'huggingface-cli login'.")
            logger.error(f" Error details: {e}")
            exit()

        # --- Load Fallback Zero-Shot Model ---
        try:
            logger.info(f"Loading fallback zero-shot model '{fallback_model_name}'...")
            self.fallback_classifier = pipeline(
                "zero-shot-classification",
                model=fallback_model_name
            )
            logger.info(" Fallback model loaded successfully.")
        except Exception as e:
            logger.error(f" Error loading fallback model. Error details: {e}")
            exit()

    def predict_primary(self, text: str) -> dict:
        """Runs a prediction using the primary fine-tuned model."""
        results = self.primary_classifier(text)[0]
        top_prediction = max(results, key=lambda x: x['score'])
        return {
            "prediction": self.label_map[top_prediction['label']],
            "confidence": top_prediction['score']
        }

    def predict_fallback(self, text: str) -> dict:
        """Runs a prediction using the fallback zero-shot model."""
        candidate_labels = ["Positive review", "Negative review"]
        hypothesis_template = "The sentiment of this review is {}."
        
        results = self.fallback_classifier(
            text,
            candidate_labels=candidate_labels,
            hypothesis_template=hypothesis_template
        )
        
        # The top score corresponds to the final prediction
        prediction = "Positive" if results['labels'][0] == "Positive review" else "Negative"
        confidence = results['scores'][0]
        
        return {
            "prediction": prediction,
            "confidence": confidence
        }