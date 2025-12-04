import os

ADMIN_LEVEL = 0
CONFIGURE_PRIV_LEVEL = 2

# Paths
RESOURCE_PATH = "resources"
POOL_PATH = os.path.join("resources", "pool")
THUMBNAIL_PATH = os.path.join("resources", "thumbnails")
TEMPLATE_DIR = os.path.join("src", "bingocardmakerserver", "templetes")
OUTPUT_PATH = os.path.join("resources", "output")
LOG_PATH = "log.txt"

# Pool
POOL_IMAGES_FILE_ENDINGS = ["PNG", "JPEG"]