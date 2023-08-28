from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class User(BaseModel):
    id: str
    username: str
    email: str


class UserInDB(User):
    hashed_password: str
