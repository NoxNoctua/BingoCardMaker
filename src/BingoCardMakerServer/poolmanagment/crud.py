import logging

from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import select, delete

from . import models, schemas

log = logging.getLogger(__name__)

"""
Add an image to the database
"""
def add_image_to_db(db:Session,image: schemas.PoolImage) -> bool:
	log.debug(f"adding image {image.name} to db")
	try:
		new_image = models.PoolImage(
			name=image.name,
			file_path=image.file_path,
			tag=image.tag,
			active=image.active
		)
		db.add(new_image)
		db.commit()
		return True
	except Exception as e:
		log.exception("Could not add image to db")
		return False

"""
Get image data from file path
"""
def get_image_by_path(db:Session, path:str) -> Optional[models.PoolImage]:
	log.debug(f"looking for image {path}")
	try:
		img = db.scalars(
			select(models.PoolImage)
			.where(models.PoolImage.file_path==path)
		).first()

		if img is not None:
			return img
		else:
			return None
	except Exception as e:
		log.exception("Could not search image in db")
		return None

"""
Get list of images in db
"""
def get_all_images(db: Session) -> Optional[list[models.PoolImage]]:
	log.debug("getting all images")
	try:
		imgs = db.scalars(
			select(models.PoolImage)
		).all()
		return imgs
	except Exception as e:
		log.exception("Could not get all images from db")
		return None



"""
Get list of image tags in db
"""
def get_all_tags(db: Session) -> Optional[list[str]]:

	log.debug("getting all tags")
	try:
		tags = db.scalars(
			select(models.PoolImage.tag)
		).unique()
		return tags
	except Exception as e:
		log.exception("Could not get all tags from db")
		return None


"""
Upadte image information
"""
def update_image_data(db: Session, img: schemas.UpdateImageForm) -> bool:

	log.debug(f"updating image {img.name}")
	try:
		img_in_db = db.scalars(
			select(models.PoolImage)
			.where(models.PoolImage.name == img.name)
		).one_or_none()

		if img_in_db is None:
			return False
		
		img_in_db.name=img.name
		img_in_db.tag=img.tag
		img_in_db.active=img.active

		db.commit()
		return True
	except Exception as e:
		log.exception("Could not update imgage infomation")
		return False
