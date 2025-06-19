# Local Command-Line Chatbot

A simple, robust command-line chatbot built in Python using the Hugging Face library. This project demonstrates a modular architecture, conversational memory management, and practical prompt engineering.

## Features

-   **Local & Fast:** Runs entirely on a standard local machine (CPU).
-   **Conversational Memory:** Remembers the last 3 turns of the conversation using a sliding window.
-   **Modular Code:** Organized into separate, clear modules for model loading, memory, and the interface.
-   **Factual Q&A:** Provides coherent, fact-based answers using a carefully selected model and prompt strategy.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/myselfmankar/Assignments_Interview/banao_ai.git
    cd task1
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## How to Run

From your terminal, simply run the `interface.py` script:

```bash
python interface.py
```
The first time you run it, the model (~990 MB) will be downloaded. After that, it will load directly from your cache. To quit, type `/exit`.

## Example Interaction

```
$ python interface.py
Loading model 'google/flan-t5-base'... This may take a moment.
Model loaded successfully!

Chatbot is ready! Type '/exit' to end the conversation.
---------------------------------------------------------
User: What is the capital of France?
Bot: Paris
User: What language do they speak there?
Bot: French
User: /exit
Exiting chatbot. Goodbye!
```

## Design Decisions

-   **Model Choice:** `google/flan-t5-base` was chosen as a practical balance between a reasonable local size (~1GB) and strong factual accuracy. Smaller models were tested but proved too unreliable for coherent Q&A.
-   **Prompt Engineering:** The chatbot formats the conversation history into a clear `context: ... question: ...` structure. This is a crucial step that instructs the Flan-T5 model to perform question-answering, leading to much more accurate results.