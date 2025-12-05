import logging

from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import select, delete

from . import models, schemas

log = logging.getLogger(__name__)


# MARK: Int
"""
Create new setting and add it to database
"""
def add_int_setting(db: Session, setting: schemas.IntSetting) -> Optional[models.IntSetting]:
	log.debug(f"Creating setting {setting}")
	try:
		new_setting = models.IntSetting(
			name=setting.name,
			value=setting.value,
			required_privilege_level=setting.required_privilege_level
		)
		db.add(new_setting)
		db.commit()
		#db.refresh(new_setting)
		return new_setting
	except Exception as e:
		log.exception("Could not add new setting")
		return None


"""
Find Int Setting in database and sets it value
"""
def set_int_setting(db: Session, name: str, value: int) -> bool:
	log.debug(f"Setting {name} to {value}")
	try:
		setting = db.scalars(
			select(models.IntSetting)
			.where(models.IntSetting.name==name)
		).one_or_none()
		if setting is not None:
			setting = value
			db.commit()
			return True
		else:
			return False
	except Exception as e:
		log.exception("Could not set setting")

"""
Fing Int setting in database
"""
def get_int_setting(db: Session, name: str) -> Optional[models.IntSetting]:
	log.debug(f"Getting setting {name}")
	try:
		setting = db.scalars(
			select(models.IntSetting)
			.where(models.IntSetting.name==name)
		).one_or_none()
		if setting is not None:
			return setting
		else:
			return None
	except Exception as e:
		log.exception("Could not find setting")
		return None

"""
Get all Int settings with privilege of given level or above
"""
def get_int_settings_by_privilege(db: Session, level: int) -> Optional[list[models.IntSetting]]:
	log.debug(f"Getting settings of level {level} or above")
	try:
		settings = db.scalars(
			select(models.IntSetting)
			.where(models.IntSetting.required_privilege_level>=level)
		).all()
		if settings is not None:
			return settings
		else:
			return None
	except Exception as e:
		log.exception("Could not find settings")
		return None

"""
Removes all int settings from the database
"""
def clear_int_settings(db: Session) -> bool:
	log.info("Clearing int settings database")
	try:
		db.execute(
			delete(models.IntSetting)
		)
		return True
	except Exception as e:
		log.exception("Could not clear table")
		return False


# MARK: string
"""
Create new setting and add it to database
"""
def add_str_setting(db: Session, setting: schemas.StrSetting) -> Optional[models.StrSetting]:
	log.debug(f"Creating setting {setting}")
	try:
		new_setting = models.StrSetting(
			name=setting.name,
			value=setting.value,
			required_privilege_level=setting.required_privilege_level
		)
		db.add(new_setting)
		db.commit()
		#db.refresh(new_setting)
		return new_setting
	except Exception as e:
		log.exception("Could not add new setting")
		return None


"""
Find Int Setting in database and sets it value
"""
def set_str_setting(db: Session, name: str, value: str) -> bool:
	log.debug(f"Setting {name} to {value}")
	try:
		setting = db.scalars(
			select(models.StrSetting)
			.where(models.StrSetting.name==name)
		).one_or_none()
		if setting is not None:
			setting.value = value
			db.commit()
			return True
		else:
			log.warn(f"Could not find setting {name}")
			return False
	except Exception as e:
		log.exception("Could not set setting")

"""
Fing Int setting in database
"""
def get_str_setting(db: Session, name: str) -> Optional[models.StrSetting]:
	log.debug(f"Getting setting {name}")
	try:
		setting = db.scalars(
			select(models.StrSetting)
			.where(models.StrSetting.name==name)
		).one_or_none()
		if setting is not None:
			return setting
		else:
			return None
	except Exception as e:
		log.exception("Could not find setting")
		return None

"""
Get all Int settings with privilege of given level or above
"""
def get_str_settings_by_privilege(db: Session, level: str) -> Optional[list[models.StrSetting]]:
	log.debug(f"Getting settings of level {level} or above")
	try:
		settings = db.scalars(
			select(models.StrSetting)
			.where(models.StrSetting.required_privilege_level>=level)
		).all()
		if settings is not None:
			return settings
		else:
			return None
	except Exception as e:
		log.exception("Could not find settings")
		return None

"""
Removes all str settings from the database
"""
def clear_str_settings(db: Session) -> bool:
	log.info("Clearing str settings database")
	try:
		db.execute(
			delete(models.StrSetting)
		)
		return True
	except Exception as e:
		log.exception("Could not clear table")
		return False


# MARK: Bool
"""
Create new setting and add it to database
"""
def add_bool_setting(db: Session, setting: schemas.BoolSetting) -> Optional[models.BoolSetting]:
	log.debug(f"Creating setting {setting}")
	try:
		new_setting = models.BoolSetting(
			name=setting.name,
			value=setting.value,
			required_privilege_level=setting.required_privilege_level
		)
		db.add(new_setting)
		db.commit()
		#db.refresh(new_setting)
		return new_setting
	except Exception as e:
		log.exception("Could not add new setting")
		return None


"""
Find Int Setting in database and sets it value
"""
def set_bool_setting(db: Session, name: str, value: bool) -> bool:
	log.debug(f"Setting {name} to {value}")
	try:
		setting = db.scalars(
			select(models.BoolSetting)
			.where(models.BoolSetting.name==name)
		).one_or_none()
		if setting is not None:
			setting = value
			db.commit()
			return True
		else:
			return False
	except Exception as e:
		log.exception("Could not set setting")

"""
Fing Int setting in database
"""
def get_bool_setting(db: Session, name: str) -> Optional[models.BoolSetting]:
	log.debug(f"Getting setting {name}")
	try:
		setting = db.scalars(
			select(models.BoolSetting)
			.where(models.BoolSetting.name==name)
		).one_or_none()
		if setting is not None:
			return setting
		else:
			return None
	except Exception as e:
		log.exception("Could not find setting")
		return None

"""
Get all Int settings with privilege of given level or above
"""
def get_bool_settings_by_privilege(db: Session, level: str) -> Optional[list[models.BoolSetting]]:
	log.debug(f"Getting settings of level {level} or above")
	try:
		settings = db.scalars(
			select(models.BoolSetting)
			.where(models.BoolSetting.required_privilege_level>=level)
		).all()
		if settings is not None:
			return settings
		else:
			return None
	except Exception as e:
		log.exception("Could not find settings")
		return None

"""
Removes all bool settings from the database
"""
def clear_bool_settings(db: Session) -> bool:
	log.info("Clearing bool settings database")
	try:
		db.execute(
			delete(models.BoolSetting)
		)
		return True
	except Exception as e:
		log.exception("Could not clear table")
		return False