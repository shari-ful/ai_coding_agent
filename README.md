# AI Coding Agent

An intelligent, multi-agent system that automatically generates complete software projects from natural language descriptions. Built with **LangGraph** and **Groq LLM**, this agent orchestrates multiple specialized agents to plan, architect, and implement entire projects.

## Overview

The AI Coding Agent takes a simple user prompt describing what you want to build and automatically:
1. **Plans** the project structure and architecture
2. **Designs** the implementation strategy and file organization
3. **Generates** complete, working code with all necessary files

This is perfect for rapidly prototyping applications, exploring ideas, or automating boilerplate code generation.

## Features

- 🤖 **Multi-Agent System**: Three specialized agents work together in a coordinated workflow
- 📋 **Intelligent Planning**: Creates comprehensive project plans from natural language descriptions
- 🏗️ **Architecture Design**: Breaks down projects into clear, manageable implementation tasks
- 💻 **Code Generation**: Generates complete, working code files with proper dependencies and integrations
- 🔄 **Iterative Execution**: Implements tasks sequentially while maintaining context and consistency
- 🛡️ **Project Isolation**: All generated code is safely contained in a dedicated `generated_project/` directory
- 📝 **Structured Output**: Leverages Pydantic models for reliable, type-safe data structures

## Architecture

The agent uses a **LangGraph state machine** with three main nodes:

```
User Prompt
    ↓
┌─────────────────────┐
│  Planner Agent      │  Creates high-level project plan
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│ Architecture Agent   │  Breaks plan into implementation tasks
└──────────┬──────────┘
           ↓
┌─────────────────────┐
│   Coder Agent       │  Implements tasks iteratively
│  (with file tools)  │
└──────────┬──────────┘
           ↓
     Generated Project
```

### Agent Workflow

1. **Planner Agent**: Analyzes the user prompt and generates a structured `Plan` containing:
   - Project name and description
   - Technology stack
   - Key features
   - File structure

2. **Architecture Agent**: Converts the plan into a `TaskPlan` with:
   - List of implementation tasks with dependencies
   - Detailed descriptions for each task
   - Proper ordering to handle dependencies first

3. **Code Generation Agent**: Executes implementation tasks iteratively:
   - Reads existing file content
   - Generates/modifies files based on task descriptions
   - Uses file management tools to write code
   - Maintains context across all tasks

## Installation

### Prerequisites
- Python 3.12 or higher
- A Groq API key (get one at [console.groq.com](https://console.groq.com))

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai_coding_agent
   ```

2. **Create a `.env` file** in the root directory with your Groq API key:
   ```bash
   echo "GROQ_API_KEY=your_api_key_here" > .env
   ```

3. **Install dependencies** using uv (or pip):
   ```bash
   uv pip install -e .
   # or
   pip install -e .
   ```

## Usage

### Running the Agent

Start the agent with an interactive prompt:

```bash
uv run main.py
```

You'll be prompted to enter your project description:

```
Enter your project prompt: Build a colorful modern todo app in HTML, CSS, and JavaScript
```

### Command-Line Options

```bash
uv run main.py --recursion-limit 100
```

- `--recursion-limit, -r`: Maximum recursion depth for processing (default: 100)

### Example Prompts

- `"Build a todo app with HTML, CSS, and JavaScript"`
- `"Create a Python CLI tool for managing tasks with SQLite database"`
- `"Build a REST API for a note-taking application using Flask"`

### Output

Generated code will be created in the `generated_project/` directory with a complete, working project structure.

## Project Structure

```
ai_coding_agent/
├── main.py                 # Entry point with CLI
├── pyproject.toml         # Project dependencies and metadata
├── README.md              # This file
├── .env                   # Groq API key (create this)
├── generated_project/     # Output directory (auto-created)
└── agent/
    ├── __init__.py
    ├── graph.py           # LangGraph workflow definition
    ├── prompts.py         # Prompt templates for agents
    ├── states.py          # Pydantic data models
    └── tools.py           # File management tools
```

## Dependencies

- **langchain** (≥1.2.18): LLM framework
- **langchain-groq** (≥1.1.2): Groq integration
- **langgraph** (≥1.1.10): Graph-based agent orchestration
- **groq** (<1): Groq API client
- **python-dotenv** (≥1.2.2): Environment variable management

## Data Models

### Plan
The planner agent outputs:
```python
- name: str              # Project name
- description: str       # One-sentence description
- techstack: list[str]  # Technologies used
- features: list[str]   # Key features
- files: list[File]     # Files to create
```

### TaskPlan
The architecture agent outputs:
```python
- implementation_steps: list[ImplementationTask]
```

Each task contains:
```python
- filepath: str         # File path
- task_description: str # Detailed task description
```

### CoderState
Tracks code generation progress:
```python
- task_plan: TaskPlan        # The implementation plan
- current_step_idx: int      # Current task index
- current_file_content: str  # Content being edited
```

## Key Components

### graph.py
- **planner_agent()**: Generates project plan using LLM
- **architecture_agent()**: Breaks plan into implementation tasks
- **code_generation_agent()**: Implements tasks iteratively with file tools
- **agent**: Compiled LangGraph workflow

### tools.py
File management utilities:
- `read_file()`: Read file content
- `write_file()`: Create/modify files
- `list_files()`: List directory contents
- `get_current_directory()`: Get project root

### prompts.py
System prompts for each agent:
- `planner_prompt()`: Planning instructions
- `architecture_prompt()`: Task breakdown instructions
- `code_generation_prompt()`: Code generation instructions

### states.py
Pydantic models defining agent data structures:
- `File`: File definition with path and purpose
- `Plan`: Complete project plan
- `ImplementationTask`: Single implementation task
- `TaskPlan`: All implementation tasks
- `CoderState`: Code generation state

## Configuration

### LLM Model
The agent uses `openai/gpt-oss-120b` via Groq. To change the model, edit [agent/graph.py](agent/graph.py):

```python
llm = ChatGroq(model="your-model-name")
```

### Recursion Limit
Control how many times the coder agent iterates:
```bash
uv run main.py --recursion-limit 50
```

## How It Works

1. **User Input**: You describe what you want to build
2. **Planning Phase**: The planner agent structures the project
3. **Architecture Phase**: The architecture agent creates detailed implementation tasks
4. **Implementation Phase**: The coder agent iteratively implements each task using file tools
5. **Output**: Complete project files appear in `generated_project/`

Each phase builds on the previous one, maintaining context and ensuring generated code is cohesive and integrated.

## Troubleshooting

### `Error: GROQ_API_KEY not set`
Make sure you've created a `.env` file with your API key:
```bash
echo "GROQ_API_KEY=your_key_here" > .env
```

### `Recursion limit exceeded`
Increase the recursion limit:
```bash
uv run main.py --recursion-limit 200
```

### Complex projects failing
Break down complex requests into simpler steps. For example, build a basic version first, then enhance it.

## Future Enhancements

- Support for multiple LLM providers
- Code validation and testing
- Interactive refinement and editing
- Project templates and starters
- Multi-file dependency analysis
- Code quality metrics

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]
