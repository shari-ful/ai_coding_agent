from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph
from langgraph.constants import END
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, SystemMessage
from agent.prompts import planner_prompt, architecture_prompt, code_generation_prompt
from agent.states import Plan, TaskPlan, CoderState, ImplementationTask
from agent.tools import read_file, write_file, list_files, get_current_directory
import json
import re


load_dotenv()

llm = ChatGroq(model="openai/gpt-oss-120b")


def parse_json_from_text(text: str) -> dict:
    """Extract and parse JSON from text response."""
    # Try to find JSON object in the response
    json_match = re.search(r'\{[\s\S]*\}', text)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass
    
    # If no JSON found, raise error
    raise ValueError(f"Could not parse JSON from response: {text[:300]}")


def planner_agent(state: dict) -> dict:
    user_prompt = state["user_prompt"]
    
    messages = [
        SystemMessage(content=planner_prompt(user_prompt)),
        HumanMessage(content="Return your response as a valid JSON object with: name, description, techstack (list), features (list), files (list of objects with path and purpose).")
    ]
    
    response = llm.invoke(messages)
    
    try:
        plan_dict = parse_json_from_text(response.content)
        # Convert files to proper format
        if "files" in plan_dict:
            from agent.states import File
            plan_dict["files"] = [File(**f) if isinstance(f, dict) else f for f in plan_dict["files"]]
        resp = Plan(**plan_dict)
    except Exception as e:
        raise ValueError(f"Planner agent failed to generate valid plan: {str(e)}")

    if not resp:
        raise ValueError("Planner agent failed to generate a plan.")

    return {"plan": resp}


def architecture_agent(state: dict) -> dict:
    plan: Plan = state["plan"]
    
    messages = [
        SystemMessage(content=architecture_prompt(plan=plan.model_dump_json())),
        HumanMessage(content="Return the implementation tasks as a valid JSON object with 'implementation_steps' array. Each step must have 'filepath' and 'task_description'.")
    ]
    
    response = llm.invoke(messages)
    
    try:
        task_plan_dict = parse_json_from_text(response.content)
        # Convert tasks to proper format
        if "implementation_steps" in task_plan_dict:
            task_plan_dict["implementation_steps"] = [
                ImplementationTask(**t) if isinstance(t, dict) else t 
                for t in task_plan_dict["implementation_steps"]
            ]
        resp = TaskPlan(**task_plan_dict)
    except Exception as e:
        raise ValueError(f"Architecture agent failed to parse tasks: {str(e)}")

    if not resp:
        raise ValueError("Architecture agent failed to generate implementation tasks.")

    return {"task_plan": resp}

def code_generation_agent(state: dict) -> dict:
    """LangGraph tool-using coder agent."""
    coder_state: CoderState = state.get("coder_state")
    if coder_state is None:
        coder_state = CoderState(task_plan=state["task_plan"], current_step_idx=0)

    steps = coder_state.task_plan.implementation_steps
    if coder_state.current_step_idx >= len(steps):
        return {"coder_state": coder_state, "status": "DONE"}

    current_task = steps[coder_state.current_step_idx]
    existing_content = read_file.run(current_task.filepath)

    system_prompt = code_generation_prompt()
    user_prompt = (
        f"Task: {current_task.task_description}\n"
        f"File: {current_task.filepath}\n"
        f"Existing content:\n{existing_content}\n"
        "Use write_file(path, content) to save your changes."
    )

    coder_tools = [read_file, write_file, list_files, get_current_directory]
    agent = create_agent(llm, coder_tools)

    agent.invoke({"messages": [{"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_prompt}]})

    coder_state.current_step_idx += 1
    return {"coder_state": coder_state}


graph = StateGraph(dict)
graph.add_node("planner", planner_agent)
graph.add_node("architecture", architecture_agent)
graph.add_node("code_generation", code_generation_agent)

graph.add_edge("planner", "architecture")
graph.add_edge("architecture", "code_generation")
graph.add_conditional_edges("code_generation", lambda s: "END" if s.get("status") == "DONE" else "code_generation", {"END": END, "code_generation": "code_generation"})

graph.set_entry_point("planner")
agent = graph.compile()


if __name__ == "__main__":
    result = agent.invoke({"user_prompt": "Build a colourful modern todo app in html css and js"},
                          {"recursion_limit": 100})
    print("Final State:", result)


