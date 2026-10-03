"""Unit tests for CabralPortoMcpAdapter."""

from scripts.mcp.tools import CabralPortoMcpAdapter


def test_mcp_adapter_provider_info():
    """Test MCP provider metadata."""
    adapter = CabralPortoMcpAdapter.create_default()
    info = adapter.get_provider_info()
    assert info["provider_name"] == "cabralporto"
    assert "search_rentals" in info["supported_operations"]
