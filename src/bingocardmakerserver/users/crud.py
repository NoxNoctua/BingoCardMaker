import logging

from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import select

from . import models, schemas, utils

log = logging.getLogger(__name__)

"""
Gets a user from the database using ID
"""
def get_user(db: Session, user_id: int) -> Optional[models.User]:
	log.debug(f"get_user with id: {user_id}")
	try:
		user = db.scalars(
			select(models.User)
			.where(models.User.id == user_id)
		).one()
		return user
	except Exception as e:
		log.error("Could not find user")
		log.error(str(e))
		return None


"""
Gets a user from the databse using username
"""
def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
	log.debug(f"get_user_by_username with username: {username}")
	try:
		user = db.scalars(
			select(models.User)
			.where(models.User.username == username)
		).one()
		return user
	except Exception as e:
		log.error("Could not find user")
		log.error(str(e))
		return None

"""
Gets a user from the database using email
"""
def fetch_user_by_email(db: Session, email: str) -> Optional[models.User]:
	log.debug(f"fetch_user_by_email with email: {email}")
	try:
		user = db.scalars(
			select(models.User)
			.where(models.User.email == email)
		).one()
		return user
	except Exception as e:
		log.error("Could not find user")
		log.error(str(e))
		return None

"""
Returns list of all users from database
"""
def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> Optional[list[models.User]]:
	log.debug(f"get_all_users")
	try:
		users = db.scalars(
			select(models.User)
		).all()
		return users
	except Exception as e:
		log.error("Could not find users")
		log.error(str(e))
		return None

"""
Adds user to table using schema createuser
"""
def create_new_user(db: Session, user: schemas.UserCreate) -> Optional[models.User]:
	log.debug(f"create_new_user with username: {user.username}")
	try:
		hashed_pass = utils.get_password_hash(user.password)
		db_user = models.User(
			username=user.username,
			email=user.email,
			full_name=user.full_name,
			hashed_password=hashed_pass,
		)
		db.add(db_user)
		db.commit()
		db.refresh(db_user)
		return db_user
	except Exception as e:
		log.error("Could not create user")
		log.error(str(e))
		return None

"""
Updates a users privilege level
"""
def change_user_privilege_level(db: Session, id: int, level: int) -> bool:
	log.debug(f"change_user_privilege_level user: {id} level: {level}")
	try:
		user = db.scalars(
			select(models.User)
			.where(models.User.id == id)
		).one()
		user.privilege_level = level
		db.commit()
		return True
	except Exception as e:
		log.error("Could not update privilege level")
		log.error(str(e))
		return False
