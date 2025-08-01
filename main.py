from pyexpat import model
import lmstudio as lms
import json
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
from ddgs import DDGS
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
import re
import os
from rich.console import Console
from rich.markdown import Markdown



def save_knowledge(knowledge: str) -> str:
    """Adds new knowledge for later use."""
    knowledge_file = Path("research_knowledge") / "knowledge.json"
    # load existing or start fresh
    if knowledge_file.exists():
        with knowledge_file.open("r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}
    else:
        data = {}
    # determine next numeric key
    nums = [int(k) for k in data.keys() if k.isdigit()]
    next_num = max(nums, default=0) + 1
    data[str(next_num)] = knowledge
    # write back
    with knowledge_file.open("w") as f:
        json.dump(data, f, indent=2)
    print(f"Knowledge {next_num} saved: {knowledge}")
    return f"Knowledge {next_num} saved successfully."

def get_all_knowledge() -> list:
    """Returns all entries in the knowledge base."""
    print("Retrieving all knowledge entries")
    knowledge_file = Path("research_knowledge") / "knowledge.json"
    if not knowledge_file.exists():
        return []
    with knowledge_file.open("r") as f:
        try:
            data = json.load(f)
            return [data[key] for key in sorted(data.keys(), key=int)]
        except json.JSONDecodeError:
            return []

async def crawl4aiasync(url: str):
    browser_conf = BrowserConfig(headless=True)  # or False to see the browser
    run_conf = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS
    )

    async with AsyncWebCrawler(config=browser_conf) as crawler:
        result = await crawler.arun(
            url=url,
            config=run_conf
        )
        # needs to be result.markdown to return the markdown content
        # ignore the warning about the return type, it is correct
        #counts tokens in the markdown content
        return result.markdown  # type: ignore

def duckduckgo_search(search_query: str) -> str:
    """Searches DuckDuckGo for the given query and returns the results.

    Args:
        query: The query to search for.
        treat it like a Google search query, accepts special formats like "query" for only exact matches, query filetype:pdf for specific file types and so on.
    Returns:
        The search results with crawlable links.
    """
    print(f"\nSearching DuckDuckGo for: {search_query}")
    results = DDGS().text(search_query, max_results=6)
    filtered_results = [{'title': r['title'], 'href': r['href']} for r in results]
    print(filtered_results)
    return json.dumps(filtered_results)

def crawl4ai(url: str):
    """Crawls a given URL and returns the text content.
        Use this tool to crawl a webpage after searching DuckDuckGo.

    Do not use this tool to crawl Wikipedia pages directly.

    Args:
        url: The URL to crawl.
        needs to start with http:// or https://
    Returns:
        The text content of the page in markdown format.
    """
    print(f"Crawling {url}")
    return asyncio.run(crawl4aiasync(url))

def get_wikipedia_page(page: str) -> str:
    """        
    Returns:
        Page content as plain text
    
    Get content from a Wikipedia page.
    If no exact match is found, it will return a list of similar pages.
    Use this instead of crawling Wikipedia pages directly.

    Args:
        page: Exact title of the Wikipedia page
            
    Returns:
        Page content as plain text
    """
    print(f"Fetching Wikipedia page: {page}")
    
    url = 'https://en.wikipedia.org/w/api.php'
    params = {
        'action': 'query',
        'format': 'json',
        'prop': 'extracts',
        'explaintext': True,
        'titles': page
    }
    
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()
    pages = data.get('query', {}).get('pages', {})

    if not pages:
        result = "No page found."
    else:
        page_data = next(iter(pages.values()))
        result = page_data.get('extract', "No content found for the given page.")


    return result

def create_report(title: str, content: str, sources: list) -> str:
    """Generates a final report in markdown format. Only use this tool after all extensive research is done.

    Args:
        title: The title of the report. Will also be used for the file name combined with the current date and time for a unique file name.
        content: The content of the extensive report.
        sources: A list of sources used in the report.
    Saves:
        The final report in markdown format into reports/ always accessible to the user.
    Returns:
        The file name of the report for the AI to tell the user where to find it or an error message.
    """

    # Validate and sanitize title
    model = lms.llm()
    # Context window details
    current_tokens = len(model.tokenize(str(chat)))
    context_length = model.get_context_length()
    total_tokens = current_tokens
    remaining_percentage = round(((context_length - total_tokens) / context_length) * 100)
    print(f"{total_tokens}/{context_length} ({remaining_percentage}%)")

    sanitized_title = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')
    if not sanitized_title:
        return "Error: Report title cannot be empty or contain only special characters."

    report_content = f"# {sanitized_title}\n\n{content}\n\n## Sources\n"
    for source in sources:
        report_content += f"- {source}\n"

    reports_dir = Path("reports")
    try:
        reports_dir.mkdir(parents=True, exist_ok=True)
        report_file = reports_dir / f"{sanitized_title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with report_file.open("w") as f:
            f.write(report_content)
        print(f"Report saved to {report_file}")
        return f"DONE, Report saved to {report_file}"
    except IOError as e:
        error_message = f"Error writing report to file: {e}"
        print(error_message)
        return error_message


