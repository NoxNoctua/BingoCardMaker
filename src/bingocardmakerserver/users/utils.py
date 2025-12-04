from datetime import datetime, timedelta, timezone

import jwt
from jwt.exceptions import InvalidTokenError

from . import schemas, crud

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30




def verify_password(plain_password, hashed_password):
	return plain_password == hashed_password


def get_password_hash(password):
	return password


def authenticate_user(db, username: str, password: str):
	user = crud.get_user_by_username(db, username)
	if not user:
		return False
	if not verify_password(password, user.hashed_password):
		return False
	return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
	to_encode = data.copy()
	if expires_delta:
		expire = datetime.now(timezone.utc) + expires_delta
	else:
		expire = datetime.now(timezone.utc) + timedelta(minutes=15)
	to_encode.update({"exp": expire})
	encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
	return encoded_jwt

def decode_token(token: str):
	try:
		return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
	except InvalidTokenError:
		return None