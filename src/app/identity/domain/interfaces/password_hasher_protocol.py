from typing import Protocol


class PasswordHasherProtocol(Protocol):
    def hash(self, raw_password: str) -> str: ...

    def verify(self, raw_password: str, hashed_password: str) -> bool: ...