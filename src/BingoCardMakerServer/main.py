import os

import logging

from typing import Annotated, Optional

from fastapi import FastAPI, Response, HTTPException, status, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request


from bingocardmaker import bingocard

from logger.logger import Logger

from .users.router import router as user_router
from .pages.router import router as page_router
from .admintools.router import router as admintools_router

log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())
log.addHandler(logging.FileHandler(
	filename="log.txt",
	mode="a",
	encoding="utf-8"
))


RESOURCE_PATH = os.path.join(".", "resources")
POOL_PATH = os.path.join(RESOURCE_PATH, "pool")
OUTPUT_PATH = os.path.join(RESOURCE_PATH, "output")
LOG_PATH = "log.txt"



# MARK: MakerServer
class MakerServer:
	card: bingocard.BingoCard = bingocard.BingoCard()
	cardNum: int = 0


	def __init__(self):
		pass

	def genCard(self, fileType: str ="PNG") -> (str, int):
		log.info(f"Generating card: {self.cardNum}")
		path = self.card.genCard(id=self.cardNum, fileType=fileType)
		
		self.cardNum += 1

		return (path, self.cardNum-1)


app = FastAPI()

app.mount("/s", StaticFiles(directory="src/BingoCardMakerServer/MountedStatic"), name="static")

origins = [
	"http://localhost",
	"http://localhost:8000",
	"http://localhost:8080",
]

app.add_middleware(
	CORSMiddleware,
	allow_origins=origins,
	allow_credentials=True,
	allow_methods=["GET", "POST"],
	allow_headers=["Set-Cookie"],
	expose_headers=["Set-Cookie"]
)

app.add_middleware(
	SessionMiddleware,
	same_site="lax",
	session_cookie="session",
	secret_key="mysecret"
)

app.include_router(user_router)
app.include_router(page_router)
app.include_router(admintools_router)

makerServer = MakerServer()





# Managment
# TODO move this to a router
# MARK: management

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
