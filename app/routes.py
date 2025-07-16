from flask import Blueprint, jsonify, current_app

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    collection = current_app.db["mensajes"]
    count = collection.count_documents({})
    return jsonify({"mensaje": "Hola Flask + Mongo", "total_mensajes": count})

@bp.route('/test-db')
def test_db():
    collection = current_app.db["profesionales"]  # usa la colección que desees
    docs = list(collection.find({}, {"_id": 0}))  # sin mostrar _id
    return jsonify(docs)
