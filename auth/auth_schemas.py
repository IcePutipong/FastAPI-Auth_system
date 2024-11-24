from pydantic import BaseModel,  EmailStr
from typing import Optional
import datetime

class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class ChangePassword(BaseModel):
    email:EmailStr  
    old_password: str
    new_password: str

class TokenCreate(BaseModel):
    user_id: str
    access_token: str
    refresh_tkeon: str
    status: bool
    created_date: datetime.datetime

