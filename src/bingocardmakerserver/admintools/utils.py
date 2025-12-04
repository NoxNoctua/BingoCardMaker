import os, logging

from ..cardgen.makermanager import maker_manager
from ..poolmanagment import utils as poolmanagment_utils
from ..poolmanagment import crud as poolmanagment_crud

from .. import constants

log = logging.getLogger(__name__)

"""
creates the directories for the server resources
"""
def set_up_dirs():
	try:
		log.info("setting up dirs")
		if not os.path.exists(constants.RESOURCE_PATH):
			os.makedirs(constants.RESOURCE_PATH)
		if not os.path.exists(constants.POOL_PATH):
			os.makedirs(constants.POOL_PATH)
		if not os.path.exists(constants.OUTPUT_PATH):
			os.makedirs(constants.OUTPUT_PATH)
		if not os.path.exists(constants.THUMBNAIL_PATH):
			os.makedirs(constants.THUMBNAIL_PATH)
	except Exception as e:
		log.exception("Failed to set up server dirs")
	finally:
		log.info("Setup dirs")

"""
Deletes the log file
"""
def clear_log() -> bool:
	try:
		log.info("Clearing log")
		if os.path.exists(constants.LOG_PATH):
			os.remove(constants.LOG_PATH)
		log.info("Cleared log")
		return True
	except Exception as e:
		log.exception("Failed to remove log.txt")
		return False

"""
deletes all files in the output directory
"""
def clear_output() -> bool:
	try:
		log.info("Clearing output")
		with os.scandir(constants.OUTPUT_PATH) as outDir:
			for e in outDir:
				log.debug(e.name)
				os.remove(e.path)
		log.info("Cleared output")
		return True
	except Exception as e:
		log.exception("Failed to clear output dir")
		return False

"""
Cleans all cache and generated files, removes incomplete or missing infomation from database
"""
def clean_all(db, clear_logs=False, rebuild_cache=False) -> bool:
	try:
		log.info("cleaning all")

		set_up_dirs()

		# remove image files that are not in the database
		# TODO ^
		# remove database entries that do not have a file image
		poolmanagment_crud.remove_missing_images(db)

		# remove thumbnails
		poolmanagment_utils.clear_thumbnails()

		# remove output
		clear_output()

		# remove log
		if clear_logs:
			clear_log()

		# reset cardnumber
		maker_manager.card_num = 0

		# reload pool
		maker_manager.refresh_pool(db)

		# rebuild thumbnails
		if rebuild_cache:
			poolmanagment_utils.recreate_thumbnails()
		
		log.info("################## Cleaned #######################")
		return True

	except Exception as e:
		log.exception("Failed clean all")
		return False