import logging, os

from sqlalchemy.orm import Session

from . import crud, models, schemas

from .. import constants

log = logging.getLogger(__name__)

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
					tag="default",
					active=True
				)
			)
	return True
