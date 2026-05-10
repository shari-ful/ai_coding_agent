from pydantic import BaseModel, Field, ConfigDict


class File(BaseModel):
    path: str = Field(description="The file path to be created or modified, including the file name and extension.")
    purpose: str = Field(description="The main purpose of the file. e.g: data processing, model definition, API route, etc.")


class Plan(BaseModel):
    name: str = Field(description="A unique name for the app to be built")
    description: str = Field(description="A single sentence description of the app to be built.")
    techstack: list[str] = Field(description="A list of technologies, frameworks, and libraries that will be used in the implementation of the engineering plan.")
    features: list[str] = Field(description="A list of key features or functionalities that the app should have.")
    files: list[File] = Field(description="A list of files that need to be created or modified")

class ImplementationTask(BaseModel):
    filepath: str = Field(description="The path to the file to be modified")
    task_description: str = Field(description="A detailed description of the task to be performed on the file, e.g. 'add user authentication', 'implement data processing logic', etc.")

class TaskPlan(BaseModel):
    implementation_steps: list[ImplementationTask] = Field(description="A list of steps to be taken to implement the task")
    model_config = ConfigDict(extra="allow")
    
class CoderState(BaseModel):
    task_plan: TaskPlan = Field(description="The plan for the task to be implemented")
    current_step_idx: int = Field(0, description="The index of the current step in the implementation steps")
    current_file_content: str | None = Field(None, description="The content of the file currently being edited or created")