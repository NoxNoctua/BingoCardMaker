"""
Router for the generating of bingo cards such as clearing the log and output files
"""
import logging
import os
from typing import Annotated

from fastapi import APIRouter, Response, Depends
from fastapi.responses import FileResponse


from . import schemas, crud
from ..database import SessionLocal
from .makermanager import maker_manager


log = logging.getLogger(__name__)

def get_db():
	try:
		db = SessionLocal()
		yield db
	finally:
		db.close()



router = APIRouter(
	prefix="/cardgen",
	tags=["cardgen"],
)







# MARK: puzzle
@router.get("/genpng")
async def get_genPuzzlePNG(db = Depends(get_db)):
	if len(maker_manager.pool) == 0:
		maker_manager.set_pool_by_tag(db, "default")
	path, id = maker_manager.genCard(fileType="PNG")
	return FileResponse(path)

@router.get("/genpdf")
async def get_genPuzzlePDF(db = Depends(get_db)):
	if len(maker_manager.pool) == 0:
		maker_manager.set_pool_by_tag(db, "default")
	path, id = maker_manager.genCard(fileType="PDF")
	return FileResponse(path)

# TODO add admin check
@router.post("/loadconfig")
async def post_loadconfig(db = Depends(get_db)):
	maker_manager.load_settings_from_db(db)

@router.get("/intsettings", response_model=list[schemas.IntSetting])
async def get_intsettings(
	db = Depends(get_db)
):
	return maker_manager.get_int_values(db, 0)

@router.get("/strsettings", response_model=list[schemas.StrSetting])
async def get_strsettings(
	db = Depends(get_db)
):
	return maker_manager.get_str_values(db, 0)

@router.get("/boolsettings", response_model=list[schemas.BoolSetting])
async def get_boolsettings(
	db = Depends(get_db)
):
	return maker_manager.get_bool_values(db, 0)


@router.post("/setbool/{name}/{value}")
async def post_setbool(name:str, value:bool, db = Depends(get_db)):
	setattr(maker_manager.card, name, value)
