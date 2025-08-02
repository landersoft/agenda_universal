from flask import Blueprint  # jsonify

bp = Blueprint("index", __name__)


@bp.route("/")
def home():
    return "<h2>API de Agenda Médica v1</h2>"
