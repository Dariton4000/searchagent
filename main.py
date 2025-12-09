import lmstudio as lms
from pathlib import Path
from datetime import datetime, timedelta
import time
from rich.console import Console
from rich.markdown import Markdown
from functions import (
    duckduckgo_search,
    save_knowledge,
    get_all_knowledge,
    crawl4ai,
    create_report,
    get_wikipedia_page,
    context_details,
)
import functions

console = Console(force_terminal=True)















class ProgressBarPrinter:
    def __init__(self):
        self.start_time = None
        self.last_time = None
        self.ema_speed = None  # Units per second
        self.alpha = 0.3  # Smoothing factor for EMA
        self.last_pct = 0
        self.first_call = True

    def update_progress(self, progress, _):
        # Normalize progress to 0-100
        if progress <= 1.0:
            pct = progress * 100
        else:
            pct = progress
        
        now = time.time()
        
        if self.first_call:
            print() # Newline to start
            self.first_call = False
        
        # Detect new processing phase: if progress dropped significantly (e.g., was at/near 100%, now low)
        # This indicates a new prompt processing started after a tool call
        if self.last_pct >= 90 and pct < 50:
            self.start_time = None
            self.last_time = None
            self.ema_speed = None
            self.last_pct = 0
        
        if self.start_time is None:
            if pct > 0:
                self.start_time = now
                self.last_time = now
                self.last_pct = pct
                self._render(pct)
                return
            else:
                self._render(pct)
                return

        dt = now - self.last_time
        
        # Update stats every 0.1s or if finished
        if dt > 0.1 or pct >= 100:
            dp = pct - self.last_pct
            if dt > 0:
                speed = dp / dt
                if self.ema_speed is None:
                    self.ema_speed = speed
                else:
                    self.ema_speed = self.alpha * speed + (1 - self.alpha) * self.ema_speed
            
            self.last_time = now
            self.last_pct = pct
            self._render(pct)

    def _render(self, pct):
        # Calculate ETA
        if self.ema_speed and self.ema_speed > 0:
            remaining = 100 - pct
            eta_seconds = remaining / self.ema_speed
            eta_str = str(timedelta(seconds=int(eta_seconds)))
        else:
            eta_str = "Calculating..."

        if self.start_time:
            elapsed = time.time() - self.start_time
        else:
            elapsed = 0
        elapsed_str = str(timedelta(seconds=int(elapsed)))

        # Bar
        width = 30
        filled = int(width * (pct / 100))
        bar = "█" * filled + "░" * (width - filled)
        
        # Colors (ANSI)
        BLUE = "\033[94m"
        GREEN = "\033[92m"
        RESET = "\033[0m"
        
        # \033[2K clears the entire line
        line = f"\r\033[2K{BLUE}Processing{RESET} ▕{bar}▏ {pct:3.0f}% • {GREEN}ETA: {eta_str}{RESET} • Elapsed: {elapsed_str}"
        print(line, end="", flush=True)

    def clear(self):
        # Clear line
        print("\r\033[2K", end="", flush=True)



