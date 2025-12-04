"""
Router for the admin tools such as clearing the log and output files
"""
import logging
import os
from typing import Annotated

from fastapi import APIRouter, Response, Depends

from . import crud, schemas
from ..users import schemas as user_schemas
from .. import dependencies, exceptions, constants
from ..database import SessionLocal

log = logging.getLogger(__name__)




def get_db():
	try:
		db = SessionLocal()
		yield db
	finally:
		db.close()



router = APIRouter(
	prefix="/admintools",
	tags=["admintools"],
)

@router.post("/setupdir")
async def api_setUpDir(
	current_user: Annotated[user_schemas.User, Depends(dependencies.get_active_admin_user)]
):
	setUpDir()
	return Response(content="Setup dirs", media_type="text")

@router.post("/clearlog")
async def post_clearLog(
	current_user: Annotated[user_schemas.User, Depends(dependencies.get_active_admin_user)]
):
	clearLog()
	return Response(content="Cleared logs.", media_type="text")

@router.post("/clearoutput")
async def post_clearOutput(
	current_user: Annotated[user_schemas.User, Depends(dependencies.get_active_admin_user)]
):
	if clearOutput():
		return Response(content="Cleared output.", media_type="text")
	else:
		 return exceptions.internal_error

@router.get("/intsettings", response_model=list[schemas.IntSetting])
async def get_intsettings(
	current_user: Annotated[user_schemas.User, Depends(dependencies.get_current_active_user)],
	db = Depends(get_db)
):
	return crud.get_int_settings_by_privilege(db, current_user.privilege_level)



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

"""
deletes all files in the output directory
"""
def clearOutput() -> bool:
	try:
		with os.scandir(constants.OUTPUT_PATH) as outDir:
			for e in outDir:
				log.debug(e.name)
				os.remove(e.path)
		return True
	except Exception as e:
		log.exception("Failed to clear output dir")
		return False
