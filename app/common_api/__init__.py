from flask import Blueprint

api = Blueprint("common_api", __name__)

from . import dataset