import sqlalchemy as db

from ..database import Base

class IntSetting(Base):
	__tablename__ = "Card_Int_Settings"
	id = db.Column(db.Integer, primary_key=True, index=True)
	name = db.Column("Name", db.String(225), nullable=False)
	required_privilege_level = db.Column("Required_Privilege_Level", db.Integer, nullable=False)
	value = db.Column("Value", db.Integer, nullable=False)

class BoolSetting(Base):
	__tablename__ = "Card_Bool_Settings"
	id = db.Column(db.Integer, primary_key=True, index=True)
	name = db.Column("Name", db.String(225), nullable=False)
	required_privilege_level = db.Column("Required_Privilege_Level", db.Integer, nullable=False)
	value = db.Column("Value", db.Boolean, nullable=False)

class StrSetting(Base):
	__tablename__ = "Card_Str_Settings"
	id = db.Column(db.Integer, primary_key=True, index=True)
	name = db.Column("Name", db.String(225), nullable=False)
	required_privilege_level = db.Column("Required_Privilege_Level", db.Integer, nullable=False)
	value = db.Column("Value", db.String(225), nullable=False)