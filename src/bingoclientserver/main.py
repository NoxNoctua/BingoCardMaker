from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware


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

app.mount("/s", StaticFiles(directory="src/bingoclientserver/static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def generate_homepage_response():
	with open("src/bingoclientserver/htmlpages/index.html") as f:
		return f.read()

@app.get("/login", response_class=HTMLResponse)
async def generate_login_response():
	with open("src/bingoclientserver/htmlpages/login.html") as f:
		return f.read()

@app.get("/authServiceWorker", response_class=FileResponse)
async def provide_serviceworker():
	return FileResponse("src/bingoclientserver/static/authServiceWorker.js")