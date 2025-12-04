"""
Router for the admin tools such as clearing the log and output files
"""
import logging
import os
from typing import Annotated

from fastapi import APIRouter, Response, Depends

from . import crud, schemas, utils
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
	if utils.set_up_dirs():
		return Response(content="Setup dirs", media_type="text")
	else:
		return exceptions.internal_error

@router.post("/clearlog")
async def post_clearLog(
	current_user: Annotated[user_schemas.User, Depends(dependencies.get_active_admin_user)]
):
	if utils.clear_log():
		return Response(content="Cleared logs.", media_type="text")
	else:
		return exceptions.internal_error

@router.post("/clearoutput")
async def post_clearOutput(
	current_user: Annotated[user_schemas.User, Depends(dependencies.get_active_admin_user)]
):
	if utils.clear_output():
		return Response(content="Cleared output.", media_type="text")
	else:
		 return exceptions.internal_error

@router.get("/intsettings", response_model=list[schemas.IntSetting])
async def get_intsettings(
	current_user: Annotated[user_schemas.User, Depends(dependencies.get_current_active_user)],
	db = Depends(get_db)
):
	return crud.get_int_settings_by_privilege(db, current_user.privilege_level)

@router.post("/cleanall/{clear_log}/{rebuild_cache}")
async def post_cleanall(
	clear_log: bool,
	rebuild_cache: bool,
	current_user: Annotated[user_schemas.User, Depends(dependencies.get_current_active_user)],
	db = Depends(get_db)
):
	return utils.clean_all(db, clear_log, rebuild_cache)