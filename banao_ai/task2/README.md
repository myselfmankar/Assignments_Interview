# ATG Technical Assignment: Self-Healing Classification DAG

**Status:** 🟩 **Submission on time. Project implementation in progress.**

**Last Updated:** [Date of your submission]

---

## Task Overview

This project implements a LangGraph-based classification pipeline with a self-healing mechanism. It uses a fine-tuned transformer model to make predictions and incorporates a fallback strategy for low-confidence results, prioritizing correctness and reliability.

---

## Part 1: Fine-Tuned Model (Completed)

The core of this pipeline is a sentiment analysis model fine-tuned for the task.

*   **Base Model:** `distilbert-base-uncased`
*   **Technique:** Parameter-Efficient Fine-Tuning (PEFT) using LoRA. This allows for efficient training by only updating a small fraction of the model's parameters.
*   **Dataset:** `sst2` (Stanford Sentiment Treebank) from the GLUE benchmark.
*   **Hugging Face Hub:** The fine-tuned model adapter is publicly available on the Hugging Face Hub at the following link:
    *   **[myselfmankar/distilbert-base-sst2-lora](https://huggingface.co/myselfmankar/distilbert-base-sst2-lora)** *(<-- Replace with your actual Hub link!)*

---

## Part 2: LangGraph DAG (Implementation in Progress)

The main application logic is being built using LangGraph to create a robust, stateful agent. The code for this will be pushed tonight.

The graph is composed of the following nodes:

1.  **`InferenceNode`**: Loads the fine-tuned model from the Hub and runs the initial classification.
2.  **`ConfidenceCheckNode` (Conditional Edge)**: Evaluates the model's confidence score. If it's above a set threshold (e.g., 90%), the prediction is accepted. If not, it triggers the fallback mechanism.
3.  **`FallbackNode`**: Asks the user for clarification via a command-line interface to ensure the final output is correct.

---

## Deliverables (To be pushed tonight)

*   [x] **Fine-tuned Model:** Available on Hugging Face Hub.
*   [x] **Source Code:** Python scripts for the LangGraph DAG and CLI.
*   [x] **README.md:** This file (will be updated).
*   [x] **Log File:** Example log file from a CLI session.
*   [ ] **Demo Video:** A short video walkthrough.

---