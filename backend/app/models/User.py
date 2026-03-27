from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class User:
    email: str
    password_hash: str
    id: int = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    reset_token: str = None
    reset_token_expires_at: datetime = None