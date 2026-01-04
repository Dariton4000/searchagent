from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

from functions import (
    duckduckgo_search,
    save_knowledge,
    get_all_knowledge,
    crawl4ai,
    create_report,
    get_wikipedia_page,
    context_details,
)
import functions  # leave this import here


ANSI_GREY = "\033[90m"
ANSI_GREEN = "\033[92m"
ANSI_RESET = "\033[0m"


_ENV_TEMPLATE = """# OpenAI API key (required)
OPENAI_API_KEY=

# Optional: model name (default: gpt-5-mini)
OPENAI_MODEL=gpt-5-mini

# Optional: low | medium | high (default: medium)
OPENAI_REASONING_EFFORT=medium

# Optional: custom OpenAI-compatible endpoint (leave blank for default)
OPENAI_BASE_URL=
"""


def _app_dir() -> Path:
    """Directory to store runtime files like .env.

    - When running as a PyInstaller-built exe, this is the exe's folder.
    - When running from source, this is the repository folder containing main.py.
    """

    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def _ensure_env_file(app_dir: Path) -> Path:
    env_path = app_dir / ".env"
    if env_path.exists():
        return env_path

    try:
        env_path.write_text(_ENV_TEMPLATE, encoding="utf-8")
        print(f"Created {env_path}. Set OPENAI_API_KEY, then rerun.")
        # Stop execution immediately so we don't continue with an empty API key.
        sys.exit(1)
    except Exception as e:
        print(f"Failed to create .env at {env_path}: {e}")

    return env_path


def _load_env() -> None:
    # Explicitly load .env from the app directory (works for both source + EXE).
    env_path = _ensure_env_file(_app_dir())
    load_dotenv(dotenv_path=env_path)


def _model_name() -> str:
    return os.environ.get("OPENAI_MODEL", "gpt-5-mini")


def _reasoning_effort() -> str:
    # low | medium | high
    return os.environ.get("OPENAI_REASONING_EFFORT", "medium")


def _client() -> OpenAI:
    # Lazily create client after dotenv load.
    kwargs: dict[str, Any] = {"api_key": os.environ.get("OPENAI_API_KEY")}
    base_url = os.environ.get("OPENAI_BASE_URL")
    if base_url:
        kwargs["base_url"] = base_url
    return OpenAI(**kwargs)


def _tool_schemas() -> list[dict[str, Any]]:
    # Strict mode requires additionalProperties=false and all props required.
    return [
        {
            "type": "function",
            "name": "duckduckgo_search",
            "description": "Search DuckDuckGo for the given query and return crawlable results.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "search_query": {
                        "type": "string",
                        "description": "Search query to run (treat like a Google query).",
                    }
                },
                "required": ["search_query"],
                "additionalProperties": False,
            },
        },
        {
            "type": "function",
            "name": "crawl4ai",
            "description": "Crawl a URL (http/https) and return the page text content as markdown.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to crawl. Must start with http:// or https://",
                    }
                },
                "required": ["url"],
                "additionalProperties": False,
            },
        },
        {
            "type": "function",
            "name": "get_wikipedia_page",
            "description": "Fetch plain-text content for a Wikipedia page title using the Wikipedia API.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "page": {
                        "type": "string",
                        "description": "Exact title of the Wikipedia page.",
                    }
                },
                "required": ["page"],
                "additionalProperties": False,
            },
        },
        {
            "type": "function",
            "name": "save_knowledge",
            "description": "Store a useful research note in the local knowledge base.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "knowledge": {
                        "type": "string",
                        "description": "The knowledge to store.",
                    }
                },
                "required": ["knowledge"],
                "additionalProperties": False,
            },
        },
        {
            "type": "function",
            "name": "get_all_knowledge",
            "description": "Return all stored knowledge base entries.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
                "additionalProperties": False,
            },
        },
        {
            "type": "function",
            "name": "create_report",
            "description": "Generate and save the final markdown report to the reports/ directory.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Report title (also used for filename).",
                    },
                    "content": {
                        "type": "string",
                        "description": "Full report content in markdown.",
                    },
                    "sources": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of sources used in the report.",
                    },
                },
                "required": ["title", "content", "sources"],
                "additionalProperties": False,
            },
        },
    ]


def _call_tool(name: str, args: dict[str, Any]) -> str:
    tool_map = {
        "duckduckgo_search": duckduckgo_search,
        "save_knowledge": save_knowledge,
        "get_all_knowledge": get_all_knowledge,
        "crawl4ai": crawl4ai,
        "create_report": create_report,
        "get_wikipedia_page": get_wikipedia_page,
    }

    fn = tool_map.get(name)
    if fn is None:
        return json.dumps({"error": f"Unknown tool: {name}"})

    try:
        result = fn(**args) if args else fn()
    except Exception as e:
        return json.dumps({"error": f"Tool {name} failed", "details": str(e)})

    if isinstance(result, str):
        return result

    try:
        return json.dumps(result)
    except Exception:
        return str(result)



