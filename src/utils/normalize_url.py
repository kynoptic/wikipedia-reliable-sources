"""Utility functions for normalizing citation URLs."""

from dataclasses import dataclass
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

@dataclass
class NormalizationConfig:
    strip_www: bool = True
    strip_subdomain: bool = True
    include_path: bool = False
    strip_query_params: bool = True
    aliases: dict | None = None


def strip_subdomain(hostname: str) -> str:
    """Return hostname without the first subdomain."""
    parts = hostname.split('.')
    if len(parts) > 2:
        return '.'.join(parts[-2:])
    return hostname


def canonicalize_url(url: str, config: NormalizationConfig) -> str:
    """Canonicalize a URL according to the provided configuration."""
    if not url:
        return url
    parsed = urlparse(url)

    host = parsed.hostname or ''
    if config.strip_www and host.startswith('www.'):
        host = host[4:]
    if config.strip_subdomain:
        host = strip_subdomain(host)

    if config.aliases and host in config.aliases:
        host = config.aliases[host]

    path = parsed.path if config.include_path else ''
    query = ''
    if not config.strip_query_params:
        query = urlencode(parse_qsl(parsed.query))

    canon = urlunparse((parsed.scheme, host, path, '', query, ''))
    return canon.lower()
