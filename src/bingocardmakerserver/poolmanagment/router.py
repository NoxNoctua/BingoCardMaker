"""
Router for managing the image pool
"""
import logging
import os, io
from typing import Annotated

from fastapi import APIRouter, Response, Depends, Form, UploadFile, File, status
from fastapi.responses import FileResponse, RedirectResponse


from . import schemas, crud, utils
from ..database import SessionLocal
from ..exceptions import image_path_not_in_db, bad_image_file
from .. import constants, exceptions, dependencies
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
	dependencies=[Depends(dependencies.get_active_admin_user)],
)

@router.post("/updatedbfrompool")
def post_update_db_from_pool(db=Depends(get_db)) -> bool:
	if utils.upload_pool_to_db(db):
		return True
	else:
		return exception.internal_error

@router.get("/allpoolimgs", response_model=list[schemas.PoolImage])
def get_all_pool_imgs(db=Depends(get_db)):
	images = crud.get_all_images(db)
	images.sort(key=lambda x: x.name)
	return images

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

@router.get("/poolimgthumbbyname/{thumb_name}", response_class=FileResponse)
def get_pool_img_thumb_by_name(thumb_name: str, db=Depends(get_db)):
	image_in_db = crud.get_image_by_name(db, thumb_name)
	if image_in_db is not None:
		return FileResponse(
			os.path.join(constants.THUMBNAIL_PATH, thumb_name)
		)
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
	log.debug(f"name: {data.name} | tag: {data.tag} | active: {data.active} | type: {data.file.content_type} | use: {data.use_type}")

	data.name = data.file.filename

	image_path = os.path.join(constants.POOL_PATH, data.file.filename)

	# TODO fixcheck for file type to allow more / configured options
	if data.file.content_type == "image/png":
		with open(image_path, "wb") as out_file:
			while content := await data.file.read(1024):
				out_file.write(content)
	else:
		return bad_image_file
	
	image_in_db = crud.get_image_by_name(db,data.name)
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
				file_path=image_path,
				use_type=data.use_type,
				thumbnail_path=os.path.join(constants.THUMBNAIL_PATH, data.name)
			)
		)
	
	utils.create_thumbnail(image_path)

	if data.use_type == "freespace":
		maker_manager.card.freespaceImagePath = image_path
		maker_manager.save_settings_to_db(db)
	if data.use_type == "base":
		maker_manager.card.baseImagePath = image_path
		maker_manager.save_settings_to_db(db)

	return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/delete/{image_path:path}")
async def post_delete_image(image_path: str, db = Depends(get_db)):
	path = os.path.join(
		constants.POOL_PATH,
		os.path.basename(image_path)
	)
	image_in_db = crud.get_image_by_path(db,path)
	if image_in_db is not None:
		return crud.delete_image_in_db(db, path)
	else:
		raise image_path_not_in_db

@router.post("/rebuildthumbnails")
def post_rebuildthumbnails():
	utils.recreate_thumbnails()

@router.post("/cleardbofmissingimages")
def post_clear_db_of_missing_images(db = Depends(get_db)):
	if not crud.remove_missing_images(db):
		return exceptions.internal_error

@router.post("/toggletile/{name}/{value}")
def post_toggle_tile(name: str, value: bool, db=Depends(get_db)):
	crud.set_tile_toggle(db,name,value)

@router.post("/updateactivepool/{tag}")
def post_update_active_pool(tag: str, db=Depends(get_db)):
	maker_manager.set_pool_by_tag(db, tag)

@router.post("/updateusetype/{name}/{value}")
def post_update_use_type(name: str, value: str, db=Depends(get_db)):
	crud.update_use_type(db, name, value)