from enum import StrEnum


class ErrorCode(StrEnum):
    INVALID_CREDENTIALS = "invalid_credentials"
    NOT_FOUND = "not_found"
    ALREADY_EXISTS = "already_exists"
    PERMISSION_DENIED = "permission_denied"
    CONFLICT = "conflict"
    VALIDATION_ERROR = "validation_error"
    PAYLOAD_TOO_LARGE = "payload_too_large"
    INTERNAL_ERROR = "internal_error"
    UNAUTHENTICATED = "unauthenticated"
    TOKEN_EXPIRED = "token_expired"
    TOKEN_INVALID = "token_invalid"


class AppException(Exception):
    def __init__(self, code: str, message: str, status_code: int = 200):
        self.code = code
        self.message = message
        self.status_code = status_code
