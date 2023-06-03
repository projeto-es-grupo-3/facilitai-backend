import os

from pathlib import Path

# endpoints
REGISTER = '/register'
LOGIN = '/login'
LOGOUT = '/logout'
CREATE_AD = '/create-ad'
UPDATE = '/update'
DELETE_AD = '/delete-ad'
EDIT_AD = '/edit-ad'
UPLOAD_IMG_AD = '/upload-image'
UPLOAD_PROFILE_IMG= '/upload-profile'

# image saving paths
IMAGE_PATH = '~/.facilitai/images/'


def initial_config():
    base_path = Path('~/.facilitai/').expanduser()

    if not base_path.exists():
        os.mkdir(base_path)

    image_path = Path(IMAGE_PATH).expanduser()

    if not image_path.exists():
        os.mkdir(image_path)