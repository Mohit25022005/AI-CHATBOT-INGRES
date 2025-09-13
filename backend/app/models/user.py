# app/models/user.py
from pydantic import BaseModel, Field
from typing import Optional

class UserSession(BaseModel):
    session_id: str
    user_id: Optional[str] = None
    created_at: Optional[str] = None