def _run_responses_agent(
    client: OpenAI,
    *,
    instructions: str,
    input_list: list[dict[str, Any]],
    tools: list[dict[str, Any]],
    model: str,
    reasoning_effort: str,
) -> None:
    """Runs the tool-calling loop until the model returns a normal message (no function calls)."""

    while True:
        response_obj = None

        print()

        stream = client.responses.create(
            model=model,
            instructions=instructions,
            input=input_list,
            tools=tools,
            tool_choice="auto",
            parallel_tool_calls=True,
            reasoning={"effort": reasoning_effort, "summary": "auto"},
            stream=True,
        )

        for event in stream:

            # Reasoning summary streaming.
            if event.type == "response.reasoning_summary_text.delta":
                print(f"{ANSI_GREY}{event.delta}{ANSI_RESET}", end="", flush=True)

            # Reasoning text streaming (non-OpenAI models).
            elif event.type == "response.reasoning_text.delta":
                print(f"{ANSI_GREY}{event.delta}{ANSI_RESET}", end="", flush=True)

            # Main assistant output text.
            elif event.type == "response.output_text.delta":
                print(event.delta, end="", flush=True)

            elif event.type in {"response.completed", "response.incomplete", "response.failed"}:
                response_obj = event.response
                break

            elif event.type == "error":
                raise RuntimeError(str(getattr(event, "error", event)))

        if response_obj is None:
            print("\n(No response received)\n")
            return

        # Show usage.
        usage = getattr(response_obj, "usage", None)
        if usage is not None:
            functions.last_usage = usage.model_dump()
            print()
            context_details()

        status = getattr(response_obj, "status", None)
        if status == "failed":
            err = getattr(response_obj, "error", None)
            print(f"\nResponse failed: {err}\n")
            return

        if status == "incomplete":
            details = getattr(response_obj, "incomplete_details", None)
            print(f"\nResponse incomplete: {details}\n")

        # Persist all output items (reasoning, function_call, messages) into the next turn.
        # Strip output-only fields that the API rejects as input.
        output_items = getattr(response_obj, "output", []) or []
        for item in output_items:
            try:
                d = item.model_dump()
            except Exception:
                d = dict(item) if isinstance(item, dict) else {}
            d.pop("status", None)
            input_list.append(d)

        tool_calls = [item for item in output_items if getattr(item, "type", None) == "function_call"]
        if not tool_calls:
            print()  # newline after assistant answer
            return

        for tc in tool_calls:
            name = getattr(tc, "name", "")
            call_id = getattr(tc, "call_id", "")
            args_str = getattr(tc, "arguments", None) or "{}"

            try:
                args = json.loads(args_str)
            except json.JSONDecodeError:
                args = {}
            if not isinstance(args, dict):
                args = {}

            print(f"\n{ANSI_GREEN}Calling tool:{ANSI_RESET} {name}")
            tool_output = _call_tool(name, args)

            input_list.append({"type": "function_call_output", "call_id": call_id, "output": tool_output})


def researcher(client: OpenAI, query: str) -> None:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    instructions = (
        f"You are a task-focused AI researcher. The current date and time is {now}. "
        "Begin researching immediately. Perform multiple online searches to gather reliable information. "
        "Crawl webpages for context. When possible use Wikipedia as a source. "
        "Research extensively: multiple searches and crawls; one source is not enough. "
        "After crawling a webpage, store any useful knowledge in the research knowledge base (treat it like permanent memory). "
        "Recall all stored knowledge before creating the final report. "
        "Ground information in reliable sources. Mark assumptions clearly. "
        "Produce an extensive report in markdown format using the create_report tool (be sure to call it). "
        "Create the report ONLY when you are done with all research. Already saved reports cannot be changed or deleted. "
        "Add tables when it helps clarity."
    )

    tools = _tool_schemas()
    model = _model_name()
    reasoning_effort = _reasoning_effort()

    input_list: list[dict[str, Any]] = [
        {"role": "user", "content": f"Here is the research query given by the user: '{query}'"}
    ]

    print("Researcher: ", end="", flush=True)
    _run_responses_agent(
        client,
        instructions=instructions,
        input_list=input_list,
        tools=tools,
        model=model,
        reasoning_effort=reasoning_effort,
    )

    while True:
        try:
            user_input = input("You (leave blank to exit): ").strip()
        except EOFError:
            print()
            break

        if not user_input:
            break

        input_list.append({"role": "user", "content": user_input})
        print("Researcher: ", end="", flush=True)
        _run_responses_agent(
            client,
            instructions=instructions,
            input_list=input_list,
            tools=tools,
            model=model,
            reasoning_effort=reasoning_effort,
        )


def main() -> None:
    _load_env()

    if not os.environ.get("OPENAI_API_KEY"):
        env_path = _app_dir() / ".env"
        print(f"OPENAI_API_KEY is not set. Put it in {env_path}, then rerun.")
        return

    knowledge_dir = Path("research_knowledge")
    knowledge_dir.mkdir(exist_ok=True)
    report_dir = Path("reports")
    report_dir.mkdir(exist_ok=True)

    # Deletes all existing knowledge files
    for file in knowledge_dir.glob("*.json"):
        file.unlink()

    research_topic = input("Please provide a research task for the ai researcher: ").strip()
    if not research_topic:
        print("No research task provided. Exiting.")
        return

    researcher(_client(), research_topic)


if __name__ == "__main__":
    main()
