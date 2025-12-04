import logging, os

from sqlalchemy.orm import Session

from PIL import Image

from . import crud, models, schemas

from .. import constants

log = logging.getLogger(__name__)

"""
Scans the pool directory and adds any untracked images to the database.
"""
def upload_pool_to_db(db: Session):
	log.info("Updating database with pool images")
	# get all images in pool
	pool = []

	file_endings = []
	for i in constants.POOL_IMAGES_FILE_ENDINGS:
		file_endings.append("."+i.lower())
	file_endings = tuple(file_endings)

	try:
		with os.scandir(constants.POOL_PATH) as pool_dir:
			for e in pool_dir:
				log.debug(f"Found image {e.path}")
				if e.name.endswith(file_endings):
					pool.append(e)
	except Exception as e:
		log.exception("Could not scan pool dir")
		raise Exception()
	# for each image if it is alread in db ignore

	for img_path in pool:
		img_in_db = crud.get_image_by_path(db, img_path.path)
		
		# otherwise upload to db with default tags
		if img_in_db is None:
			crud.add_image_to_db(
				db,
				schemas.PoolImage(
					name=img_path.name,
					file_path=img_path.path,
					thumbnail_path=os.path.join(constants.THUMBNAIL_PATH, img_path.name),
					tag="default",
					active=True
				)
			)
			create_thumbnail(img_path.path)
	return True

"""
Takes image path resized it to thumbnail size and saves it to thumbnails then returns thumbnail path
"""
def create_thumbnail(image_path: str) -> str:
	size = 64, 64
	try:
		with Image.open(image_path) as img:
			img.thumbnail(size)
			thumbnail_path = os.path.join(
				constants.THUMBNAIL_PATH,
				os.path.basename(image_path)
			)
			log.debug(f"making thumbnail {thumbnail_path}")
			img.save(thumbnail_path)
	except Exception as e:
		log.exception(e)

"""
Clears thumbnail dir and recreates all pool image thumbnails
"""
def recreate_thumbnails() -> None:
	try:
		log.info("Clearning Thumbnail dir")
		with os.scandir(constants.THUMBNAIL_PATH) as thumb_path:
			for thumb in thumb_path:
				log.debug(thumb.name)
				os.remove(thumb.path)
	except Exception as e:
		log.error("Failed to clear Thumbnail dir")
		log.exception(e)
	
	log.info("Rebuilding Thumbnails")
	try:
		with os.scandir(constants.POOL_PATH) as pool_dir:
			for img_path in pool_dir:
				create_thumbnail(img_path.path)
	except Exception as e:
		log.exception(e)