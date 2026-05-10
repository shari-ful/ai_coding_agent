from pathlib import Path
from langchain_core.tools import tool
import subprocess


PROJECT_ROOT = Path.cwd() / "generated_project"

def path_for_generated_project(path: str) -> str:
    """Returns the root path of generated project."""
    project_path = (PROJECT_ROOT / path).resolve()
    if PROJECT_ROOT.resolve() not in project_path.parents and PROJECT_ROOT.resolve() != project_path.parent and PROJECT_ROOT.resolve() != project_path:
        raise ValueError("Attempt to write outside project root")
    return project_path

def init_project_root():
    """Initializes the project root directory."""
    PROJECT_ROOT.mkdir(parents=True, exist_ok=True)


@tool
def get_current_directory() -> str:
    """Returns the current working directory."""
    return str(PROJECT_ROOT)

@tool
def read_file(file_path: str) -> str:
    """Reads the content of a file and returns it as a string."""
    path = path_for_generated_project(file_path)
    if not path.exists():
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
    
@tool
def write_file(file_path: str, content: str) -> str:
    """Writes the given content to a file."""
    path = path_for_generated_project(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"File '{file_path}' written successfully."

@tool
def list_files(directory: str) -> str:
    """Lists all files in the given directory."""
    path = path_for_generated_project(directory)
    if not path.exists() or not path.is_dir():
        return f"Directory '{directory}' does not exist."
    files = [str(p.relative_to(PROJECT_ROOT)) for p in path.rglob("*") if p.is_file()]
    return "\n".join(files)

@tool
def run_command(command: str, cwd: str = None, timeout: int = 30) -> str:
    """Runs a shell command and returns its output."""
    cwd_path = path_for_generated_project(cwd) if cwd else PROJECT_ROOT
    result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=cwd_path, timeout=timeout)
    if result.returncode != 0:
        return f"Error running command: {result.stderr}"
    return result.returncode, result.stdout, result.stderr