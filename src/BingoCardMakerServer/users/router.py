"""
This is the router for the user modual.

This handle login and user validation
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

from typing import Annotated, Optional


from starlette.requests import Request

router = APIRouter(
	prefix="/users",
	tags=["users"],
)

# MARK: temp sec

fake_users_db = {
	"johndoe": {
		"username": "johndoe",
		"full_name": "John Doe",
		"email": "johndoe@example.com",
		"hashed_password": "fakehashedsecret",
		"disabled": False,
	}
}

def fake_hash_password(password: str):
	return "fakehashed" + password

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class User(BaseModel):
	username: str
	email: str | None = None
	full_name: str | None = None
	disabled: bool | None = None

class UserInDB(User):
	hashed_password: str

def get_user(db, username: str):
	if username in db:
		user_dict = db[username]
		return UserInDB(**user_dict)

def fake_decode_token(token):
	user=get_user(fake_users_db, token)
	return user

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
	user = fake_decode_token(token)
	if not user:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Invalid authentication credentials",
			headers={"WWW-Authenticate": "Bearer"}
		)
	return user

async def get_current_active_user(
	current_user: Annotated[User, Depends(get_current_user)],
):
	if current_user.disabled:
		raise HTTPException(status_code=400, detail="Inactive user")
	return current_user



# MARK: end temp sec

# MARK: temp sec calls
@router.post("/token")
async def login(
	request: Request,
	form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
	):
	user_dict = fake_users_db.get(form_data.username)
	if not user_dict:
		raise HTTPException(status_code=400, detail="Incorrect username or password")
	user = UserInDB(**user_dict)
	hashed_password = fake_hash_password(form_data.password)
	if not hashed_password == user.hashed_password:
		raise HTTPException(status_code=400, detail="Incorrect username or password")
	print(f"login in as: {user.username}")

	request.session.update({"token": user.username})

	return {"access_token": user.username, "token_type": "Bearer"}

@router.get("/me")
async def read_users_me(
	request: Request,
):
	print(request.session)
	if not request.session:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Not session token"
		)
	return request.session
# MARK: end temp sec calls
