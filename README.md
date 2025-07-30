# AI Research Agent

This project is an AI-powered research agent that uses large language models to answer research queries. It can search the web, crawl websites, and generate reports based on its findings.

## Installation

To install the project, run the `install.bat` script. This will create a virtual environment, install the required dependencies, and set up the necessary browser components for `crawl4ai`.

```bash
install.bat
```

## Usage

Once the installation is complete, you can run the research agent using the `start.bat` script.

```bash
start.bat
```

The script will activate the virtual environment and then execute the `main.py` script. You will be prompted to enter a research query.

## Functionality

- **Research:** The agent takes a user-provided query and uses DuckDuckGo to search for relevant information.
- **Crawling:** It can crawl websites to extract text content for further analysis.
- **Knowledge Base:** The agent can store and retrieve information from a local knowledge base (`research_knowledge/knowledge.json`).
- **Reporting:** After conducting research, the agent generates a detailed report in markdown format and saves it in the `reports/` directory.

## Project Structure

- `main.py`: The main entry point of the application.
- `requirements.txt`: A list of the Python dependencies.
- `install.bat`: A script to automate the installation process.
- `start.bat`: A script to run the research agent.
- `reports/`: A directory where the generated reports are stored.
- `research_knowledge/`: A directory used to store the knowledge base.

Todo:
- Load model function