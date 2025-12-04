"""
This is the router for the user modual.

This handle login and user validation
"""

from pydantic import BaseModel

from typing import Annotated, Optional


from starlette.requests import Request


from datetime import timedelta
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError

from . import schemas, utils
from .. import dependencies
from ..database import SessionLocal

ACCESS_TOKEN_EXPIRE_MINUTES = 30


def get_db():
	try:
		db = SessionLocal()
		yield db
	finally:
		db.close()


router = APIRouter(
	prefix="/users",
	tags=["users"],
	responses={40: {"description": "Invalid"}},
)






@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
	request: Request,
	form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
	db=Depends(get_db)
):
	user = utils.authenticate_user(
		db, form_data.username, form_data.password
	)
	if not user:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Incorrect username or password",
			headers={"WWW-Authenticate": "Bearer"},
		)
	access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
	access_token = utils.create_access_token(
		data={"sub": user.username}, expires_delta=access_token_expires
	)
	request.session.update({"token": access_token})
	return schemas.Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=schemas.User)
async def read_users_me(
	current_user: Annotated[schemas.User, Depends(dependencies.get_current_active_user)],
):
	return schemas.User.model_validate(current_user)

@router.get("/isadmin", response_model=schemas.User)
async def read_user_isadmin(
	current_user: Annotated[schemas.User, Depends(dependencies.get_active_admin_user)],
):
	return schemas.User.model_validate(current_user)

@router.post("/logout")
async def post_logout(
	request: Request,
):
	request.session.clear()
	return {"success": True}