from flask import Blueprint, jsonify, current_app

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    collection = current_app.db["mensajes"]
    count = collection.count_documents({})
    return jsonify({"mensaje": "Hola Flask + Mongo", "total_mensajes": count})
