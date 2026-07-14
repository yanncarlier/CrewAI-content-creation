# content_creation.py

import os
import re
import warnings
from pathlib import Path
from crewai import Task, Agent, Crew
from patch import disable_ssl_verification

# --- 1. Environment Configuration ---

disable_ssl_verification()
warnings.filterwarnings('ignore')

os.environ["CREWAI_TESTING"] = "true"

# Load .env (prefer python-dotenv if available), fallback to a simple parser
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    env_path = Path('.env')
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

# --- 2. Helper Function to Load MD Content ---

def load_md_content(file_path):
    """Parses MD files to extract labeled sections for Agents and Tasks."""
    content = Path(file_path).read_text()
    
    def extract_section(label, text):
        # Matches content after **Label:** until the next double newline or end of file
        pattern = rf"\*\*{label}:\*\*\s*([\s\S]*?)(?=\n\n\*\*|\Z)"
        match = re.search(pattern, text)
        return match.group(1).strip() if match else ""

    return {
        "role": extract_section("Role", content),
        "goal": extract_section("Goal", content),
        "backstory": extract_section("Backstory", content),
        "description": extract_section("Description", content),
        "expected_output": extract_section("Expected Output", content)
    }

# --- 3. Resource Loading ---

agent_cfg = load_md_content("agent_definitions/micro_history_strategist.md")
task_cfg = load_md_content("task_definitions/create_shorts_plan.md")

# --- 4. Agent Definition ---

llm_model = os.getenv("LLM_MODEL", "nvidia/nemotron-3-ultra-550b-a55b")

content_creator_assistant = Agent(
    role=agent_cfg["role"],
    goal=agent_cfg["goal"],
    backstory=agent_cfg["backstory"],
    llm=llm_model,
    verbose=True
)

# --- 5. Task Definition ---

task = Task(
    description=task_cfg["description"],
    expected_output=task_cfg["expected_output"],
    agent=content_creator_assistant
)

# --- 6. Crew Assembly and Execution ---

content_crew = Crew(
    agents=[content_creator_assistant],
    tasks=[task]
)

def run_content_planner():
    """Executes the CrewAI workflow and prints the resulting content plan."""
    print("🚀 Initiating content planning workflow...")
    
    result = content_crew.kickoff()
    
    print("\n" + "=" * 80)
    print("STRATEGIC WEEKLY CONTENT PLAN")
    print("=" * 80)
    print(result.raw)

if __name__ == "__main__":
    run_content_planner()