from flask import Blueprint

api = Blueprint("common_api", __name__)

from . import dataset
from . import operator
from . import model
from . import pipeline
from . import resource