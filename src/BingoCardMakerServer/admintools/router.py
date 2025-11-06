"""
Router for the admin tools such as clearing the log and output files
"""
import logging
import os
from fastapi import APIRouter, Response

log = logging.getLogger(__name__)

router = APIRouter(
	prefix="/admintools",
	tags=["admintools"],
)

@router.post("/setupdir")
async def api_setUpDir():
	setUpDir()
	return Response(content="Setup dirs", media_type="text")

@router.post("/clearlog")
async def post_clearLog():
	clearLog()
	return Response(content="Cleared logs.", media_type="text")

@router.post("/clearoutput")
async def post_clearOutput():
	clearOutput()
	return Response(content="Cleared output.", media_type="text")


def setUpDir():
	try:
		if not os.path.exists(RESOURCE_PATH):
			os.makedirs(RESOURCE_PATH)
		if not os.path.exists(POOL_PATH):
			os.makedirs(POOL_PATH)
		if not os.path.exists(OUTPUT_PATH):
			os.makedirs(OUTPUT_PATH)
	except Exception as e:
		log.error("Failed to set up server dirs")
		log.error(str(e))
	finally:
		log.info("Setup dirs")

# Deletes the log.txt file
def clearLog():
	try:
		if os.path.exists(LOG_PATH):
			os.remove(LOG_PATH)
	except Exception as e:
		log.error("Failed to remove log.txt")
		log.error(str(e))
	log.info("Cleared log")

def clearOutput():
	try:
		with os.scandir(OUTPUT_PATH) as outDir:
			for e in outDir:
				log.debug(e.name)
				os.remove(e.path)
	except Exception as e:
		log.error("Failed to clear output dir")
		log.error(str(e))
