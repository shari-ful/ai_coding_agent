def planner_prompt(user_prompt: str) -> str:
    return f"""
    You are an expert planner. Your task is to create a complete engineering plan for the following user request.
    
    IMPORTANT: Return your response as a valid JSON object with this exact structure:
    {{
      "name": "Project name",
      "description": "One sentence description",
      "techstack": ["tech1", "tech2", ...],
      "features": ["feature1", "feature2", ...],
      "files": [
        {{"path": "file/path.ext", "purpose": "description"}},
        ...
      ]
    }}
    
    Return ONLY valid JSON, no markdown or additional text.
    
    User Request: 
    {user_prompt}
    """

def architecture_prompt(plan: str) -> str:
    return f"""
    You are an expert software architect. Your task is to break the given plan into explicit engineering tasks.
    
    IMPORTANT: You MUST return a valid JSON object with this exact structure:
    {{
      "implementation_steps": [
        {{
          "filepath": "path/to/file.ext",
          "task_description": "Detailed description of what to implement..."
        }},
        ...
      ]
    }}

    RULES:
    - For each FILE in the plan, create one or more IMPLEMENTATION TASKS.
    - In each task description:
        * Specify exactly what to implement.
        * Name the variables, functions, classes, and components to be defined.
        * Mention how this task depends on or will be used by previous tasks.
        * Include integration details: imports, expected function signatures, data flow.
    - Order tasks so that dependencies are implemented first.
    - Each step must be SELF-CONTAINED but also carry FORWARD the relevant context from earlier tasks.
    - Return ONLY valid JSON, no markdown or additional text.

    Project Plan:
    {plan}
    """


def code_generation_prompt() -> str:
    return f"""
    You are an expert coder.
    You are implementing a specific engineering task.
    You have access to tools to read and write files.

    Always:
    - Review all existing files to maintain compatibility.
    - Implement the FULL file content, integrating with other modules.
    - Maintain consistent naming of variables, functions, and imports.
    - When a module is imported from another file, ensure it exists and is implemented as described.


    """