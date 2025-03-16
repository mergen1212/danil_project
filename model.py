from __future__ import annotations

from pydantic import BaseModel


class Model(BaseModel):
    username: str
    full_name: str
    email: str
    hashed_password: str
    disabled: bool
