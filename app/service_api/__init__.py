from flask import Blueprint

api = Blueprint("service_api", __name__)

from . import user
