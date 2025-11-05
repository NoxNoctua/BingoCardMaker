import os

from typing import Annotated

from fastapi import FastAPI, Response, HTTPException, status, Depends
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


from bingocardmaker import bingocard

from logger.logger import Logger

log = Logger()

RESOURCE_PATH = os.path.join(".", "resources")
POOL_PATH = os.path.join(RESOURCE_PATH, "pool")
OUTPUT_PATH = os.path.join(RESOURCE_PATH, "output")
LOG_PATH = "log.txt"


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
# MARK: MakerServer
class MakerServer:
	card: bingocard.BingoCard = bingocard.BingoCard()
	cardNum: int = 0


	def __init__(self):
		pass

	def genCard(self, fileType: str ="PNG") -> (str, int):
		log.tags.append("MakerServer_genCard")
		
		path = self.card.genCard(id=self.cardNum, fileType=fileType)
		
		self.cardNum += 1
		log.tags.pop()

		return (path, self.cardNum-1)


app = FastAPI()

origins = [
	"*",
]

app.add_middleware(
	CORSMiddleware,
	allow_origins=origins,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)
makerServer = MakerServer()

# MARK: temp sec calls
@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
	user_dict = fake_users_db.get(form_data.username)
	if not user_dict:
		raise HTTPException(status_code=400, detail="Incorrect username or password")
	user = UserInDB(**user_dict)
	hashed_password = fake_hash_password(form_data.password)
	if not hashed_password == user.hashed_password:
		raise HTTPException(status_code=400, detail="Incorrect username or password")
	print(f"login in as: {user.username}")
	return {"access_token": user.username, "token_type": "Bearer"}

@app.get("/users/me")
async def read_users_me(
	current_user: Annotated[User, Depends(get_current_active_user)],
):
	return current_user
# MARK: end temp sec calls


@app.get("/")
def root():
	return Response(content="This is bingo car maker root", media_type="text")

# Managment
# TODO move this to a router
# MARK: management
@app.post("/management/setupdir")
async def api_setUpDir():
	setUpDir()
	return Response(content="Setup dirs", media_type="text")

@app.post("/management/clearlog")
async def post_clearLog():
	clearLog()
	return Response(content="Cleared logs.", media_type="text")

@app.post("/management/clearoutput")
async def post_clearOutput():
	clearOutput()
	return Response(content="Cleared output.", media_type="text")

# puzzle
# TODO move this to a router
# MARK: puzzle
@app.get("/puzzle/genpng")
async def get_genPuzzlePNG():
	path, id = makerServer.genCard(fileType="PNG")
	#return Response(content=path, media_type="text")
	return FileResponse(path)

@app.get("/puzzle/genpdf")
async def get_genPuzzlePDF():
	path, id = makerServer.genCard(fileType="PDF")
	#return Response(content=path, media_type="text")
	return FileResponse(path)




# MARK: managment Content
# sets up the resource paths for the pool and output
def setUpDir():
	log.tags.append("setUpDir")
	try:
		if not os.path.exists(RESOURCE_PATH):
			os.makedirs(RESOURCE_PATH)
		if not os.path.exists(POOL_PATH):
			os.makedirs(POOL_PATH)
		if not os.path.exists(OUTPUT_PATH):
			os.makedirs(OUTPUT_PATH)
	except Exception as e:
		log.err("Failed to set up server dirs")
		log.err(str(e))
	finally:
		log.tags.pop()

# Deletes the log.txt file
def clearLog():
	log.tags.append("clearLog")
	try:
		if os.path.exists(LOG_PATH):
			os.remove(LOG_PATH)
	except Exception as e:
		log.err("Failed to remove log.txt")
		log.err(str(e))
	log.tags.pop()

def clearOutput():
	log.tags.append("clearOutput")
	try:
		with os.scandir(OUTPUT_PATH) as outDir:
			for e in outDir:
				log.dbg(e.name)
				os.remove(e.path)
	except Exception as e:
		log.err("Failed to clear output dir")
		log.err(str(e))
	log.tags.pop()
