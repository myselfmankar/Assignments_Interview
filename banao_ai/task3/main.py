import logging
import os
from graph_setup import build_graph, GraphState, judge_node
from langgraph.graph import END


# --- Logging Setup ---
# This will log all state transitions and messages to a file as required
log_directory = "logs"
os.makedirs(log_directory, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_directory, "debate_log.txt"),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='w' # 'w' overwrites the log file on each run
)

def main():
    if not os.getenv("GOOGLE_API_KEY"):
        print("ERROR: GOOGLE_API_KEY environment variable not set.")
        return

    graph = build_graph()

    print("--- Multi-Agent Debate Simulation ---")
    topic = input("Enter the topic for the debate (or press Enter for default): ")
    if not topic:
        topic = "Should AI be regulated as strictly as medicine?"
    
    print(f"\nStarting debate on: '{topic}'...")
    logging.info(f"Debate Topic: {topic}")
    
    initial_state = {
        "topic": topic, "messages": [], "round_number": 0,
        "next_speaker": "Scientist", "winner": "", "summary": ""
    }

    final_state = None
    for i, step in enumerate(graph.stream(initial_state, {"recursion_limit": 15})):
        node_name, output = list(step.items())[0]
        
        logging.info(f"--- Transition {i}: Node '{node_name}' ---")
        logging.info(f"Output: {output}")

        if "messages" in output and output["messages"]:
            last_message = output["messages"][-1]
            print(f"\n[Round {output['round_number']}]\n {last_message.name}: {last_message.content}")
        
        if node_name == "judge_node":
            final_state = output
            logging.info(f"\n--- Final Judgement Received ---\n {final_state}")
            

    if final_state:
        print("\n\n--- DEBATE FINISHED ---")
        print(f"[Judge] Summary of debate:\n{final_state.get('summary', 'N/A')}")
        print(f"\n[Judge] Winner: {final_state.get('winner', 'N/A')}")
        print(f"[Judge] Reason: {final_state.get('justification', 'N/A')}")

        logging.info("--- FINAL VERDICT ---")
        logging.info(f"Summary: {final_state.get('summary', 'N/A')}")
        logging.info(f"Winner: {final_state.get('winner', 'N/A')}")
        logging.info(f"Justification: {final_state.get('justification', 'N/A')}")

    # try:
    #     diagram_bytes = graph.get_graph().draw_mermaid_png()
    #     with open("dag_diagram.png", "wb") as f:
    #         f.write(diagram_bytes)
    #     print("\nDAG diagram saved to dag_diagram.png")
    # except Exception as e:
    #     print(f"\nCould not generate diagram: {e}. Check pygraphviz installation.")

if __name__ == "__main__":
    main()