class ProgressBarPrinter:
    def __init__(self):
        self.progress = 0
        self.start_time = None

    def update_progress(self, progress, _):
        if self.start_time is None:
            self.start_time = time.time()
        # Convert progress to percentage if it's in 0-1 range
        if progress <= 1.0:
            self.progress = progress * 100
        else:
            self.progress = progress
        self._print_progress_bar()

    def _print_progress_bar(self):
        bar_length = 50
        # Ensure progress is within valid range
        progress = max(0, min(100, self.progress))
        filled_length = int(bar_length * progress / 100)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)

        elapsed_time = time.time() - (self.start_time if self.start_time else time.time())
        
        if progress == 100:
            eta_str = "done"
            completion_str = ""
        elif progress > 0:
            total_time = (elapsed_time / progress) * 100
            remaining_time = total_time - elapsed_time
            completion_time = datetime.now() + timedelta(seconds=remaining_time)
            
            eta_str = f"ETA: {int(remaining_time)}s"
            completion_str = f"Completion: {completion_time.strftime('%H:%M:%S')}"
        else: # progress is 0
            eta_str = "ETA: N/A"
            completion_str = ""

        # Clear the line before printing to avoid overlapping text and format progress as integer
        print(f"\r{' ' * 120}\r|{bar}| {int(progress)}% | {eta_str} | {completion_str}", end="", flush=True)
    
    def clear(self):
        # Clear the progress bar from the terminal and move cursor to beginning of line
        print(f"\r{' ' * 120}\r", end="", flush=True)

def context_details():
    # context window details
    model = lms.llm()
    token_count = len(model.tokenize(str(chat)))
    context_length = model.get_context_length()
    remaining_percentage = round(((context_length - token_count) / context_length) * 100)
    print(f"{token_count}/{context_length} ({remaining_percentage}%)")
    return

class FormattedPrinter:
    # For reasoning content of the LLM, doesn't affect LLMs that don't reason
    # This version is more robust and handles edge cases like stray tags
    # and interruptions during streaming.
    def __init__(self):
        self.current_buffer = ""
        self.bot_response_buffer = ""
        self.in_think_content_mode = False
        self.think_tag_open = "<think>"
        self.think_tag_close = "</think>"
        self.grey_code = "\033[90m"
        self.reset_code = "\033[0m"
        
        # Enable ANSI escape codes on Windows
        if os.name == 'nt':
            os.system('')

    def print_fragment(self, fragment, round_index=0):
        self.current_buffer += fragment.content
        self._process_buffer()

    def _process_buffer(self):
        while self.current_buffer:
            if self.in_think_content_mode:
                close_tag_index = self.current_buffer.find(self.think_tag_close)
                if close_tag_index != -1:
                    text_to_print = self.current_buffer[:close_tag_index]
                    print(text_to_print, end="", flush=True)
                    print(self.reset_code, end="", flush=True)
                    self.current_buffer = self.current_buffer[close_tag_index + len(self.think_tag_close):]
                    self.in_think_content_mode = False
                else:
                    print(self.current_buffer, end="", flush=True)
                    self.current_buffer = ""
                    return
            else:  # not in_think_content_mode
                open_tag_index = self.current_buffer.find(self.think_tag_open)
                close_tag_index = self.current_buffer.find(self.think_tag_close)

                if open_tag_index != -1 and (open_tag_index < close_tag_index or close_tag_index == -1):
                    # Process the opening tag
                    text_to_print = self.current_buffer[:open_tag_index]
                    self.bot_response_buffer += text_to_print
                    # print(text_to_print, end="", flush=True)
                    print(self.grey_code, end="", flush=True)
                    self.current_buffer = self.current_buffer[open_tag_index + len(self.think_tag_open):]
                    self.in_think_content_mode = True
                elif close_tag_index != -1:
                    # A stray closing tag is the next tag, remove it
                    text_to_print = self.current_buffer[:close_tag_index]
                    self.bot_response_buffer += text_to_print
                    # print(text_to_print, end="", flush=True)
                    self.current_buffer = self.current_buffer[close_tag_index + len(self.think_tag_close):]
                else:
                    # No tags in buffer
                    self.bot_response_buffer += self.current_buffer
                    # print(self.current_buffer, end="", flush=True)
                    self.current_buffer = ""
                    return
    
    def finalize(self):
        self._process_buffer()
        if self.in_think_content_mode:
            print(self.reset_code, end="", flush=True)
            self.in_think_content_mode = False
        
        console = Console()
        console.print(Markdown(self.bot_response_buffer))
        self.bot_response_buffer = ""

