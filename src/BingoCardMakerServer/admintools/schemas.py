from pydantic import BaseModel, ConfigDict

class IntSetting(BaseModel):
	model_config = ConfigDict(from_attributes=True)

	name: str
	required_privilege_level: int
	value: int


class BoolSetting(BaseModel):
	model_config = ConfigDict(from_attributes=True)
	
	name: str
	required_privilege_level: int
	value: bool


class StrSetting(BaseModel):
	model_config = ConfigDict(from_attributes=True)
	
	name: str
	required_privilege_level: int
	value: str