# AI Research Agent

A sophisticated AI-powered research agent that leverages OpenAI's Responses API to conduct in-depth research, web searches, and generate comprehensive reports. Built with Python and designed for deployment as a standalone executable.

## Features

- **OpenAI Responses API Integration**: Uses cutting-edge OpenAI Responses API with tool-calling support for intelligent research automation
- **Web Search & Crawling**: Integrates DuckDuckGo for web searching and Crawl4AI for efficient webpage extraction
- **Wikipedia Integration**: Direct access to Wikipedia articles via the official Wikipedia API
- **Persistent Knowledge Base**: Stores and retrieves research findings in a local JSON-based knowledge base for continuous learning
- **Markdown Report Generation**: Creates well-formatted, source-cited reports automatically
- **Multi-turn Conversations**: Interactive follow-up questions during research sessions
- **Token Usage Tracking**: Monitors OpenAI API token consumption (input, output, and total)
- **Async Web Crawling**: Non-blocking web crawling with caching capabilities
- **Parallel Tool Calls**: Supports concurrent function execution for faster research
- **Reasoning Summaries**: Displays AI reasoning process with configurable effort levels (low, medium, high)

## Installation

**uv** is a fast Python package and project manager. If you don’t already have it installed, follow the official installation guide: https://docs.astral.sh/uv/getting-started/installation/

1. Run the installation script (Windows):

```bash
install.bat
```

This will:
- Create a Python 3.11 virtual environment using **uv**
- Install all dependencies from `requirements.txt`
- Set up Crawl4AI browser components (Playwright/Patchright)

## Usage

### Running the Agent

Start the research agent:
```bash
start.bat
```

The application will:
1. Prompt you for a research query
2. Begin autonomous research using multiple search and crawl operations
3. Store important findings in the knowledge base
4. Generate a comprehensive markdown report
5. Allow follow-up questions via interactive prompts

### Building a Standalone Executable

Create a Windows executable:
```bash
build.bat
```

The compiled executable will be available in the `dist/` folder.

## Configuration

Set these environment variables in a `.env` file:

```
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-5-mini  # or another available model
OPENAI_REASONING_EFFORT=medium  # low, medium, or high
OPENAI_BASE_URL=  # Optional: custom API endpoint
```

## Project Structure

```
searchagent/
├── main.py                   # Entry point with Responses API agent loop
├── functions.py              # Tool implementations (search, crawl, reporting)
├── requirements.txt          # Python dependencies (installed via uv)
├── install.bat               # Setup script (creates venv, installs deps)
├── start.bat                 # Launch script (use this to run the program once installed)
├── build.bat                 # PyInstaller build script
├── SearchAgent.spec          # PyInstaller configuration
├── reports/                  # Generated markdown reports
├── research_knowledge/       # Local knowledge base (JSON)
└── media/                    # Assets (icons, etc.)
```

## Key Components

### Tools Available to the Agent

The research agent has access to these tools:

- **duckduckgo_search**: Search the web and return crawlable results
- **crawl4ai**: Extract text content from webpages as markdown
- **get_wikipedia_page**: Fetch Wikipedia article content via API
- **save_knowledge**: Store findings in the persistent knowledge base
- **get_all_knowledge**: Retrieve all stored knowledge entries
- **create_report**: Generate and save the final markdown report

### main.py

The main orchestrator using OpenAI's Responses API. Features:
- Streaming support for real-time output display
- Multi-turn conversation handling
- Tool call execution with error handling
- Usage statistics tracking
- Reasoning process visualization (with color-coded output)

### functions.py

Implements all research tools and utilities:
- URL extraction and validation (including DuckDuckGo and Bing redirects)
- Web search result formatting with hyperlink support
- Asynchronous webpage crawling
- Wikipedia API integration with proper User-Agent headers
- Knowledge base management (JSON persistence)
- Report generation with source citations
- Console output helpers (hyperlinks, safe Unicode printing)

## Recent Updates

### Latest: OpenAI Responses API Port
The project has been migrated to use OpenAI's latest Responses API, featuring:
- Streaming responses with real-time output
- Built-in reasoning with configurable effort levels
- Parallel tool execution support
- Structured function calling with strict mode validation

### Previous Enhancements
- Improved URL extraction and DuckDuckGo search result handling
- Token count logging for web crawls
- Knowledge management refactored to functions.py
- Wikipedia API compliance with proper User-Agent
- Installation process simplified with uv package manager
- Progress reporting and ETA calculations
- PyInstaller configuration with all necessary hidden imports

## Dependencies

Key Python packages:
- **openai**: OpenAI API client (v2.14.0+)
- **crawl4ai**: Web page crawler with browser automation
- **ddgs**: DuckDuckGo search API
- **requests**: HTTP library for API calls
- **python-dotenv**: Environment variable management
- **pyinstaller**: Executable compilation
- **rich**: Enhanced console formatting

Full list in `requirements.txt`

## Notes

- The knowledge base is cleared at the start of each research session (see `main.py`)
- Reports are permanent once created (cannot be modified or deleted)
- Supports OSC 8 hyperlinks in terminal output (VS Code, WezTerm, iTerm2, VTE-based terminals)
- Uses async/await for non-blocking web operations
- Handles URL redirect chains (DuckDuckGo, Bing ad links)
- Safe Unicode console printing with fallback encoding

## Future Enhancements

Potential improvements for consideration:
- Load model selection function for runtime model switching
- Knowledge base persistence across sessions
- Advanced filtering and search within knowledge base
- Custom research templates
- Rate limiting and quota management
