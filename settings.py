# coding: utf-8
from os import environ

MATRIX_SERVER = environ.get("MATRIX_SERVER", "https://matrix.example.org")
MATRIX_TOKEN = environ.get("MATRIX_TOKEN", "matrix_token")
MATRIX_ROOM = environ.get("MATRIX_ROOM", "!room_id:example.org")
LOG_LEVEL = environ.get("LOG_LEVEL", "INFO")
debug_enabled = environ.get("debug_enabled", False)
