import re
from pathlib import Path
from typing import ClassVar

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=Path(__file__).parent.parent / ".env")

    # API keys
    serpapi_api_key: str = ""
    tavily_api_key: str = ""

    # eBay search
    min_ebay_score: int = 100

    # Card extraction — compiled once at class definition, not env-configurable
    GRADED_PATTERN: ClassVar[re.Pattern] = re.compile(
        r"\b(PSA|BGS|CGC)\s*(\d+(?:\.\d+)?)\b", re.IGNORECASE
    )
    UNGRADED_CONDITIONS: ClassVar[list[tuple[re.Pattern, str]]] = [
        (re.compile(r"\bNM-MT\b", re.IGNORECASE), "nm-mt"),
        (re.compile(r"\bNear Mint\b", re.IGNORECASE), "nm"),
        (re.compile(r"\bLightly Played\b", re.IGNORECASE), "lp"),
        (re.compile(r"\bMP\b", re.IGNORECASE), "mp"),
        (re.compile(r"\bHP\b", re.IGNORECASE), "hp"),
        (re.compile(r"\bDMG\b", re.IGNORECASE), "dmg"),
        (re.compile(r"\bNM\b", re.IGNORECASE), "nm"),
        (re.compile(r"\bLP\b", re.IGNORECASE), "lp"),
    ]
    CLEANUP_PATTERN: ClassVar[re.Pattern] = re.compile(
        r"\b(PSA|BGS|CGC)\s*\d+(?:\.\d+)?\b"
        r"|\bNM-MT\b|\bNear Mint\b|\bLightly Played\b"
        r"|\bMP\b|\bHP\b|\bDMG\b|\bNM\b|\bLP\b",
        re.IGNORECASE,
    )


settings = Settings()
