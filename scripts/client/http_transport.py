"""HTTP transport layer for Cabral Porto Imóveis API queries."""

import socket
from typing import Any

import httpx

from scripts.client.configuration import CabralPortoConfiguration
from scripts.domain.exceptions import PropertyNotFoundException, RentalDomainException

_ORIGINAL_GETADDRINFO = socket.getaddrinfo


def _forced_ipv4_getaddrinfo(host: Any, port: Any, family: int = 0, type: int = 0, proto: int = 0, flags: int = 0) -> Any:
    """Force IPv4 address resolution to avoid network unreachable errors."""
    return _ORIGINAL_GETADDRINFO(host, port, socket.AF_INET, type, proto, flags)


class CabralPortoHttpTransport:
    """Dispatches HTTP network requests to Tecimob API for Cabral Porto."""

    DEFAULT_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"

    def __init__(
        self,
        configuration: CabralPortoConfiguration | None = None,
        http_client: httpx.Client | None = None,
    ) -> None:
        """Initialize transport with configuration and client collaborator."""
        self._config = configuration or CabralPortoConfiguration()
        self._ensure_ipv4_patch()
        client = http_client or httpx.Client(timeout=20.0, follow_redirects=True)
        client.headers["User-Agent"] = self.DEFAULT_USER_AGENT
        client.headers["Accept"] = "application/json"
        client.headers["x-domain"] = self._config.base_hostname
        self._client = client

    def _ensure_ipv4_patch(self) -> None:
        """Apply monkeypatch to socket getaddrinfo if needed."""
        if socket.getaddrinfo is not _forced_ipv4_getaddrinfo:
            socket.getaddrinfo = _forced_ipv4_getaddrinfo

    def public_base_url(self) -> str:
        """Return configured public property site base URL."""
        return self._config.public_base_url()

    def get_json(self, url: str, params: dict[str, str] | None = None) -> dict[str, Any]:
        """Fetch and parse JSON payload from URL with optional query parameters."""
        response = self.get_response(url, params=params)
        try:
            return response.json()
        except Exception as error:
            raise RentalDomainException(f"Failed to parse JSON from {url}: {error}") from error

    def get_response(self, url: str, params: dict[str, str] | None = None) -> httpx.Response:
        """Execute HTTP GET and return raw response, handling 404/422 as not found."""
        try:
            response = self._client.get(url, params=params)
            if response.status_code in (404, 422):
                raise PropertyNotFoundException(f"Resource at {url} was not found (status {response.status_code}).")
            response.raise_for_status()
            return response
        except httpx.HTTPError as error:
            raise RentalDomainException(f"Network request to {url} failed: {error}") from error
