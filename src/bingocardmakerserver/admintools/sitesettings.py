import logging
from . import crud, schemas


log = logging.getLogger(__name__)



"""
Holds setting related to the sites operation such as paths to resources,
how many cards to keep before deleting old ones, base url and url's 
for other pages, etc.
"""
class SiteSettings:
	
	
	def __init__(self):
		log.debug("Initing SiteSettings")

		# Str Settings
		self.site_title: str = "Bingo Maker Default"
		self.site_url: str = "http://localhost:8000"
		self.resources_dir_path: str = "./resources"
		

		# Int Settings
		self.max_number_of_cards_to_hold: int = 20


	"""
	using this class as a dictionary save all of its atributes to the db
	"""
	def save_settings_to_db(self, db):
		log.info("Saving site settings to database")
		settings = vars(self)
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
		for name, value in vars(self).items():
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


site_settings = SiteSettings()