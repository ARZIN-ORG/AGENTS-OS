class AacpSdkError(Exception):
    """Base SDK error."""

class ValidationError(AacpSdkError):
    """Raised when inputs fail validation."""

class SecurityError(AacpSdkError):
    """Raised when signature or crypto checks fail."""

class ScopeError(AacpSdkError):
    """Raised when policy scopes/channels are invalid or missing."""
