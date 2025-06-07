"""Utility helpers for normalizing citation URLs."""

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
import json


@dataclass
class NormalizationConfig:
    """Configuration options for URL canonicalization."""

    strip_www: bool = True
    strip_subdomain: bool = True
    include_path: bool = False
    # bool removes all query params, list removes specific ones
    strip_query_params: bool | list[str] = True
    aliases: dict | None = None


def strip_subdomain(hostname: str) -> str:
    """Return hostname without the first subdomain."""
    parts = hostname.split(".")
    if len(parts) > 2:
        return ".".join(parts[-2:])
    return hostname


def load_aliases(path: Path) -> dict:
    """Load a domain alias map from a JSON file if it exists."""
    if not path.exists():
        return {}
    with path.open() as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def canonicalize_url(url: str, config: NormalizationConfig) -> str:
    """Canonicalize a URL according to the provided configuration."""
    if not url:
        return url
    parsed = urlparse(url)

    host = parsed.hostname or ""
    if config.strip_www and host.startswith("www."):
        host = host[4:]
    if config.strip_subdomain:
        host = strip_subdomain(host)

    if config.aliases and host in config.aliases:
        host = config.aliases[host]

    path = parsed.path if config.include_path else ""
    query = parsed.query
    if config.strip_query_params is True:
        query = ""
    elif isinstance(config.strip_query_params, list):
        qs = [
            (k, v)
            for k, v in parse_qsl(parsed.query, keep_blank_values=True)
            if k not in config.strip_query_params
        ]
        query = urlencode(sorted(qs))
    else:
        query = urlencode(
            sorted(parse_qsl(parsed.query, keep_blank_values=True))
        )

    canon = urlunparse((parsed.scheme, host, path, "", query, ""))
    return canon.lower()
