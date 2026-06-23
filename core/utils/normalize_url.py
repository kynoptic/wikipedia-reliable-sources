"""Utility helpers for normalizing citation URLs."""

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
import json

import tldextract

# Offline mode: use tldextract's bundled Public Suffix List snapshot so
# decomposition is deterministic and never makes a network call (keeps CI green).
_EXTRACT = tldextract.TLDExtract(suffix_list_urls=())


@dataclass
class NormalizationConfig:
    """Configuration options for URL canonicalization."""

    strip_www: bool = True
    strip_subdomain: bool = True
    include_path: bool = False
    # bool removes all query params, list removes specific ones
    strip_query_params: bool | list[str] = True
    aliases: dict | None = None


@dataclass
class HostParts:
    """A hostname split into Public Suffix List components."""

    host: str       # full hostname as given, e.g. "news.bbc.co.uk"
    subdomain: str  # "news"
    domain: str     # "bbc"
    suffix: str     # "co.uk"


def strip_subdomain(hostname: str) -> str:
    """Return hostname without the first subdomain."""
    parts = hostname.split(".")
    if len(parts) > 2:
        return ".".join(parts[-2:])
    return hostname


def decompose_host(hostname: str) -> HostParts:
    """Split ``hostname`` into Public Suffix List components.

    Unlike :func:`strip_subdomain`, this is PSL-aware: ``news.bbc.co.uk`` yields
    domain ``bbc`` and suffix ``co.uk``. The subdomain is preserved so callers
    can distinguish ``www.`` / ``mobile.`` hosts; collapse them by grouping on
    ``(domain, suffix)``.
    """
    extracted = _EXTRACT(hostname)
    return HostParts(
        host=hostname,
        subdomain=extracted.subdomain,
        domain=extracted.domain,
        suffix=extracted.suffix,
    )


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
