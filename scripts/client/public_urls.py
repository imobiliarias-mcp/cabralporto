"""Public property URL validation at the parser boundary."""

from urllib.parse import urljoin, urlsplit


class PublicPropertyUrlError(ValueError):
    """Raised when a listing has no recoverable public property URL."""


class PublicPropertyUrlResolver:
    """Resolve public card links using a configured public site base URL."""

    def __init__(self, public_base_url: str) -> None:
        """Validate and retain the public site base URL."""
        self._base_url = self._validate_base_url(public_base_url)

    def resolve(self, raw_url: object, property_context: str) -> str:
        """Return an absolute HTTP(S) property URL or raise with listing context."""
        candidate = self._clean_candidate(raw_url)
        if not candidate:
            raise PublicPropertyUrlError(f"Missing public property URL for '{property_context}'.")
        normalized_candidate = self._normalize_candidate(candidate, property_context)
        return self._resolve_candidate(normalized_candidate, property_context)

    def _normalize_candidate(self, candidate: str, property_context: str) -> str:
        """Prefix documented bare slugs while retaining explicit URL forms."""
        try:
            parts = urlsplit(candidate)
        except ValueError as error:
            raise PublicPropertyUrlError(
                f"Invalid public property URL for '{property_context}'."
            ) from error
        if parts.scheme or candidate.startswith("/"):
            return candidate
        if parts.path.startswith(("imovel/", "details/")):
            return candidate
        return f"/imovel/{candidate}"

    def _clean_candidate(self, raw_url: object) -> str:
        """Trim string URL input and reject values of other types."""
        if not isinstance(raw_url, str):
            return ""
        return raw_url.strip()

    def _validate_base_url(self, public_base_url: str) -> str:
        """Require an HTTP(S) base URL with a hostname."""
        try:
            parts = urlsplit(public_base_url.strip())
            hostname = parts.hostname
        except ValueError as error:
            raise PublicPropertyUrlError("Invalid configured public base URL.") from error
        if parts.scheme.lower() not in {"http", "https"} or not hostname:
            raise PublicPropertyUrlError("Invalid configured public base URL.")
        return f"{public_base_url.rstrip('/')}/"

    def _resolve_candidate(self, candidate: str, property_context: str) -> str:
        """Join a candidate link and validate the final scheme and host."""
        try:
            absolute_url = urljoin(self._base_url, candidate)
            parts = urlsplit(absolute_url)
            hostname = parts.hostname
        except ValueError as error:
            raise PublicPropertyUrlError(
                f"Invalid public property URL for '{property_context}'."
            ) from error
        if parts.scheme.lower() not in {"http", "https"} or not hostname or parts.username or parts.password:
            raise PublicPropertyUrlError(f"Invalid public property URL for '{property_context}'.")
        if not self._is_property_page(parts):
            raise PublicPropertyUrlError(f"Invalid public property URL for '{property_context}'.")
        return absolute_url

    def _is_property_page(self, parts) -> bool:
        """Reject Tecimob endpoints, media assets, and known search routes."""
        hostname = (parts.hostname or "").lower()
        path = parts.path.lower()
        if hostname == "api-sites.tecimob.com.br" or self._is_media_path(path):
            return False
        normalized_path = path.rstrip("/")
        return normalized_path in {"/imovel", "/details"} or normalized_path.startswith(
            ("/imovel/", "/details/")
        )

    @staticmethod
    def _is_media_path(path: str) -> bool:
        """Recognize common public media asset suffixes."""
        return path.endswith((".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg"))
