import os

from fastapi import FastAPI, Response
from fastapi.responses import FileResponse

from bingocardmaker import bingocard

from logger.logger import Logger

log = Logger()

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
		log.tags.append("MakerServer_genCard")
		
		path = self.card.genCard(id=self.cardNum, fileType=fileType)
		
		self.cardNum += 1
		log.tags.pop()

		return (path, self.cardNum-1)


app = FastAPI()

makerServer = MakerServer()

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
