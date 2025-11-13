from typing import Annotated

from pydantic import BaseModel, ConfigDict
from fastapi import UploadFile, File

class PoolImage(BaseModel):
	model_config = ConfigDict(from_attributes=True)
	name: str
	file_path: str
	tag: str
	active: bool

class UploadImageForm(BaseModel):
	model_config = ConfigDict(from_attributes=True)
	name: str
	tag: str
	active: bool
	for_pool: bool
	file: Annotated[UploadFile, File()]

class UpdateImageForm(BaseModel):
	model_config = ConfigDict(from_attributes=True)
	name: str
	tag: str
	active:bool