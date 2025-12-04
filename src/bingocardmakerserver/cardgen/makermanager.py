import logging

from bingocardmaker import bingocard

from . import crud, schemas
from ..poolmanagment import crud as poolcrud

log = logging.getLogger(__name__)

class MakerManager:
	
	def __init__(self):
		log.debug("initlizing makermanager")
		self.card: bingocard.BingoCard = bingocard.BingoCard()
		self.card_num: int = 0
		self.pool = []
		self.active_tags = ["default"]

	def genCard(self, fileType: str ="PNG") -> (str, int):
		log.info(f"Generating card: {self.card_num}")
		path = self.card.genCard(pool=self.pool, id=self.card_num, fileType=fileType)
		
		self.card_num += 1

		return (path, self.card_num-1)
	
	def refresh_pool(self, db) -> bool:
		try:
			log.info("Refreshing pool")
			self.pool = []
			for tag in self.active_tags:
				db_pool = poolcrud.get_images_by_tag(db, tag)
				for t in db_pool:
					if t.use_type == "pool":
						t.path = t.file_path
						self.pool.append(t)
			# TODO remove duplicate entries when there are multiple selected tags
			log.info("pool refreshed")
		except Exception as e:
			log.exception("Failed to refresh_pool")

	def set_pool_by_tag(self, db, tag:str):
		self.active_tags = []
		self.active_tags.append(tag)
		self.refresh_pool(db)

	#TODO add additional tags

	"""
	using this class as a dictionary save all of its atributes to the db
	"""
	def save_settings_to_db(self, db):
		log.info("Saving site settings to database")
		settings = vars(self.card)
		for name, value in settings.items():
			if type(value) == int:
				crud.set_int_setting(db, name, value)
			elif type(value) == str:
				crud.set_str_setting(db, name, value)
			elif type(value) == bool:
				crud.set_str_setting(db, name, value)
	
	"""
	clears the db of current settings and adds the settings currently in this intance
	"""
	def init_saved_settings(self, db):
		crud.clear_int_settings(db)
		crud.clear_str_settings(db)
		for name, value in vars(self.card).items():
			if type(value) == int:
				setting = schemas.IntSetting(
					name=name,
					value=value,
					required_privilege_level=0
				)
				crud.add_int_setting(
					db,
					setting
				)
			elif type(value) == str:
				crud.add_str_setting(
					db,
					schemas.StrSetting(
						name=name,
						value=value,
						required_privilege_level=0
					)
				)
			elif type(value) == bool:
				crud.add_bool_setting(
					db,
					schemas.BoolSetting(
						name=name,
						value=value,
						required_privilege_level=0
					)
				)

	"""
	loads the card config from the database
	"""
	def load_settings_from_db(self, db):
		log.info("Loading card config from database")
		# int settings
		database_int_settings = crud.get_int_settings_by_privilege(db, -1)

		for int_setting in database_int_settings:
			log.debug(f"setting {int_setting.name} to {int_setting.value}")
			setattr(self.card, int_setting.name, int_setting.value)

		# str settings
		database_str_settings = crud.get_str_settings_by_privilege(db, -1)

		for str_setting in database_str_settings:
			log.debug(f"setting {str_setting.name} to {str_setting.value}")
			setattr(self.card, str_setting.name, str_setting.value)

		# bool settings
		database_bool_settings = crud.get_bool_settings_by_privilege(db, -1)

		for bool_setting in database_bool_settings:
			log.debug(f"setting {bool_setting.name} to {bool_setting.value}")
			setattr(self.card, bool_setting.name, bool_setting.value)

	"""
	returns a json list of bool settings and their current values based on priv level
	"""
	def get_bool_values(self, db, privilege_level):
		from_db = crud.get_bool_settings_by_privilege(db, privilege_level)

		return_list = []

		for setting in from_db:
			current_value = getattr(self.card, setting.name)
			setting.value = current_value
			return_list.append(setting)
		
		return return_list

	"""
	returns a json list of str settings and their current values based on priv level
	"""
	def get_str_values(self, db, privilege_level):
		from_db = crud.get_str_settings_by_privilege(db, privilege_level)

		return_list = []

		for setting in from_db:
			current_value = getattr(self.card, setting.name)
			setting.value = current_value
			return_list.append(setting)
		
		return return_list

	"""
	returns a json list of int settings and their current values based on priv level
	"""
	def get_int_values(self, db, privilege_level):
		from_db = crud.get_int_settings_by_privilege(db, privilege_level)

		return_list = []

		for setting in from_db:
			current_value = getattr(self.card, setting.name)
			setting.value = current_value
			return_list.append(setting)
		
		return return_list

maker_manager = MakerManager()