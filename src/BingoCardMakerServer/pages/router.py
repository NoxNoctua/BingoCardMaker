"""
Router for the pages modual that generates and returns the various html files and pages
"""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse


router = APIRouter(
	prefix="",
	tags=["pages"],
)

@router.get("/", response_class=HTMLResponse)
async def generate_homepage_response():
	with open("src/BingoCardMakerServer/MountedStatic/index.html") as f:
		return f.read()

@router.get("/login", response_class=HTMLResponse)
async def generate_login_response():
	with open("src/BingoCardMakerServer/MountedStatic/login.html") as f:
		return f.read()


