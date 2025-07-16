from flask import Blueprint, jsonify, current_app, request

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    #collection = current_app.db["mensajes"]
    #count = collection.count_documents({})
    return jsonify({"mensaje": "Hola Flask + Mongo"})


@bp.route("/test-db", methods=["GET"])
def test_db_get():
    db = current_app.db
    #collection = current_app.db["profesionales"]  # usa la colección que desees
    documentos = list(db.profesionales.find({}, {"_id": 0}))  # sin mostrar _id
    #docs = list(collection.find({}, {"_id": 0}))  # sin mostrar _id
    return jsonify(documentos), 200

@bp.route("/test-db", methods=["POST"])
def test_db_post():
    db = current_app.db
    data = request.get_json()
    if not data:
        nuevo_documento = {"nombre": "Anibal", "especialidad": "General"}
        result = db.profesionales.insert_one(nuevo_documento)
        return jsonify({"mensaje": "Documento insertado", "id": str(result.inserted_id)}), 200
        
    
    result = db.profesionales.insert_one(data)
    return jsonify({
        "mensaje": "Documento insertado",
        "id": str(result.inserted_id)
        }), 201