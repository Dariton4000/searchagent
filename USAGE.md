# Example Usage Guide

This guide shows you how to use the refactored AI Research Agent with OpenAI's GPT-5-mini.

## Quick Start

### 1. Set your OpenAI API Key

**Windows (Command Prompt):**
```cmd
set OPENAI_API_KEY=sk-your-api-key-here
```

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="sk-your-api-key-here"
```

**Linux/Mac:**
```bash
export OPENAI_API_KEY=sk-your-api-key-here
```

### 2. Run the Agent

```bash
# Windows
start.bat

# Or directly
python main.py
```

### 3. Enter your research query

When prompted, enter a research topic, for example:
- "What are the latest developments in quantum computing?"
- "Explain the impact of climate change on polar ice caps"
- "History of the Python programming language"

## How It Works

The agent will:
1. **Search** the web using DuckDuckGo
2. **Crawl** relevant webpages for detailed information
3. **Store** important findings in a knowledge base
4. **Retrieve** information from Wikipedia when appropriate
5. **Generate** a comprehensive report in markdown format

## Features

### Reasoning Model with Extended Thinking
GPT-5-mini is an advanced reasoning model that:
- Thinks through complex queries step-by-step with visible reasoning process
- Provides well-structured and logical responses
- Considers multiple sources before drawing conclusions
- Displays its internal reasoning in real-time (shown in gray text)
- Saves reasoning summaries automatically for later review

### Reasoning Summaries
The agent automatically:
- Captures all reasoning steps during research
- Saves summaries to `research_knowledge/reasoning_summaries.json`
- Provides a summary count at the end of each research session
- Allows you to review the model's thought process

### Tool Calling
The agent has access to these tools:
- `duckduckgo_search`: Web search capability
- `save_knowledge`: Store research findings
- `get_all_knowledge`: Retrieve stored findings
- `crawl4ai`: Crawl and extract webpage content
- `get_wikipedia_page`: Fetch Wikipedia articles
- `create_report`: Generate final research report

### Interactive Mode
After completing the initial research, you can:
- Ask follow-up questions
- Request clarifications
- Explore related topics
- Leave blank input to exit
- All interactions benefit from the model's reasoning capabilities

## Example Session

```
Please provide a research task for the ai researcher: What is machine learning?

Bot: [Reasoning shown in gray] Analyzing the query about machine learning...
Let me research that for you...

[Calling: duckduckgo_search]
[Calling: crawl4ai]
[Calling: save_knowledge]
[Calling: get_wikipedia_page]
[Calling: create_report]

==================================================
Reasoning Summary: 5 reasoning step(s) completed
==================================================

Report saved to reports/Machine_Learning_Overview_20250102_143052.md

You (leave blank to exit): How is it different from AI?

Bot: [Reasoning shown in gray] Considering the relationship between ML and AI...
Let me explain the differences...
```

## Output

Research reports are saved in the `reports/` directory as markdown files with:
- Comprehensive content
- Tables and structured information
- Source citations

Reasoning summaries are saved in `research_knowledge/reasoning_summaries.json` with:
- Timestamp for each reasoning step
- Full reasoning content
- Iteration tracking
- Timestamped filenames

## Troubleshooting

### API Key Issues
- Ensure your API key is set in the environment
- Check that the key has sufficient credits
- Verify the key is valid (starts with `sk-`)

### Connection Errors
- Check your internet connection
- Verify you can access openai.com
- Check for firewall/proxy issues

### Missing Dependencies
Run the installation script again:
```bash
install.bat
```

## Notes

- The agent will make multiple searches and web crawls for thorough research
- Longer queries may take more time and API credits
- Reports cannot be edited after creation (start a new research session instead)
- Knowledge base is cleared at the start of each session
