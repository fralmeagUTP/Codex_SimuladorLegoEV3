"""HTTP-facing errors for the web layer."""

from __future__ import annotations


class WebError(Exception):
    status_code = 400
    code = "WEB_ERROR"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class SessionNotFound(WebError):
    status_code = 404
    code = "SESSION_NOT_FOUND"


class SessionForbidden(WebError):
    status_code = 403
    code = "SESSION_FORBIDDEN"


class CapacityExceeded(WebError):
    status_code = 429
    code = "CAPACITY_EXCEEDED"


class InvalidPayload(WebError):
    status_code = 400
    code = "INVALID_PAYLOAD"


class InvalidSessionState(WebError):
    status_code = 409
    code = "INVALID_SESSION_STATE"
