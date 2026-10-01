"""Domain exceptions for Cabral Porto rental research."""


class RentalDomainException(Exception):
    """Base exception for all rental domain errors."""


class InvalidPriceException(RentalDomainException):
    """Raised when a monetary price is invalid."""


class InvalidPropertyCodeException(RentalDomainException):
    """Raised when a property identifier or code is invalid."""


class InvalidFilterException(RentalDomainException):
    """Raised when query filter constraints are contradictory or invalid."""


class PropertyNotFoundException(RentalDomainException):
    """Raised when a property cannot be found in the catalog."""
