# AI Research Agent

This project is an AI-powered research agent that uses OpenAI's GPT-5-mini model to answer research queries. It can search the web, crawl websites, and generate reports based on its findings.

## Prerequisites

- Python 3.8 or higher
- OpenAI API key (set as environment variable `OPENAI_API_KEY`)

## Installation

To install the project, run the `install.bat` script. This will create a virtual environment, install the required dependencies, and set up the necessary browser components for `crawl4ai`.

```bash
install.bat
```

## Configuration

Before running the agent, you need to set your OpenAI API key as an environment variable:

**Windows:**
```cmd
set OPENAI_API_KEY=your_api_key_here
```

**Linux/Mac:**
```bash
export OPENAI_API_KEY=your_api_key_here
```

## Usage

Once the installation is complete and your API key is set, you can run the research agent using the `start.bat` script.

```bash
start.bat
```

The script will activate the virtual environment and then execute the `main.py` script. You will be prompted to enter a research query.

## Functionality

- **Research:** The agent takes a user-provided query and uses DuckDuckGo to search for relevant information.
- **Crawling:** It can crawl websites to extract text content for further analysis.
- **Knowledge Base:** The agent can store and retrieve information from a local knowledge base (`research_knowledge/knowledge.json`).
- **Reporting:** After conducting research, the agent generates a detailed report in markdown format and saves it in the `reports/` directory.
- **Reasoning:** Uses GPT-5-mini reasoning model with extended thinking capabilities. The agent displays its reasoning process in real-time and saves reasoning summaries for later reference.
- **Reasoning Summaries:** All reasoning steps are automatically saved to `research_knowledge/reasoning_summaries.json` for review and analysis.

## Project Structure

- `main.py`: The main entry point of the application.
- `requirements.txt`: A list of the Python dependencies.
- `install.bat`: A script to automate the installation process.
- `start.bat`: A script to run the research agent.
- `reports/`: A directory where the generated reports are stored.
- `research_knowledge/`: A directory used to store the knowledge base and reasoning summaries.