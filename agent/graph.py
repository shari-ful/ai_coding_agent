from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph
from langgraph.constants import END
from langchain.agents import create_agent
from agent.prompts import planner_prompt, architecture_prompt, code_generation_prompt
from agent.states import Plan, TaskPlan, CoderState
from agent.tools import read_file, write_file, list_files, get_current_directory



load_dotenv()

llm = ChatGroq(model="openai/gpt-oss-120b")


def planner_agent(state: dict) -> dict:
    user_prompt = state["user_prompt"]
    resp = llm.with_structured_output(Plan).invoke(planner_prompt(user_prompt))

    if not resp:
        raise ValueError("Planner agent failed to generate a plan.")

    return {"plan": resp}


def architecture_agent(state: dict) -> dict:
    plan: Plan = state["plan"]
    resp = llm.with_structured_output(TaskPlan).invoke(architecture_prompt(plan=plan.model_dump_json()))

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

