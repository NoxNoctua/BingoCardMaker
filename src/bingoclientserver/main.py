from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def generate_homepage_response():
	with open("src/bingoclientserver/htmlpages/index.html") as f:
		return f.read()

@app.get("/login", response_class=HTMLResponse)
async def generate_login_response():
	with open("src/bingoclientserver/htmlpages/login.html") as f:
		return f.read()