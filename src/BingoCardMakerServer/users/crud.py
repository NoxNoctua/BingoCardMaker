from sqlalchemy.orm import Session

from . import models, schemas, utils


def get_user(db: Session, user_id: int):
	return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
	return db.query(models.User).filter(models.User.username == username).first()


def fetch_user_by_email(db: Session, email: str):
	return db.query(models.User).filter(models.User.email == email).first()


def get_all_users(db: Session, skip: int = 0, limit: int = 100):
	return db.query(models.User).offset(skip).limit(limit).all()


def create_new_user(db: Session, user: schemas.UserCreate):
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