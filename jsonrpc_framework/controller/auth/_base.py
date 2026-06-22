from enum import StrEnum

__all__ = [
    "AccessType",
]


class AccessType(StrEnum):
    PUBLIC = "public"
    OPTIONAL = "optional"
    PRIVATE = "private"


class BaseAuthentication: ...


class BasePermission: ...
