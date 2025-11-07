from typing import Annotated


from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from starlette.requests import Request

from .users import utils, schemas, crud
from .database import SessionLocal

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"


def get_db():
	try:
		db = SessionLocal()
		yield db
	finally:
		db.close()

async def get_current_user(request: Request, db = Depends(get_db)):
	credentials_exception = HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Could not validate credentials",
	)
	if not request.session:
		raise credentials_exception
	payload = utils.decode_token(request.session["token"])
	if payload is None:
		raise credentials_exception
	username: str = payload.get("sub")
	if username is None:
		raise credentials_exception
	token_data = schemas.TokenData(username=username)
	
	user = crud.get_user_by_username(db, username=token_data.username)
	if user is None:
		raise credentials_exception
	return user


async def get_current_active_user(
	current_user: Annotated[schemas.User, Depends(get_current_user)],
):
	if current_user.disabled:
		raise HTTPException(status_code=400, detail="Inactive user")
	return current_user