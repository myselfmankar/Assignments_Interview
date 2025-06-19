from transformers import pipeline

def load_model(model_name="google/flan-t5-base"):
    """
    Loads a pre-trained text2text-generation model from Hugging Face.
    'google/flan-t5-base' is chosen for its balance of size and factual accuracy.
    """
    print(f"Loading model '{model_name}'... This may take a moment.")
    try:
        # Use the pipeline designed for this type of model
        generator = pipeline('text2text-generation', model=model_name)
        print("Model loaded successfully!")
        return generator
    except Exception as e:
        print(f"Error loading model: {e}")
        return None