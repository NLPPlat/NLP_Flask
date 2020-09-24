from flask import Blueprint

api = Blueprint("service_api", __name__)

from . import user
from .bbs_service import bbs_admin
from .bbs_service import bbs_user
from .bbs_service import bbs_common