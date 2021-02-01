from flask import Blueprint

api = Blueprint("expand_api", __name__)

from . import arrange