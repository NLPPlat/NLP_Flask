from flask import Blueprint

api = Blueprint("admin_api", __name__)

from . import user_manage
