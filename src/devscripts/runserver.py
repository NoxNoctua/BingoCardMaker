import logging
import uvicorn
import uvicorn.config
from bingocardmakerserver.main import app

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())


log_config = dict(uvicorn.config.LOGGING_CONFIG)
log_config["disable_existing_loggers"] = False


if __name__ == "__main__":
	uvicorn.run("bingocardmakerserver.main:app", host="0.0.0.0", port=8000, reload=True, log_config=log_config)