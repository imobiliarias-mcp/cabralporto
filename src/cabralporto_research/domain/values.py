"""Domain value objects representing search parameters and constraints."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PriceRange:
    """Encapsulates minimum and maximum price constraints in Brazilian Reais."""

    minimum: int | None = None
    maximum: int | None = None

    def __post_init__(self) -> None:
        """Validate price constraints fail-fast."""
        if self.minimum is not None and self.minimum < 0:
            raise ValueError(f"Minimum price cannot be negative: {self.minimum}")
        if self.maximum is not None and self.maximum < 0:
            raise ValueError(f"Maximum price cannot be negative: {self.maximum}")
        if self.minimum is not None and self.maximum is not None and self.minimum > self.maximum:
            raise ValueError(f"Minimum price {self.minimum} exceeds maximum price {self.maximum}")

    def query_parameters(self) -> dict[str, str]:
        """Convert price range to Tecimob query parameters."""
        parameters: dict[str, str] = {}
        if self.minimum is not None:
            parameters["filter[by_higher_than_price]"] = str(self.minimum)
        if self.maximum is not None:
            parameters["filter[by_lower_than_price]"] = str(self.maximum)
        return parameters


@dataclass(frozen=True)
class AreaRange:
    """Encapsulates minimum and maximum square meters constraints."""

    minimum: int | None = None
    maximum: int | None = None
    area_type: str = "total_area"

    def __post_init__(self) -> None:
        """Validate area constraints fail-fast."""
        if self.minimum is not None and self.minimum < 0:
            raise ValueError(f"Minimum area cannot be negative: {self.minimum}")
        if self.maximum is not None and self.maximum < 0:
            raise ValueError(f"Maximum area cannot be negative: {self.maximum}")
        if self.minimum is not None and self.maximum is not None and self.minimum > self.maximum:
            raise ValueError(f"Minimum area {self.minimum} exceeds maximum {self.maximum}")

    def query_parameters(self) -> dict[str, str]:
        """Convert area range to Tecimob query parameters."""
        parameters: dict[str, str] = {}
        if self.minimum is not None:
            parameters["filter[by_area][greater_equals]"] = str(self.minimum)
        if self.maximum is not None:
            parameters["filter[by_area][lower_equals]"] = str(self.maximum)
        if self.minimum is not None or self.maximum is not None:
            parameters["filter[by_area][name]"] = self.area_type
        return parameters


@dataclass(frozen=True)
class RoomCount:
    """Represents a room quantity constraint (exact or minimum)."""

    count: int
    is_minimum: bool = True

    def __post_init__(self) -> None:
        """Validate room quantity."""
        if self.count < 0:
            raise ValueError(f"Room count cannot be negative: {self.count}")

    def query_parameters(self, room_type: str = "bedroom") -> dict[str, str]:
        """Convert room count to Tecimob query parameter."""
        filter_mode = "by_room_greater_equals" if self.is_minimum else "by_room_equals"
        key = f"filter[{filter_mode}][{room_type}]"
        return {key: str(self.count)}


@dataclass(frozen=True)
class PageNumber:
    """Represents a 1-indexed pagination number and limit."""

    value: int = 1
    limit: int = 21

    def __post_init__(self) -> None:
        """Validate pagination boundary."""
        if self.value < 1:
            raise ValueError(f"Page number must be at least 1, got {self.value}")
        if self.limit < 1 or self.limit > 100:
            raise ValueError(f"Page limit must be between 1 and 100, got {self.limit}")

    def query_parameters(self) -> dict[str, str]:
        """Convert page number to Tecimob query parameters."""
        return {
            "offset": str(self.value),
            "limit": str(self.limit),
        }


@dataclass(frozen=True)
class PropertyCode:
    """Represents a sanitized property identifier or reference code."""

    value: str

    def __post_init__(self) -> None:
        """Validate property identifier is non-empty string."""
        if not self.value or not self.value.strip():
            raise ValueError("Property code cannot be empty.")

    def sanitized(self) -> str:
        """Return cleaned property code."""
        return self.value.strip()
