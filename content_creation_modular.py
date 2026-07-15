# content_creation.py

import os
import re
import warnings
from pathlib import Path
from crewai import Task, Agent, Crew
from patch import disable_ssl_verification

# --- 0. Import Custom Tools ---
from tools.post_to_x import PostToX

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
poster_cfg = load_md_content("agent_definitions/social_media_poster.md")
task_cfg = load_md_content("task_definitions/create_shorts_plan.md")

# --- 4. Agent Definitions ---

llm_model = os.getenv("LLM_MODEL", "nvidia/nemotron-3-ultra-550b-a55b")

# Content Creator Agent
content_creator_assistant = Agent(
    role=agent_cfg["role"],
    goal=agent_cfg["goal"],
    backstory=agent_cfg["backstory"],
    llm=llm_model,
    verbose=True
)

# Social Media Poster Agent - can post to X (Twitter)
post_to_x_tool = PostToX()
social_media_poster = Agent(
    role=poster_cfg["role"],
    goal=poster_cfg["goal"],
    backstory=poster_cfg["backstory"],
    llm=llm_model,
    verbose=True,
    tools=[post_to_x_tool]
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

# Separate crew for posting - can be used after content is created
posting_crew = Crew(
    agents=[social_media_poster],
    tasks=[]
)


def run_content_planner():
    """Executes the CrewAI workflow and prints the resulting content plan."""
    print("🚀 Initiating content planning workflow...")
    
    result = content_crew.kickoff()
    
    print("\n" + "=" * 80)
    print("STRATEGIC WEEKLY CONTENT PLAN")
    print("=" * 80)
    print(result.raw)
    
    return result


def post_to_x(content: str) -> str:
    """
    Posts content to X (Twitter) using the post_to_x tool.
    
    Args:
        content: The text content to post to X (Twitter).
        
    Returns:
        str: Result message with tweet URL or error details.
    """
    try:
        # Use the tool directly
        result = post_to_x_tool.run(content)
        return result
    except Exception as e:
        return f"Error posting to X: {str(e)}"


def post_content_to_x(content: str) -> str:
    """
    Alternative method: Posts content to X using the social_media_poster agent.
    
    Args:
        content: The text content to post to X (Twitter).
        
    Returns:
        str: Result message with tweet URL or error details.
    """
    # Create a posting task
    posting_task = Task(
        description=f"Post this content to X (Twitter): {content}",
        expected_output="Confirmation that the content was posted successfully with tweet URL",
        agent=social_media_poster,
        tools=[post_to_x_tool]
    )
    
    # Execute the posting task
    result = posting_crew.kickoff(input=content)
    return result.raw if result else "Error: Failed to post content"


if __name__ == "__main__":
    result = run_content_planner()
    
    # Auto-post to X if enabled via AUTO_POST_TO_X environment variable
    auto_post = os.getenv("AUTO_POST_TO_X", "false").lower() == "true"
    
    if auto_post and result and hasattr(result, 'raw'):
        import json
        try:
            raw_content = result.raw.strip()
            # Try to parse as JSON first
            if raw_content.startswith('{') or raw_content.startswith('['):
                posts_data = json.loads(raw_content)
                # Handle both direct list and object with posts key
                if isinstance(posts_data, dict) and 'posts' in posts_data:
                    posts = posts_data['posts']
                elif isinstance(posts_data, list):
                    posts = posts_data
                else:
                    posts = []
                
                if posts and isinstance(posts, list) and len(posts) > 0:
                    first_post = posts[0]
                    hook = first_post.get('hook_line', '')
                    body = first_post.get('body_text', '')
                    post_text = f"{hook}\n\n{body}".strip()
                    if len(post_text) <= 280:
                        print("\n" + "=" * 80)
                        print("POSTING TO X (TWITTER)")
                        print("=" * 80)
                        post_result = post_to_x(post_text)
                        print(post_result)
            else:
                # If not JSON, use raw content directly (if short enough)
                if len(raw_content) <= 280:
                    print("\n" + "=" * 80)
                    print("POSTING TO X (TWITTER)")
                    print("=" * 80)
                    post_result = post_to_x(raw_content)
                    print(post_result)
        except Exception as e:
            print(f"Could not auto-post: {e}")