from pydantic import BaseModel


class UserBase(BaseModel):
	username: str
	email: str | None = None
	full_name: str | None = None


class UserCreate(UserBase):
	password: str


class User(UserBase):
	disabled: bool | None = None


class UserInDB(User):
	hashed_password: str


class Token(BaseModel):
	access_token: str
	token_type: str


class TokenData(BaseModel):
	username: str