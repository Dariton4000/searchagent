# SearchAgent Architecture

This document provides a detailed overview of the SearchAgent architecture, design patterns, and implementation details.

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Package Structure](#package-structure)
4. [Core Components](#core-components)
5. [Data Flow](#data-flow)
6. [Design Patterns](#design-patterns)
7. [Configuration Management](#configuration-management)
8. [Error Handling](#error-handling)
9. [Testing Strategy](#testing-strategy)
10. [Extensibility](#extensibility)

## Overview

SearchAgent is built using a modular architecture that separates concerns into distinct packages:

- **Core**: Research orchestration and chat management
- **Tools**: LLM-callable functions for research tasks
- **UI**: User interface and output formatting
- **Config**: Centralized configuration management

The system follows SOLID principles and emphasizes:
- **Separation of Concerns**: Each module has a single responsibility
- **Dependency Injection**: Eliminates global state
- **Testability**: All components are independently testable
- **Maintainability**: Clear module boundaries and documentation

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         User Interface                       │
│                       (CLI / main.py)                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Core / Researcher                         │
│  ┌──────────────────┐      ┌──────────────────────────┐    │
│  │  ChatManager     │◄─────┤  researcher()           │    │
│  │  - System Prompt │      │  - Orchestrates         │    │
│  │  - Chat State    │      │  - Interactive Loop     │    │
│  │  - Tool Registry │      └──────────────────────────┘    │
│  └──────────────────┘                                       │
└────────────┬───────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│                      LM Studio / LLM                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Tool Selection & Execution                          │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────┬───────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│                         Tools Layer                          │
│  ┌─────────┐  ┌─────────┐  ┌──────────┐  ┌──────────┐     │
│  │ Search  │  │Crawler  │  │Knowledge │  │Wikipedia │     │
│  └─────────┘  └─────────┘  └──────────┘  └──────────┘     │
│  ┌──────────────┐  ┌────────────────────────────────┐     │
│  │  Reporting   │  │         Utils                  │     │
│  └──────────────┘  └────────────────────────────────┘     │
└────────────┬───────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│                    External Services                         │
│  ┌──────────┐  ┌───────────┐  ┌──────────────┐            │
│  │DuckDuckGo│  │Wikipedia  │  │Web Pages     │            │
│  │   API    │  │   API     │  │(crawl4ai)    │            │
│  └──────────┘  └───────────┘  └──────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

## Package Structure

### searchagent/

```
searchagent/
├── __init__.py              # Package exports
├── main.py                  # Application entry point
│
├── core/                    # Core research logic
│   ├── __init__.py
│   ├── chat_manager.py      # Chat session management
│   └── researcher.py        # Research orchestration
│
├── tools/                   # LLM-callable tools
│   ├── __init__.py
│   ├── search.py            # DuckDuckGo search
│   ├── crawler.py           # Web crawling
│   ├── knowledge.py         # Knowledge base
│   ├── wikipedia.py         # Wikipedia API
│   ├── reporting.py         # Report generation
│   └── utils.py             # Utilities
│
├── ui/                      # UI components
│   ├── __init__.py
│   ├── progress.py          # Progress bar
│   └── formatter.py         # Output formatting
│
├── config/                  # Configuration
│   ├── __init__.py
│   ├── settings.py          # Settings classes
│   └── constants.py         # Constants
│
└── templates/               # Templates
    └── system_prompt.txt    # System prompt
```

## Core Components

### ChatManager

**Purpose**: Manages LLM chat sessions with encapsulated state.

**Responsibilities**:
- Initialize chat with system prompt
- Manage conversation history
- Track token usage
- Execute research rounds
- Handle tool registration

**Key Methods**:
```python
__init__(query: str, tools: List[Callable])  # Initialize session
add_user_message(message: str)               # Add user input
execute_research_round(callbacks...)         # Run LLM inference
get_context_usage() -> tuple                 # Token usage stats
```

**Design Pattern**: Facade pattern - simplifies LM Studio interaction.

### Researcher

**Purpose**: Orchestrates the research workflow.

**Responsibilities**:
- Initialize ChatManager
- Execute initial research
- Handle interactive loop
- Coordinate UI components

**Key Functions**:
```python
researcher(query: str)                       # Main entry point
get_tool_functions() -> List[Callable]       # Get available tools
_execute_research_round(chat_manager)        # Helper for execution
```

**Design Pattern**: Template Method - defines research workflow structure.

### Tools Layer

Each tool is a standalone function callable by the LLM:

#### search.py
- **Function**: `duckduckgo_search(query: str) -> str`
- **Purpose**: Perform web searches
- **Returns**: JSON string with results
- **Error Handling**: Returns empty array on failure

#### crawler.py
- **Function**: `crawl4ai(url: str) -> str`
- **Purpose**: Extract page content
- **Validation**: URL format checking
- **Returns**: Markdown content
- **Error Handling**: Detailed error messages

#### knowledge.py
- **Class**: `KnowledgeBase`
- **Functions**: `save_knowledge()`, `get_all_knowledge()`
- **Storage**: JSON file with numeric keys
- **Thread Safety**: File-based locking

#### wikipedia.py
- **Function**: `get_wikipedia_page(page: str) -> str`
- **Purpose**: Fetch Wikipedia content
- **API**: Official Wikipedia API
- **User Agent**: Compliant with WMF policy

#### reporting.py
- **Function**: `create_report(title, content, sources) -> str`
- **Validation**: Title sanitization
- **Timestamps**: Unique filenames
- **Format**: Markdown with sources section

## Data Flow

### Research Session Flow

```
1. User Input
   └─> main.py: get research query
       └─> researcher(query)
           ├─> ChatManager.__init__(query, tools)
           │   ├─> Load system prompt template
           │   ├─> Format with timestamp & query
           │   └─> Create Chat instance
           │
           ├─> execute_research_round()
           │   ├─> model.act() [LM Studio]
           │   │   ├─> LLM decides which tools to call
           │   │   ├─> Calls duckduckgo_search()
           │   │   ├─> Calls crawl4ai()
           │   │   ├─> Calls save_knowledge()
           │   │   └─> Calls create_report()
           │   │
           │   └─> UI callbacks
           │       ├─> ProgressBarPrinter.update_progress()
           │       └─> FormattedPrinter.print_fragment()
           │
           └─> Interactive loop
               ├─> Get user input
               ├─> Add to chat
               └─> execute_research_round() [repeat]
```

### Knowledge Base Flow

```
save_knowledge(text)
  ├─> KnowledgeBase._load()
  │   └─> Read JSON from file
  ├─> Determine next ID
  ├─> Add entry
  ├─> KnowledgeBase._save()
  │   └─> Write JSON to file
  └─> Return success message

get_all_knowledge()
  ├─> KnowledgeBase._load()
  │   └─> Read JSON from file
  ├─> Sort by numeric keys
  └─> Return list of values
```

## Design Patterns

### 1. Facade Pattern
**Used in**: ChatManager
**Purpose**: Simplifies LM Studio API interaction
**Benefits**: Single interface for complex operations

### 2. Singleton Pattern
**Used in**: Configuration (`config`)
**Purpose**: Single global config instance
**Benefits**: Consistent settings across app

### 3. Template Method Pattern
**Used in**: Researcher workflow
**Purpose**: Define algorithm structure
**Benefits**: Consistent research flow

### 4. Strategy Pattern
**Used in**: Tool functions
**Purpose**: Interchangeable research strategies
**Benefits**: Easy to add new tools

### 5. Dependency Injection
**Used in**: ChatManager, Tools
**Purpose**: Eliminate global state
**Benefits**: Testability, maintainability

## Configuration Management

### Settings Hierarchy

```
AppConfig
├── PathConfig (paths)
│   ├── knowledge_dir: Path
│   ├── reports_dir: Path
│   ├── logs_dir: Path
│   └── cache_dir: Path
│
├── SearchConfig (search)
│   ├── max_results: int
│   ├── timeout: int
│   └── user_agent: str
│
├── CrawlerConfig (crawler)
│   ├── headless: bool
│   ├── timeout: int
│   └── bypass_cache: bool
│
├── ProgressConfig (progress)
│   ├── ema_alpha: float
│   ├── bar_width: int
│   ├── update_interval: float
│   └── reset_threshold: float
│
├── KnowledgeConfig (knowledge)
│   ├── filename: str
│   ├── max_file_size_mb: int
│   └── auto_flush: bool
│
└── LLMConfig (llm)
    ├── model_name: Optional[str]
    ├── temperature: float
    └── max_tokens: Optional[int]
```

### Usage

```python
from searchagent.config import config

# Access settings
max_results = config.search.max_results
reports_path = config.paths.reports_dir

# Override settings
config.search.timeout = 20
config.progress.bar_width = 40
```

## Error Handling

### Strategy

1. **Tool Functions**: Return error strings (not exceptions)
   - Allows LLM to see and respond to errors
   - Example: `"Error: Invalid URL format"`

2. **Internal Functions**: Raise specific exceptions
   - Caught at appropriate levels
   - Logged with full context

3. **User-Facing**: Friendly error messages
   - Hide implementation details
   - Provide actionable guidance

### Logging Levels

- **DEBUG**: Detailed execution flow
- **INFO**: Key operations (search, crawl, save)
- **WARNING**: Recoverable issues
- **ERROR**: Failures requiring attention

## Testing Strategy

### Unit Tests

**Location**: `tests/unit/`
**Coverage**: Individual functions and classes
**Mocking**: External dependencies (LM Studio, APIs)

Example test structure:
```python
class TestKnowledgeBase:
    def test_save_knowledge_creates_file(self, knowledge_file):
        # Arrange
        kb = KnowledgeBase(knowledge_file)
        # Act
        result = kb.save_knowledge("test")
        # Assert
        assert knowledge_file.exists()
```

### Integration Tests

**Location**: `tests/integration/`
**Coverage**: Component interactions
**Markers**: `@pytest.mark.integration`

### Test Fixtures

**Location**: `tests/conftest.py`
**Shared fixtures**:
- `temp_dir`: Temporary directory
- `knowledge_file`: Test knowledge file
- `mock_llm`: Mocked LLM
- `sample_data`: Test data

### CI/CD

**GitHub Actions**: `.github/workflows/test.yml`
- Multi-OS testing (Ubuntu, Windows, macOS)
- Coverage reporting
- Linting (ruff)
- Type checking (mypy)
- Security scanning (bandit, pip-audit)

## Extensibility

### Adding New Tools

1. Create function in `searchagent/tools/`:
```python
def my_new_tool(param: str) -> str:
    """Tool description for LLM.

    Args:
        param: Parameter description

    Returns:
        Result description
    """
    # Implementation
    return result
```

2. Add to `tools/__init__.py`:
```python
from .my_tool import my_new_tool
__all__ = [..., "my_new_tool"]
```

3. Register in `core/researcher.py`:
```python
def get_tool_functions() -> List[Callable]:
    return [
        # existing tools...
        my_new_tool,
    ]
```

### Adding Configuration

1. Add dataclass in `config/settings.py`:
```python
@dataclass
class MyConfig:
    setting1: str = "default"
    setting2: int = 10
```

2. Add to `AppConfig`:
```python
@dataclass
class AppConfig:
    # existing configs...
    my_config: MyConfig = field(default_factory=MyConfig)
```

3. Use in code:
```python
from searchagent.config import config
value = config.my_config.setting1
```

### Adding UI Components

1. Create module in `ui/`:
```python
class MyUIComponent:
    def display(self, data):
        # Implementation
        pass
```

2. Export from `ui/__init__.py`

3. Use in researcher or tools

---

**Last Updated**: 2024-12-10
**Version**: 2.0.0