def researcher(query: str):
    model = lms.llm()
    context_length = model.get_context_length()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    global chat
    chat = lms.Chat(
        f"You are a task-focused AI researcher. The current date and time is {now}. Begin researching immediately. Perform multiple online searches to gather reliable information. Crawl webpages for context. When possible use Wikipedia as a source. Research extensively, multiple searches and crawls, One Source is not enough. After crawling a webpage, store any useful knowledge in the research knowledge base, treat it like your permanent memory. Recall all stored knowledge before creating the final report. Don't forget to ground information in reliable sources, crawl pages after searching DuckDuckGo for this. Mark any assumptions clearly. Produce an extensive report in markdown format using the create_report tool, be sure to use this tool. Create the report ONLY when you are done with all research. Already saved reports can NOT be changed or deleted. Add some tables if you think it will help clarify the information."
    )

    chat.add_user_message(f"Here is the research query given by the user: '{query}'")

    current_tokens = len(model.tokenize(str(chat)))
    remaining_percentage = round(((context_length - current_tokens) / context_length) * 100)
    printer = FormattedPrinter()
    progressprinter = ProgressBarPrinter()
    print(f"{remaining_percentage}% Bot: ", end="", flush=True)
    model.act(
        chat,
        [duckduckgo_search, save_knowledge, get_all_knowledge, crawl4ai, create_report, get_wikipedia_page],
        on_message=chat.append,
        on_prediction_fragment=printer.print_fragment,
        on_round_end=lambda round_index: context_details(),
        on_prompt_processing_progress=progressprinter.update_progress,
    )
    # Clear progress bar and reset cursor position before finalizing output
    progressprinter.clear()
    print(f"\r{remaining_percentage}% Bot: ", end="", flush=True)
    printer.finalize()

    # Now enter the interactive loop
    while True:
        try:
            user_input = input("You (leave blank to exit): ")
        except EOFError:
            print()
            break
        if not user_input:
           break
        chat.add_user_message(user_input)
        
        current_tokens = len(model.tokenize(str(chat)))
        remaining_percentage = round(((context_length - current_tokens) / context_length) * 100)
        printer = FormattedPrinter()
        progressprinter = ProgressBarPrinter()
        print(f"{remaining_percentage}% Bot: ", end="", flush=True)
        model.act(
            chat,
            [duckduckgo_search, save_knowledge, get_all_knowledge, crawl4ai, create_report, get_wikipedia_page],
            on_message=chat.append,
            on_prediction_fragment=printer.print_fragment,
            on_round_end=lambda round_index: context_details(),
            on_prompt_processing_progress=progressprinter.update_progress,
        )
        # Clear progress bar and reset cursor position before finalizing output
        progressprinter.clear()
        print(f"\r{remaining_percentage}% Bot: ", end="", flush=True)
        printer.finalize()


def main():
    KNOWLEDGE_DIR = Path("research_knowledge")   # Directory to store research knowledge
    KNOWLEDGE_DIR.mkdir(exist_ok=True)   # Create the directory if it doesn't exist
    REPORT_DIR = Path("reports")   # Directory to store final reports
    REPORT_DIR.mkdir(exist_ok=True)   # Create the directory if it doesn't exist
    # Deletes all existing knowledge files
    for file in KNOWLEDGE_DIR.glob("*.json"):
        file.unlink()
    
    # gets research query from user, if empty exits
    research_topic = input("Please provide a research task for the ai researcher: ").strip()
    if not research_topic:
        print("No research task provided. Exiting.")
        return
    
    # start the research
    researcher(research_topic)

if __name__ == "__main__":
    main()
