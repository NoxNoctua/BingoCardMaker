"""
Router for managing the image pool
"""
import logging
import os, io
from typing import Annotated

from fastapi import APIRouter, Response, Depends, Form, UploadFile, File
from fastapi.responses import FileResponse


from . import schemas, crud, utils
from ..database import SessionLocal
from ..exceptions import image_path_not_in_db, bad_image_file
from .. import constants
from ..cardgen.makermanager import maker_manager


log = logging.getLogger(__name__)

def get_db():
	try:
		db = SessionLocal()
		yield db
	finally:
		db.close()



router = APIRouter(
	prefix="/poolmanagment",
	tags=["pool_managment"],
)

@router.post("/updatedbfrompool")
def post_update_db_from_pool(db=Depends(get_db)) -> bool:
	result = utils.upload_pool_to_db(db)
	return result

@router.get("/allpoolimgs", response_model=list[schemas.PoolImage])
def get_all_pool_imgs(db=Depends(get_db)):
	return crud.get_all_images(db)

@router.get("/poolimgfrompath/{image_path:path}", response_class=FileResponse)
def get_pool_image_from_path(image_path: str, db=Depends(get_db)):
	image_in_db = crud.get_image_by_path(db,image_path)
	if image_in_db is not None:
		return FileResponse(image_path)
	else:
		raise image_path_not_in_db

@router.get("/poolimgthumbfrompath/{thumb_path:path}", response_class=FileResponse)
def get_pool_img_thumb_from_path(thumb_path: str, db=Depends(get_db)):
	image_in_db = crud.get_image_by_path(
		db,
		os.path.join(
			constants.POOL_PATH,
			os.path.basename(thumb_path)
		)
	)
	if image_in_db is not None:
		return FileResponse(thumb_path)
	else:
		raise image_path_not_in_db

@router.get("/poolimgtags")
def get_pool_img_tags(db=Depends(get_db)) -> list[str]:
	return crud.get_all_tags(db)

@router.post("/uploadimg")
async def post_upload_pool_img(
	data: Annotated[schemas.UploadImageForm, Form(media_type="multipart/form-data")],
	db=Depends(get_db)
):
	log.info(f"Got file with name {data.file.filename}")
	log.debug(f"name: {data.name} | tag: {data.tag} | active: {data.active} | type: {data.file.content_type}")

	image_path = os.path.join(constants.RESOURCE_PATH, data.file.filename)
	if data.for_pool:
		image_path = os.path.join(constants.POOL_PATH, data.file.filename)

	# TODO fixcheck for file type
	if data.file.content_type == "image/png":
		with open(image_path, "wb") as out_file:
			while content := await data.file.read(1024):
				out_file.write(content)
	else:
		return bad_image_file
	

	image_in_db = crud.get_image_by_path(db,image_path)
	if image_in_db is not None:
		crud.update_image_data(
			db,
			schemas.UpdateImageForm.model_validate(data)
		)
	else:
		crud.add_image_to_db(
			db,
			schemas.PoolImage(
				name=data.name,
				tag=data.tag,
				active=data.active,
				file_path=image_path
			)
		)

	return {"Result": "OK"}

@router.post("/rebuildthumbnails")
def post_rebuildthumbnails():
	utils.recreate_thumbnails()

@router.post("/toggletile/{name}/{value}")
def post_toggle_tile(name: str, value: bool, db=Depends(get_db)):
	crud.set_tile_toggle(db,name,value)

@router.post("/updateactivepool")
def post_update_active_pool(db=Depends(get_db)):
	maker_manager.set_pool_by_tag(db, "default")
 