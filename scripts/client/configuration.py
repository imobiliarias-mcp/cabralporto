"""Configuration settings for Cabral Porto Imóveis API client."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CabralPortoConfiguration:
    """Holds configuration parameters for portal communication."""

    base_hostname: str = "cabralportoimoveis.com.br"
    base_url: str = "https://cabralportoimoveis.com.br"
    api_base_url: str = "https://api-sites.tecimob.com.br/api"

    def origin_header_value(self) -> str:
        """Return canonical portal origin."""
        return f"https://{self.base_hostname}"

    def referer_header_value(self) -> str:
        """Return canonical portal referer."""
        return f"https://{self.base_hostname}/"
