from enum import StrEnum, auto


class UserRole(StrEnum):
    ADMIN = auto()
    MODERATOR = auto()
    USER = auto()


class SessionStatus(StrEnum):
    ACTIVE = auto()
    INACTIVE = auto()
    EXPIRED = auto()
