# modular_versions/content_creation

## What’s in this module
Modular, configuration-driven version of the **Social Media Shorts content planning** workflow.

### Program: `content_creation_modular.py`
This script:
- Loads **Agent** and **Task** prompts from markdown files in:
  - `agent_definitions/`
  - `task_definitions/`
- Builds a CrewAI workflow and runs it to generate a content plan.

#### Run
From the repository root:

```bash
python content_creation_modular.py
```

#### Output
Prints the resulting plan to stdout.

#### Notes
- Expects an appropriate `.env` (handled in `utils.py`).
- Uses `patch.py` to disable SSL verification in constrained environments.

## Resources
- [Understanding AI Agent Workflows](https://www.coursera.org/learn/design-develop-and-deploy-multi-agent-systems-with-crewai/lecture/4QpBD/understanding-ai-agent-workflows)
- [Google Scraper API](https://serper.dev/logs) - Best way to scrape search engine results with an easy-to-use API

## Setup

```bash
uv venv .venv
source .venv/bin/activate
uv init

uv add crewai 
uv add 'crewai[litellm]'
uv add patch

uv add tools crewai_tools exa_py dill
uv pip install dlai-grader

uv pip freeze > requirements.txt
uv pip install -r requirements.txt
```

