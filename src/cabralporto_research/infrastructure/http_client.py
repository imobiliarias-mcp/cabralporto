"""HTTP transport abstraction and implementation for Tecimob API."""

import socket
from dataclasses import dataclass
from typing import Any, Protocol
import httpx

_ORIGINAL_GETADDRINFO = socket.getaddrinfo


def _forced_ipv4_getaddrinfo(host: Any, port: Any, family: int = 0, type: int = 0, proto: int = 0, flags: int = 0) -> Any:
    """Force IPv4 address resolution to avoid network unreachable errors on dual-stack hosts."""
    return _ORIGINAL_GETADDRINFO(host, port, socket.AF_INET, type, proto, flags)


class CabralPortoResearchError(Exception):
    """Base exception for Cabral Porto research operations."""


class PropertyNotFoundError(CabralPortoResearchError):
    """Raised when a requested property cannot be found."""


class NetworkError(CabralPortoResearchError):
    """Raised when an HTTP or network connection error occurs."""


@dataclass(frozen=True)
class HttpResponse:
    """Encapsulates response payload from HTTP endpoints."""

    status_code: int
    text: str
    json_data: Any
    final_url: str


class HttpClientProtocol(Protocol):
    """Protocol defining network transport contract."""

    def get(self, url: str, params: dict[str, str] | None = None) -> HttpResponse:
        """Execute HTTP GET request with optional query parameters."""
        ...


class HttpxHttpClient:
    """Production HTTP client powered by httpx with forced IPv4 resolution."""

    DEFAULT_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    DEFAULT_DOMAIN = "cabralportoimoveis.com.br"

    def __init__(self, timeout: float = 15.0, domain: str = DEFAULT_DOMAIN) -> None:
        """Initialize client with timeout and domain header."""
        self._timeout = timeout
        self._domain = domain
        self._ensure_ipv4_patch()

    def _ensure_ipv4_patch(self) -> None:
        """Apply monkeypatch to socket getaddrinfo if not already set."""
        if socket.getaddrinfo is not _forced_ipv4_getaddrinfo:
            socket.getaddrinfo = _forced_ipv4_getaddrinfo

    def _build_headers(self) -> dict[str, str]:
        """Construct standard headers required by Tecimob."""
        return {
            "User-Agent": self.DEFAULT_USER_AGENT,
            "Accept": "application/json",
            "x-domain": self._domain,
        }

    def get(self, url: str, params: dict[str, str] | None = None) -> HttpResponse:
        """Execute GET request and return wrapped HttpResponse."""
        headers = self._build_headers()
        try:
            with httpx.Client(follow_redirects=True, timeout=self._timeout) as client:
                resp = client.get(url, headers=headers, params=params)
                json_body = self._safe_parse_json(resp)
                return HttpResponse(
                    status_code=resp.status_code,
                    text=resp.text,
                    json_data=json_body,
                    final_url=str(resp.url),
                )
        except httpx.HTTPError as exc:
            raise NetworkError(f"HTTP request to {url} failed: {exc}") from exc

    def _safe_parse_json(self, response: httpx.Response) -> Any:
        """Safely parse JSON response body or return None."""
        try:
            return response.json()
        except ValueError:
            return None
