from typing import List, TypedDict, Annotated, Sequence
import operator
from functools import partial
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage 
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END

from prompts import (
    scientist_system_prompt,
    philosopher_system_prompt,
    agent_human_prompt,
    judge_system_prompt,
    judge_human_prompt,
)

from dotenv import load_dotenv
load_dotenv()


class GraphState(TypedDict):
    topic: str
    messages: Annotated[List[BaseMessage], operator.add]
    round_number: int
    next_speaker: str
    winner: str
    summary: str
    justification: str


def format_history(messages: List[BaseMessage]) -> str:
    history = []
    for msg in messages:
        history.append(f"[{msg.name}]: {msg.content}")
    return "\n".join(history) if history else "Debat not stated yet."


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.5,
)

def agent_node(state: GraphState, system_prompt: str, name: str) -> dict:
    """Node for the Scientist or Philosopher agent."""
    history = format_history(state["messages"])
    human_prompt = agent_human_prompt.format(topic=state["topic"], history=history)

    message_list = [SystemMessage(content=system_prompt), HumanMessage(content=human_prompt)]

    print(f"---calling {name}---")
    response = llm.invoke(message_list)
    
    message = HumanMessage(content=response.content, name=name)
    next_speaker = "Philosopher" if name == "Scientist" else "Scientist"
    round_number = state["round_number"] + 1

    return {
        "messages": [message],
        "round_number": round_number,
        "next_speaker": next_speaker
    }

def judge_node(state: GraphState) -> dict:
    """Node for the Judge agent."""
    history = format_history(state["messages"])
    human_prompt = judge_human_prompt.format(topic=state["topic"], history=history)
    
    message_list = [SystemMessage(content=judge_system_prompt), HumanMessage(content=human_prompt)]
    
    print("--- Calling Judge ---")
    response = llm.invoke(message_list)
    
    try:
        content_after_summary_label = response.content.split("Summary of debate:")[1]
        summary = content_after_summary_label.split("Winner:")[0].strip()
        content_after_winner_label = content_after_summary_label.split("Winner:")[1]
        winner = content_after_winner_label.split("Reason:")[0].strip()
        justification = content_after_winner_label.split("Reason:")[1].strip()
    except IndexError:
        summary, winner, justification, verdict_part = "Parsing Error", "Error", "Error", response.content
    
    return {"summary": summary, "winner": winner, "justification": justification}



def router(state: GraphState) -> str:
    """Router to determine the next speaker based on the round number."""
    if state["round_number"] >= 8:
        return "judge_node"
    return state["next_speaker"]


def build_graph() -> StateGraph:
    """Build the debate graph with Scientist, Philosopher, and Judge nodes."""
    workflow = StateGraph(GraphState)
    scientist_node_partial = partial(agent_node, system_prompt=scientist_system_prompt, name="Scientist")
    philosopher_node_partial = partial(agent_node, system_prompt=philosopher_system_prompt, name="Philosopher")
    
    workflow.add_node("Scientist", scientist_node_partial)
    workflow.add_node("Philosopher", philosopher_node_partial)
    workflow.add_node("judge_node", judge_node)
    
    workflow.set_entry_point("Scientist")
    
    workflow.add_conditional_edges("Scientist", router, {"Philosopher": "Philosopher", "judge_node": "judge_node"})
    workflow.add_conditional_edges("Philosopher", router, {"Scientist": "Scientist", "judge_node": "judge_node"})
    workflow.add_edge("judge_node", END)
    
    return workflow.compile()

