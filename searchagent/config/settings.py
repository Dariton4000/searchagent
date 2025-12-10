"""Configuration management for SearchAgent.

This module centralizes all configuration values to improve maintainability
and make it easier to customize the application behavior.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class PathConfig:
    """File system path configuration."""

    knowledge_dir: Path = Path("research_knowledge")
    reports_dir: Path = Path("reports")
    logs_dir: Path = Path("logs")
    cache_dir: Path = Path(".cache")

    def ensure_directories_exist(self) -> None:
        """Create all configured directories if they don't exist."""
        self.knowledge_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        self.cache_dir.mkdir(exist_ok=True)


@dataclass
class SearchConfig:
    """Search engine configuration."""

    max_results: int = 6
    timeout: int = 10
    user_agent: str = "SearchAgent/1.0 (AI Research Tool Bot; https://github.com/Dariton4000/searchagent)"


@dataclass
class CrawlerConfig:
    """Web crawler configuration."""

    headless: bool = True
    timeout: int = 30
    bypass_cache: bool = True


@dataclass
class ProgressConfig:
    """Progress bar configuration."""

    ema_alpha: float = 0.3  # Smoothing factor for exponential moving average
    bar_width: int = 30
    update_interval: float = 0.1  # Minimum time between updates (seconds)
    reset_threshold: float = 90.0  # Progress % to detect new phase


@dataclass
class KnowledgeConfig:
    """Knowledge base configuration."""

    filename: str = "knowledge.json"
    max_file_size_mb: int = 10
    auto_flush: bool = False  # Auto-save after each operation


@dataclass
class LLMConfig:
    """LLM configuration."""

    model_name: Optional[str] = None  # None = use default from LM Studio
    temperature: float = 0.7
    max_tokens: Optional[int] = None


@dataclass
class AppConfig:
    """Main application configuration."""

    paths: PathConfig = field(default_factory=PathConfig)
    search: SearchConfig = field(default_factory=SearchConfig)
    crawler: CrawlerConfig = field(default_factory=CrawlerConfig)
    progress: ProgressConfig = field(default_factory=ProgressConfig)
    knowledge: KnowledgeConfig = field(default_factory=KnowledgeConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)

    # System prompt template path
    system_prompt_template: str = "templates/system_prompt.txt"

    def __post_init__(self):
        """Initialize and validate configuration."""
        self.paths.ensure_directories_exist()


# Global configuration instance
config = AppConfig()


def get_config() -> AppConfig:
    """Get the global configuration instance.

    Returns:
        The application configuration object.
    """
    return config
