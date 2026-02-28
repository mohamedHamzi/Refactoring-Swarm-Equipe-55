
from typing import TypedDict, Annotated, List, Dict, Any
from langgraph.graph import StateGraph, END
import operator
import os

from src.agents.auditor import AuditorAgent
from src.agents.fixer import FixerAgent
from src.agents.judge import JudgeAgent
from src.utils.logger import log_experiment, ActionType
from src.config import DEFAULT_MODEL_NAME


# Define the state of the graph
class AgentState(TypedDict):
    target_file: str
    current_code: str
    refactoring_plan: str
    pylint_score: float
    test_results: Dict[str, Any]
    iterations: int
    max_iterations: int
    error_context: str
    status: str

# Node Functions 
def auditor_node(state: AgentState, model_name: str = DEFAULT_MODEL_NAME):
    print(f"--- Auditor Node: {state['target_file']} ---")
    auditor = AuditorAgent(model_name=model_name)
    result = auditor.analyze(state['target_file'], iteration=state.get("iterations", 0))
    
    return {
        "refactoring_plan": result['plan'],
        "pylint_score": result['pylint_score'],
        "current_code": result['original_code'],
        "error_context": None  # Reset error context on fresh analysis/plan
    }

def fixer_node(state: AgentState, model_name: str = DEFAULT_MODEL_NAME):
    iteration = state["iterations"] + 1
    print(f"--- Fixer Node: Iteration {iteration} ---")
    fixer = FixerAgent(model_name=model_name)
    error_ctx = state.get("error_context")
    
    fixed_code = fixer.fix(
        state['target_file'], 
        state['current_code'], 
        state['refactoring_plan'],
        error_context=error_ctx,
        iteration=iteration
    )
    
    return {
        "current_code": fixed_code,
        "iterations": iteration
    }

def judge_node(state: AgentState):
    print("--- Judge Node ---")
    judge = JudgeAgent()
    target_dir = os.path.dirname(state['target_file'])
    results = judge.evaluate(target_dir, iteration=state.get("iterations", 0))
    
    # Determine status — environment errors get special treatment
    error_type = results.get("error_type")
    if results['success']:
        status = "SUCCESS"
    elif error_type == "ENVIRONMENT_ERROR":
        status = "ENVIRONMENT_ERROR"
    elif error_type == "TIMEOUT":
        status = "ENVIRONMENT_ERROR"
    else:
        status = "FAILURE"
    
    return {
        "test_results": results,
        "status": status,
        "error_context": results['output'] if not results['success'] else None
    }

# Edge Logic
def check_status(state: AgentState):
    if state['status'] == "SUCCESS":
        return "end"
    
    # Stop immediately on environment errors — retrying won't help
    if state['status'] == "ENVIRONMENT_ERROR":
        print("⚠️ Environment error detected. Stopping loop — retrying won't fix infrastructure issues.")
        return "end"
    
    if state['iterations'] >= state['max_iterations']:
        print("Max iterations reached. Stopping.")
        return "end"
        
    return "fix_again"

# Graph Construction
def create_graph(model_name: str = DEFAULT_MODEL_NAME):
    workflow = StateGraph(AgentState)
    
    from functools import partial
    
    workflow.add_node("auditor", partial(auditor_node, model_name=model_name))
    workflow.add_node("fixer", partial(fixer_node, model_name=model_name))
    workflow.add_node("judge", judge_node)
    
    workflow.set_entry_point("auditor")
    
    workflow.add_edge("auditor", "fixer")
    workflow.add_edge("fixer", "judge")
    
    workflow.add_conditional_edges(
        "judge",
        check_status,
        {
            "end": END,
            "fix_again": "fixer"  # Loop back to fixer with error context
        }
    )
    
    return workflow.compile()
