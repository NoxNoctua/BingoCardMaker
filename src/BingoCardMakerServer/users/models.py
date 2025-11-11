import sqlalchemy as db

from ..database import Base


class User(Base):
	__tablename__ = "Users"
	id = db.Column(db.Integer, primary_key=True, index=True)
	username = db.Column("Username", db.String(225), nullable=False)
	email = db.Column("Email", db.String(225), default=None)
	full_name = db.Column("Full_Name", db.String(255), default=None)
	disabled = db.Column("Disabled", db.Boolean(), default=False)
	hashed_password = db.Column("Hashed_Password", db.String(225), nullable=False)
	privilege_level = db.Column("Privilege_Level", db.Integer, default=5, nullable=False)

	def __str__(self):
		ret_str = ("---\n" + 
			str(self.id) + "\n" +
			str(self.username) +  "\n" +
			str(self.email) +  "\n" +
			str(self.full_name) +  "\n" +
			str(self.disabled) + "\n" +
			str(self.hashed_password) + "\n" +
			str(self.privilege_level))
		return ret_str