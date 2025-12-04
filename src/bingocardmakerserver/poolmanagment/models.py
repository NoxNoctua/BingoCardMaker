import sqlalchemy as db

from ..database import Base

class PoolImage(Base):
	__tablename__ = "Pool_Images"
	id = db.Column(db.Integer, primary_key=True, index=True)
	name = db.Column("Name", db.String(225), nullable=False)
	file_path = db.Column("File_Path", db.String(225), nullable=False)
	tag = db.Column("Tag", db.String(225), nullable=False)
	use_type = db.Column("Use_Type", db.String(225), nullable=False)
	active = db.Column("Active", db.Boolean, nullable=False)