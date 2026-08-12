# CrewAI Content Creation

A CrewAI multi-agent system that plans and publishes social media content in the **Micro-History of Everyday Things** niche — then optionally posts it to X (Twitter).

The workflow generates a 1-day content plan of 5 text-post blueprints (scroll-stopping hooks, narrative twists, and viral CTAs) for text-first networks like LinkedIn, X, and Facebook, and saves each post as JSON, Markdown, and HTML.

## Architecture

```
content_creation_modular.py   # Entry point: env loading, crew assembly, execution
├── agent_definitions/        # Agent prompts (Role / Goal / Backstory) in Markdown
├── task_definitions/         # Task prompt + expected output schema in Markdown
├── tools/
│   └── post_to_x.py          # Custom CrewAI tool posting to X via Tweepy (OAuth 1.0a)
└── patch.py                  # Disables SSL verification for constrained/proxy environments
```

### Agents

| Agent | Source | Tools |
|---|---|---|
| Micro-History Strategist | `agent_definitions/micro_history_strategist.md` | — |
| Social Media Poster | `agent_definitions/social_media_poster.md` | `post_to_x` |

### Flow

1. `content_creation_modular.py` loads agent/task definitions from the Markdown config files.
2. The **content crew** runs the Micro-History Strategist against `create_shorts_plan.md`, which asks for a JSON array of 5 post blueprints.
3. Results are parsed (dict, list, or JSON string) and written to `output/post_N.{json,md,html}`.
4. If `AUTO_POST_TO_X=true`, the first post is auto-posted to X through the `PostToX` tool (requires the four X API credentials in `.env`).

## Setup

Requires Python >= 3.11 and [uv](https://docs.astral.sh/uv/).

```bash
uv venv .venv
source .venv/bin/activate
uv sync
```

## Configuration

Copy `example.env` to `.env` and fill in the values:

```bash
cp example.env .env
```

| Variable | Description |
|---|---|
| `OPENAI_API_BASE` | LLM API base URL (e.g. OpenRouter: `https://openrouter.ai/api/v1`) |
| `LLM_MODEL` | Model identifier, e.g. `nvidia/nemotron-3-ultra-550b-a55b` |
| `OPENROUTER_API_KEY` | API key for the LLM provider |
| `X_API_KEY`, `X_API_SECRET` | X (Twitter) API key + secret (developer portal → Keys and tokens) |
| `X_ACCESS_TOKEN`, `X_ACCESS_TOKEN_SECRET` | X OAuth 1.0a access token + secret (Read + Write permission) |
| `AUTO_POST_TO_X` | `true`/`false` — auto-post the first blueprint after generation |

Get X credentials at <https://developer.x.com/en/portal/dashboard> (OAuth 1.0a User Context, Read + Write).

## Usage

```bash
python content_creation_modular.py
```

Outputs:

- The full content plan printed to stdout.
- Per-post files in `output/`:
  - `post_N.json` — structured post data
  - `post_N.md` — plain text post copy
  - `post_N.html` — minimal HTML rendering of the post

Programmatic use:

```python
from content_creation_modular import post_to_x, post_content_to_x

post_to_x("Hello from CrewAI")        # post directly via the tool
post_content_to_x("Hello from CrewAI") # post via the poster agent crew
```

## Security notes

- Secrets live only in `.env` (git-ignored); `example.env` contains placeholders.
- `patch.py` globally disables SSL verification (`verify=False` on `requests`, `httpx`, and the OpenAI client). It exists for constrained proxy/test environments — **do not** use it in production or with untrusted networks, as it enables man-in-the-middle attacks.
