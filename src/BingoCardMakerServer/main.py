import os
import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

import uvicorn

from .users.router import router as user_router
from .pages.router import router as page_router
from .admintools.router import router as admintools_router
from .cardgen.router import router as cardgen_router

# MARK: Setting up logging

class CustomFormatter(logging.Formatter):
	grey = '\x1b[38;21m'
	blue = '\x1b[38;5;39m'
	yellow = '\x1b[38;5;226m'
	red = '\x1b[38;5;196m'
	bold_red = '\x1b[31;1m'
	reset = '\x1b[0m'

	def __init__(self, fmt):
		super().__init__()
		self.fmt = fmt
		self.FORMATS = {
			logging.DEBUG: self.grey + self.fmt + self.reset,
			logging.INFO: self.blue + self.fmt + self.reset,
			logging.WARNING: self.yellow + self.fmt + self.reset,
			logging.ERROR: self.red + self.fmt + self.reset,
			logging.CRITICAL: self.bold_red + self.fmt + self.reset,
		}
	
	def format(self, record):
		log_fmt = self.FORMATS.get(record.levelno)
		formatter = logging.Formatter(log_fmt)
		return formatter.format(record)

project_root_log = logging.getLogger("bingocardmakerserver")
lib_log_root = logging.getLogger("bingocardmaker")

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

log = logging.getLogger(__name__)


formatter = CustomFormatter(
	fmt="%(levelname)s:\t %(name)s %(message)s"
)
console_handler.setFormatter(formatter)

project_root_log.addHandler(console_handler)
project_root_log.setLevel(logging.DEBUG)

lib_log_root.addHandler(console_handler)
lib_log_root.setLevel(logging.DEBUG)

# MARK: Setting up app

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
app.include_router(cardgen_router)
