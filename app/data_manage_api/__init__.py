from flask import Blueprint

api = Blueprint("data_manage_api", __name__)

from . import data_venation
from . import operator_manage
from . import model_manage
from . import resource_manage
from . import pipeline_manage
