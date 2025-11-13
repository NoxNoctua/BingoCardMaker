import logging

import os
import sys

from sqlalchemy import MetaData

sys.path.append(os.path.join(os.path.dirname(__file__), "/src"))
from bingocardmakerserver.database import entity_manager

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
log.addHandler(logging.StreamHandler())
log.setLevel(logging.DEBUG)

def init_db():
	from bingocardmakerserver.users import models as users_models  # noqa: F401
	from bingocardmakerserver.admintools import models as admintools_models # noqa F401
	from bingocardmakerserver.cardgen import models as cardgen_models # noqa F401
	from bingocardmakerserver.poolmanagment import models as poolmanagment_models # noqa F401
	

	entity_manager.Base.metadata.create_all(entity_manager.engine)

	metadata = MetaData()
	metadata.reflect(bind=entity_manager.engine)

	tables = metadata.tables.keys()

	print("List of tables:")
	for table in tables:
		print(table)

	db = entity_manager.SessionLocal()
	db.commit()
	db.close()


def clear_users():
	from bingocardmakerserver.users import models as user_models

	db = entity_manager.SessionLocal()
	db.query(user_models.User).delete()
	db.commit()
	db.close()

def drop_tables():
	db = entity_manager.SessionLocal()
	entity_manager.metadata.drop_all(bind=entity_manager.engine)
	db.commit()
	db.close()


def add_user_admin():
	from bingocardmakerserver.users import crud, schemas

	admin = schemas.UserCreate(username="admin", password="admin")
	db = entity_manager.SessionLocal()

	crud.create_new_user(db, admin)
	crud.change_user_privilege_level(db,1,0)
	db.close()

def add_user_kaden():
	from bingocardmakerserver.users import crud, schemas

	admin = schemas.UserCreate(username="Kaden", password="T")
	db = entity_manager.SessionLocal()

	crud.create_new_user(db, admin)
	db.close()

def init_site_settings():
	from bingocardmakerserver.admintools import sitesettings
	db = entity_manager.SessionLocal()

	print(vars(sitesettings.site_settings))

	sitesettings.site_settings.init_saved_settings(db)

def init_board_settings():
	from bingocardmakerserver.cardgen import makermanager
	db = entity_manager.SessionLocal()

	print(vars(makermanager.maker_manager.card))

	makermanager.maker_manager.init_saved_settings(db)


if __name__ == "__main__":
	drop_tables()
	init_db()
	clear_users()
	add_user_admin()
	add_user_kaden()
	init_site_settings()
	init_board_settings()