class FormattedPrinter:
    # For reasoning content of the LLM, doesn't affect LLMs that don't reason
    # This version is more robust and handles edge cases like stray tags
    # and interruptions during streaming.
    def __init__(self):
        self.current_buffer = ""
        self.bot_response_buffer = ""
        self.in_think_content_mode = False
        self.in_analysis_mode = False
        self.think_tag_open = "<think>"
        self.think_tag_close = "</think>"
        self.channel_tag_open = "<|channel|>"
        self.message_tag_open = "<|message|>"
        self.end_tag_close = "<|end|>"
        self.grey_code = "\033[90m"
        self.reset_code = "\033[0m"

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
            elif self.in_analysis_mode:
                end_tag_index = self.current_buffer.find(self.end_tag_close)
                if end_tag_index != -1:
                    text_to_print = self.current_buffer[:end_tag_index]
                    print(text_to_print, end="", flush=True)
                    print(self.reset_code, end="", flush=True)
                    self.current_buffer = self.current_buffer[end_tag_index + len(self.end_tag_close):]
                    self.in_analysis_mode = False
                else:
                    print(self.current_buffer, end="", flush=True)
                    self.current_buffer = ""
                    return
            else:  # not in any special mode
                think_open_tag_index = self.current_buffer.find(self.think_tag_open)
                channel_open_tag_index = self.current_buffer.find(self.channel_tag_open)

                # Determine which tag comes first
                first_tag_index = -1
                is_think_tag = False
                is_channel_tag = False

                if think_open_tag_index != -1 and (channel_open_tag_index == -1 or think_open_tag_index < channel_open_tag_index):
                    first_tag_index = think_open_tag_index
                    is_think_tag = True
                elif channel_open_tag_index != -1:
                    first_tag_index = channel_open_tag_index
                    is_channel_tag = True

                if is_think_tag:
                    text_to_print = self.current_buffer[:first_tag_index]
                    self.bot_response_buffer += text_to_print
                    print(self.grey_code, end="", flush=True)
                    self.current_buffer = self.current_buffer[first_tag_index + len(self.think_tag_open):]
                    self.in_think_content_mode = True
                elif is_channel_tag:
                    message_tag_index = self.current_buffer.find(self.message_tag_open)
                    if message_tag_index != -1 and message_tag_index > first_tag_index:
                        text_to_print = self.current_buffer[:first_tag_index]
                        self.bot_response_buffer += text_to_print
                        
                        channel_content = self.current_buffer[first_tag_index + len(self.channel_tag_open):message_tag_index]
                        
                        print(f"{self.grey_code}", end="", flush=True)

                        self.current_buffer = self.current_buffer[message_tag_index + len(self.message_tag_open):]
                        self.in_analysis_mode = True
                    else: # No message tag, just print
                        self.bot_response_buffer += self.current_buffer
                        self.current_buffer = ""
                else:
                    # No tags in buffer
                    self.bot_response_buffer += self.current_buffer
                    self.current_buffer = ""
                    return
    
    def finalize(self):
        self._process_buffer()
        if self.in_think_content_mode or self.in_analysis_mode:
            print(self.reset_code, end="", flush=True)
            self.in_think_content_mode = False
            self.in_analysis_mode = False
        
        # Only print the markdown if the buffer contains non-whitespace content;
        # this prevents printing empty markdown blocks.
        if self.bot_response_buffer.strip():
            console.print(Markdown(self.bot_response_buffer))
        self.bot_response_buffer = ""

def researcher(query: str):
    model = lms.llm()
    context_length = model.get_context_length()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    global chat
    # Researchquery needs to be included in the initial system message for some reason for some models ???
    chat = lms.Chat(
        f"You are a task-focused AI researcher. The current date and time is {now}. Begin researching immediately. Perform multiple online searches to gather reliable information. Crawl webpages for context. When possible use Wikipedia as a source. Research extensively, multiple searches and crawls, One Source is not enough. After crawling a webpage, store any useful knowledge in the research knowledge base, treat it like your permanent memory. Recall all stored knowledge before creating the final report. Don't forget to ground information in reliable sources, crawl pages after searching DuckDuckGo for this. Mark any assumptions clearly. Produce an extensive report in markdown format using the create_report tool, be sure to use this tool. Create the report ONLY when you are done with all research. Already saved reports can NOT be changed or deleted. Add some tables if you think it will help clarify the information. Here is the research query: '{query}'"
    )
    functions.chat = chat  # Share chat with functions module

    chat.add_user_message(f"Here is the research query given by the user: '{query}'")

    current_tokens = len(model.tokenize(str(chat)))
    remaining_percentage = round(((context_length - current_tokens) / context_length) * 100)
    printer = FormattedPrinter()
    progressprinter = ProgressBarPrinter()
    print(f"Researcher: ", end="", flush=True)
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
    print(f"\rResearcher: ", end="", flush=True)
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
        functions.chat = chat  # Update chat reference in functions module
        
        current_tokens = len(model.tokenize(str(chat)))
        remaining_percentage = round(((context_length - current_tokens) / context_length) * 100)
        printer = FormattedPrinter()
        progressprinter = ProgressBarPrinter()
        print(f"Researcher: ", end="", flush=True)
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
        print(f"\rResearcher: ", end="", flush=True)
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
