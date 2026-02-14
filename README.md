# Searchagent
Searchagent is a powerful tool inspired by OpenAI's Deep Research, capable of performing continuous long horizon research tasks. With local or cloud models.
## Features:
- **Web Search**: Searchagent is capable of performing many web searches to gather surface-level information on a topic using the DuckDuckGo search engine.
- **Web Scraping**: Searchagent can scrape the content of web pages with crawl4ai, allowing it to extract relevant information from the web.
- **Choice of Models**: Searchagent supports all OpenAI responses-compatible endpoints, enabling users to choose from a variety of providers like OpenAI, Azure, and even local models via LM-Studio.

## Installation
Please refer to the [Installation Guide](https://github.com/Dariton4000/searchagent/wiki/Installation) for detailed instructions on how to set up Searchagent.

## Development Status:

### Compact .exe Version:
- In Experimental Stage, you can test it via the releases page on the GitHub repository. Please note that this version may not work at all and is not recommended for use at all as of now.

### Context compaction:
- In Design Stage, we are currently working on a context compaction system that will automatically compact (summarize) the context of the session when the context limit is nearly reached.

### Sub Agents:
- In Design Stage, we are planning to implement a sub-agent system that will allow Searchagent to create and manage multiple sub-agents for different tasks, enabling it to perform more complex research tasks faster and more thoroughly.