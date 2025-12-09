


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
    print()
    print(f"Knowledge {next_num} saved: {knowledge}")
    return f"Knowledge {next_num} saved successfully."

def get_all_knowledge() -> list:
    """Returns all entries in the knowledge base."""
    print()
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
    print()
    print(f"Crawling {url}")
    return asyncio.run(crawl4aiasync(url))

def duckduckgo_search(search_query: str) -> str:
    """Searches DuckDuckGo for the given query and returns the results.

    Args:
        query: The query to search for.
        treat it like a Google search query.
    Returns:
        The search results with crawlable links.
    """
    print()
    print(f"Searching DuckDuckGo for: {search_query}")
    try:
        results = DDGS().text(search_query, max_results=6)
        filtered_results = [{'title': r['title'], 'href': r['href']} for r in results]
        print(filtered_results)
        return json.dumps(filtered_results)
    except Exception as e:
        print(f"Error searching DuckDuckGo: {e}")
        return json.dumps([])
    

def get_wikipedia_page(page: str) -> str:
    # Todo: Add +tokencount in the tokenoverview to better track token usage 
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
    print()
    print(f"Fetching Wikipedia page: {page}")
    
    url = 'https://en.wikipedia.org/w/api.php'
    params = {
        'action': 'query',
        'format': 'json',
        'prop': 'extracts',
        'explaintext': True,
        'titles': page
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()
        pages = data.get('query', {}).get('pages', {})

        if not pages:
            result = "No page found."
        else:
            page_data = next(iter(pages.values()))
            result = page_data.get('extract', "No content found for the given page.")
    except Exception as e:
        print(f"Error fetching Wikipedia page: {e}")
        result = f"Error fetching Wikipedia page: {e}"

    model = lms.llm()
    print(f"Token count: {len(model.tokenize(str(result)))}")
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
    
def context_details():
    # context window details
    model = lms.llm()
    token_count = len(model.tokenize(str(chat)))
    context_length = model.get_context_length()
    remaining_percentage = round(((context_length - token_count) / context_length) * 100)
    print()
    print(f"{token_count}/{context_length} ({remaining_percentage}%)")
    print("\n")
    return