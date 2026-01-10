from langgraph.graph import StateGraph, END

from src.agents.auditor import auditor_agent
from src.agents.fixer import fixer_agent
from src.agents.judge import judge_agent

def should_continue(state: dict) -> str: # a function to decide whether we should stop the loop or no
    # If all tests passed,stop the loop 
    if state.get("judge_verdict") == "PASS":
        return END

    # if the number of iterations exceeds 10, stop the loop
    if state["iteration"] >= 10:
        state["judge_verdict"] = "FAIL (max iterations reached)"
        return END

    # else we continue the fix
    return "fixer"


def build_workflow(): # builds and returns the langGraph workflow
    graph = StateGraph(dict) # create a state graph, the state is a python dictionnary (dict)

    # adding agents nodes to the graph
    graph.add_node("auditor", auditor_agent)
    graph.add_node("fixer", fixer_agent)
    graph.add_node("judge", judge_agent)

    # building the flow of the graph
    graph.set_entry_point("auditor")
    graph.add_edge("auditor", "fixer")
    graph.add_edge("fixer", "judge")

    # judge decides whether to go back to fixer or end the loop using should-continue
    graph.add_conditional_edges(
        "judge",
        should_continue,
        {
            "fixer": "fixer",
            END: END
        }
    )

    return graph.compile()
