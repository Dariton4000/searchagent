import json
from pathlib import Path
import requests
from datetime import datetime
import asyncio
from ddgs import DDGS
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
import re
import sys
import os
import base64
from urllib.parse import urlparse, parse_qs, unquote

# Updated by main.py after each model call (OpenAI Responses API usage object)
last_usage: dict | None = None

_CONSOLE_TEXT_TRANSLATION = str.maketrans(
    {
        "\u00a0": " ",  # no-break space
        "\u200b": "",  # zero-width space
        "\u2010": "-",  # hyphen
        "\u2011": "-",  # non-breaking hyphen
        "\u2012": "-",  # figure dash
        "\u2013": "-",  # en dash
        "\u2014": "-",  # em dash
        "\u2212": "-",  # minus sign
        "\u2026": "...",  # ellipsis
    }
)


def _normalize_whitespace(text: str) -> str:
    return " ".join(text.split())


def _truncate_middle(text: str, max_chars: int) -> str:
    if max_chars <= 0:
        return ""
    if len(text) <= max_chars:
        return text
    if max_chars <= 3:
        return text[:max_chars]
    keep_start = max(1, (max_chars - 3) // 2)
    keep_end = max(1, max_chars - 3 - keep_start)
    return text[:keep_start].rstrip() + "..." + text[-keep_end:].lstrip()


def _extract_target_url(href: str) -> str | None:
    href = href.strip()
    if not href:
        return None

    try:
        parsed = urlparse(href)
    except Exception:
        return None

    host = (parsed.netloc or "").lower()

    # DuckDuckGo redirect wrapper: https://duckduckgo.com/l/?uddg=<urlencoded>
    if host.endswith("duckduckgo.com") and parsed.path.startswith("/l/"):
        qs = parse_qs(parsed.query)
        uddg = qs.get("uddg", [None])[0]
        if uddg:
            target = unquote(uddg).strip()
            if target.startswith(("http://", "https://")):
                return target

    # Bing ad/redirect wrapper. Sometimes appears without a '?' in the URL.
    if host.endswith("bing.com") and parsed.path.startswith("/aclick"):
        qs_str = parsed.query
        if not qs_str and "&u=" in parsed.path:
            qs_str = parsed.path[len("/aclick") :].lstrip("?")

        if qs_str:
            qs = parse_qs(qs_str)
            u = qs.get("u", [None])[0]
            if u:
                u = u.strip()
                # Often base64 of a percent-encoded URL.
                try:
                    padded = u + ("=" * (-len(u) % 4))
                    decoded = base64.b64decode(padded, validate=False)
                    decoded_str = decoded.decode("utf-8", errors="replace")
                    target = unquote(decoded_str).strip()
                    if target.startswith(("http://", "https://")):
                        return target
                except Exception:
                    pass

                target = unquote(u).strip()
                if target.startswith(("http://", "https://")):
                    return target

    return None


def _url_display_text(url: str, *, max_chars: int = 80) -> str:
    url = url.strip()
    if not url:
        return url

    try:
        parsed = urlparse(url)
    except Exception:
        return _truncate_middle(url, max_chars)

    if parsed.netloc:
        host = parsed.netloc
        if host.startswith("www."):
            host = host[4:]
        path = parsed.path or ""
        if path == "/":
            path = ""
        display = (host + path).rstrip("/")
        if display:
            return _truncate_middle(display, max_chars)

    return _truncate_middle(url, max_chars)


def _supports_osc8_hyperlinks() -> bool:
    if not getattr(sys.stdout, "isatty", lambda: False)():
        return False

    if os.environ.get("WT_SESSION"):
        return True

    term_program = (os.environ.get("TERM_PROGRAM") or "").lower()
    if term_program in {"vscode", "wezterm", "iterm.app"}:
        return True

    if os.environ.get("VTE_VERSION") or os.environ.get("KONSOLE_VERSION"):
        return True

    return False


def _osc8_link(url: str, text: str) -> str:
    esc = "\x1b"
    st = esc + "\\"
    safe_url = url.replace(esc, "")
    safe_text = text.replace(esc, "")
    return f"{esc}]8;;{safe_url}{st}{safe_text}{esc}]8;;{st}"


def _safe_print(text: str = "", *, end: str = "\n") -> None:
    text = str(text).translate(_CONSOLE_TEXT_TRANSLATION)
    try:
        print(text, end=end, flush=True)
    except UnicodeEncodeError:
        encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
        data = (text + end).encode(encoding, errors="replace")
        buffer = getattr(sys.stdout, "buffer", None)
        if buffer is not None:
            buffer.write(data)
            buffer.flush()
        else:
            sys.stdout.write(data.decode(encoding, errors="replace"))
            sys.stdout.flush()


def _print_duckduckgo_results(query: str, results: list[dict]) -> None:
    if not results:
        _safe_print(f"DuckDuckGo results for: {query} (none)")
        return

    _safe_print(f"DuckDuckGo results for: {query} ({len(results)}):")
    use_osc8 = _supports_osc8_hyperlinks()
    for idx, r in enumerate(results, start=1):
        title = _normalize_whitespace(str(r.get("title", ""))).strip() or "(no title)"
        title = title.translate(_CONSOLE_TEXT_TRANSLATION)
        title = re.sub(r"\s*-\s*$", "", title).strip() or "(no title)"
        href = str(r.get("href", "")).strip()

        if href:
            target = _extract_target_url(href) or href
            display = _url_display_text(target, max_chars=80)
            link_text = _osc8_link(target, display) if use_osc8 else target
            _safe_print(f"{idx}. {title} - {link_text}")
        else:
            _safe_print(f"{idx}. {title} - (no url)")

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
    result = asyncio.run(crawl4aiasync(url))
    return result

def duckduckgo_search(search_query: str) -> str:
    """Searches DuckDuckGo for the given query and returns the results.

    Args:
        query: The query to search for.
        treat it like a Google search query.
    Returns:
        The search results with crawlable links.
    """
    _safe_print(f"Searching DuckDuckGo for: {search_query}")
    try:
        results = list(DDGS().text(search_query, max_results=6))
        filtered_results = [{"title": r["title"], "href": r["href"]} for r in results]
    except Exception as e:
        _safe_print(f"Error searching DuckDuckGo: {e}")
        return json.dumps([])

    try:
        _print_duckduckgo_results(search_query, results)
    except Exception:
        # Best-effort printing only; the tool result should still be returned.
        pass

    return json.dumps(filtered_results)


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
    # Wikipedia API requires a descriptive User-Agent identifying the bot
    # See: https://foundation.wikimedia.org/wiki/Policy:Wikimedia_Foundation_User-Agent_Policy
    headers = {
        'User-Agent': 'SearchAgent/1.0 (AI Research Tool Bot; https://github.com/Dariton4000/searchagent)'
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
    if last_usage:
        input_tokens = last_usage.get("input_tokens")
        output_tokens = last_usage.get("output_tokens")
        total_tokens = last_usage.get("total_tokens")
        print(f"Tokens: in={input_tokens} out={output_tokens} total={total_tokens}")

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
    """Prints the most recent token usage stats (from the OpenAI Responses API)."""
    if not last_usage:
        return

    input_tokens = last_usage.get("input_tokens")
    output_tokens = last_usage.get("output_tokens")
    total_tokens = last_usage.get("total_tokens")

    print(f"Tokens: in={input_tokens} out={output_tokens} total={total_tokens}")
