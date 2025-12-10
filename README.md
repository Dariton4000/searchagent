# SearchAgent - AI-Powered Research Assistant

[![Tests](https://github.com/Dariton4000/searchagent/workflows/Tests/badge.svg)](https://github.com/Dariton4000/searchagent/actions)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

SearchAgent is an AI-powered research assistant that autonomously searches the web, analyzes content, builds a knowledge base, and generates comprehensive research reports. It leverages local LLMs through LM Studio for privacy-focused, offline research capabilities.

## ✨ Features

- 🔍 **Autonomous Research**: Automatically performs web searches and analyzes results
- 🌐 **Web Crawling**: Extracts content from web pages using headless browser automation
- 📚 **Knowledge Base**: Builds and maintains a persistent knowledge base during research
- 📊 **Report Generation**: Creates comprehensive markdown reports with sources
- 🎯 **Wikipedia Integration**: Direct API access for reliable encyclopedia content
- 💬 **Interactive Mode**: Follow-up questions after initial research
- 🎨 **Rich UI**: Progress bars, ETA estimates, and formatted output
- 🔒 **Privacy-Focused**: Runs completely locally with LM Studio

## 📋 Requirements

- Python 3.11 or higher
- LM Studio (running locally)
- 4GB+ RAM recommended
- Internet connection for web searches

## 🚀 Quick Start

### Windows

```batch
# Install
install.bat

# Run
start.bat
```

### Linux/Mac

```bash
# Install
chmod +x install.sh
./install.sh

# Run
./start.sh
```

## 📦 Installation

### Option 1: Using Install Scripts (Recommended)

**Windows:**
```batch
install.bat
```

**Linux/Mac:**
```bash
chmod +x install.sh
./install.sh
```

### Option 2: Manual Installation

1. Create a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up browser components for web crawling:
```bash
crawl4ai-setup
```

## 💻 Usage

### Basic Usage

1. Start LM Studio and load a model
2. Run SearchAgent:
   - Windows: `start.bat`
   - Linux/Mac: `./start.sh`
   - Or directly: `python main.py`

3. Enter your research query when prompted
4. The AI will autonomously research and generate a report
5. Optionally ask follow-up questions

### Example Session

```
Please provide a research task for the ai researcher: What are the latest developments in quantum computing?

Researcher: [AI begins researching...]
- Searching DuckDuckGo...
- Crawling relevant pages...
- Storing knowledge...
- Creating comprehensive report...

Report saved to reports/Latest_Developments_in_Quantum_Computing_20240101_120000.md

You (leave blank to exit): Tell me more about quantum error correction
Researcher: [AI provides additional information...]

You (leave blank to exit):
```

## 🏗️ Architecture

SearchAgent follows a modular architecture for maintainability:

```
searchagent/
├── core/                   # Core research logic
│   ├── chat_manager.py    # LLM chat session management
│   └── researcher.py      # Research orchestration
├── tools/                  # LLM-callable tools
│   ├── search.py          # Web search (DuckDuckGo)
│   ├── crawler.py         # Web crawling (crawl4ai)
│   ├── knowledge.py       # Knowledge base management
│   ├── wikipedia.py       # Wikipedia API integration
│   ├── reporting.py       # Report generation
│   └── utils.py           # Utility functions
├── ui/                     # User interface components
│   ├── progress.py        # Progress bar with ETA
│   └── formatter.py       # Output formatting
├── config/                 # Configuration management
│   ├── settings.py        # Application settings
│   └── constants.py       # Constants and magic strings
└── templates/              # Templates
    └── system_prompt.txt  # LLM system prompt template
```

For detailed architecture documentation, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## 🧪 Testing

### Run All Tests

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=searchagent --cov-report=html
```

### Run Specific Test Types

```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/ -m integration

# Specific test file
pytest tests/unit/test_knowledge.py -v
```

### Code Quality

```bash
# Linting
ruff check searchagent/ tests/

# Type checking
mypy searchagent/ --ignore-missing-imports

# Security scan
bandit -r searchagent/

# Format code
black searchagent/ tests/
```

## ⚙️ Configuration

SearchAgent uses a centralized configuration system. Modify `searchagent/config/settings.py` to customize:

- **Search Settings**: Max results, timeout, user agent
- **Crawler Settings**: Headless mode, cache behavior
- **Progress Bar**: EMA smoothing, bar width, update interval
- **Paths**: Knowledge directory, reports directory, logs
- **LLM Settings**: Model name, temperature, max tokens

Example configuration override:

```python
from searchagent.config import config

# Customize search
config.search.max_results = 10
config.search.timeout = 20

# Customize paths
config.paths.reports_dir = Path("/custom/reports")
```

## 📊 Project Structure

```
searchagent/
├── .github/
│   └── workflows/
│       ├── build.yml       # Build executable workflow
│       └── test.yml        # Testing workflow
├── searchagent/            # Main package
│   ├── core/               # Core functionality
│   ├── tools/              # Research tools
│   ├── ui/                 # UI components
│   ├── config/             # Configuration
│   ├── templates/          # Templates
│   └── main.py             # Application entry point
├── tests/                  # Test suite
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── conftest.py         # Shared fixtures
├── docs/                   # Documentation
├── media/                  # Icons and media
├── main.py                 # Entry point script
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # Development dependencies
├── pytest.ini              # Pytest configuration
├── SearchAgent.spec        # PyInstaller spec
└── README.md               # This file
```

## 🔧 Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/Dariton4000/searchagent.git
cd searchagent

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest
```

### Building Executable

**Windows:**
```batch
build.bat
```

**Linux/Mac:**
```bash
./build.sh
```

The executable will be in the `dist/` directory.

## 📝 Logging

SearchAgent uses structured logging with automatic rotation:

- **Location**: `logs/searchagent_YYYY-MM-DD_HH-MM-SS.log`
- **Rotation**: Daily
- **Retention**: 7 days
- **Levels**: DEBUG, INFO, WARNING, ERROR

View logs:
```bash
tail -f logs/searchagent_*.log
```

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting (`pytest && ruff check .`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

Please ensure:
- All tests pass
- Code coverage remains above 80%
- Code is formatted with `black`
- Type hints are added for new functions
- Docstrings follow Google style

## 📄 License

This project is open source. See LICENSE file for details.

## 🙏 Acknowledgments

- [LM Studio](https://lmstudio.ai/) - Local LLM inference
- [crawl4ai](https://github.com/unclecode/crawl4ai) - Web crawling
- [DuckDuckGo](https://duckduckgo.com/) - Privacy-focused search
- [Rich](https://github.com/Textualize/rich) - Terminal formatting

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Dariton4000/searchagent/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Dariton4000/searchagent/discussions)

## 🗺️ Roadmap

- [ ] Support for additional LLM backends (Ollama, OpenAI)
- [ ] Web UI interface
- [ ] Export to PDF/DOCX
- [ ] Multi-language support
- [ ] Configurable research strategies
- [ ] Citation management
- [ ] Research project workspaces

---

**Version**: 2.0.0
**Status**: Active Development
