from fastapi import HTTPException, status

from .admintools.sitesettings import site_settings

credentials_exception = HTTPException(
	status_code=status.HTTP_401_UNAUTHORIZED,
	detail="Could not validate credentials",
	headers={"Location": site_settings.site_url+"/login"}
)

notadmin_exception = HTTPException(
	status_code=status.HTTP_401_UNAUTHORIZED,
	detail="Could not validate addmin credentials",
)

inactive_user_exception = HTTPException(
	status_code=400,
	detail="Could not validate addmin credentials",
)

image_path_not_in_db = HTTPException(
	status_code=status.HTTP_404_NOT_FOUND,
	detail="Image does not exist in database"
)

bad_image_file = HTTPException(
	status_code=status.HTTP_400_BAD_REQUEST,
	detail="Image file could not be decoded"
)

internal_error = HTTPException(
	status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
	detail="Internal Server Error.  Check logs"
)