from fastapi import HTTPException, status

credentials_exception = HTTPException(
	status_code=status.HTTP_401_UNAUTHORIZED,
	detail="Could not validate credentials",
)

notadmin_exception = HTTPException(
	status_code=status.HTTP_401_UNAUTHORIZED,
	detail="Could not validate addmin credentials",
)

inactive_user_exception = HTTPException(
	status_code=400,
	detail="Could not validate addmin credentials",
)