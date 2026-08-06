from __future__ import annotations

class AACPError(Exception):
    pass

class RejectError(AACPError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message
