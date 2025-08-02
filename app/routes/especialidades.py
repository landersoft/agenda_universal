from flask import Blueprint, jsonify, request, current_app

# from bson import ObjectId
from app.models.especialidad import EspecialidadInput  # EspecialidadOutput
from pydantic import ValidationError
import time


especialidades_bp = Blueprint("especialidades", __name__)


'''@especialidades_bp.route('')
@especialidades_bp.route('/')
def index():
    """Endpoint para la página de inicio de especialidades"""
    return jsonify({"message": "Bienvenido a la API de Especialidades"}), 200  '''


@especialidades_bp.route("/especialidades", methods=["GET"])
def obtener_especialidades():
    print("Obteniendo especialidades")
    db = current_app.db

    """Endpoint para obtener todas las especialidades"""
    especialidades = list(db.especialidades.find())
    if not especialidades:
        return jsonify({"message": "No hay especialidades registradas"}), 404
    for e in especialidades:
        e["_id"] = str(e["_id"])
    return jsonify(especialidades), 200


@especialidades_bp.route("/especialidades", methods=["POST"])
def crear_especialidad():
    db = current_app.db
    try:
        data = EspecialidadInput(**request.json)
        print("Datos recibidos:", data)

    except ValidationError as e:
        return jsonify({"error": str(e)}), 422

    nueva = {
        "codigo": data.codigo,
        "nombre": data.nombre,
        "descripcion": data.descripcion,
        "taxonomia": data.taxonomia or [],
        "created_at": time.time()
    }

    resultado = db.especialidades.insert_one(nueva)
    return (
        jsonify(
            {
                "id": str(resultado.inserted_id),
                "nombre": data.nombre,
                "codigo": data.codigo,
            }
        ),
        201,
    )


@especialidades_bp.route("/especialidades", methods=["PUT"])
def actualizar_especialidad():
    db = current_app.db
    try:
        data = EspecialidadInput(**request.json)
        print("Datos recibidos para actualización:", data)
    except ValidationError as e:
        return jsonify({"error": str(e)}), 422

    if not data.nombre:
        return jsonify({"error": "El nombre es obligatorio"}), 400

    resultado = db.especialidades.update_one(
        {"codigo": data.codigo},
        {
            "$set": {
                "nombre": data.nombre,
                "descripcion": data.descripcion,
                "taxonomia": data.taxonomia or [],
                "updated_at": time.time(),
            }
        },
    )

    if resultado.matched_count == 0:
        return jsonify({"error": "Especialidad no encontrada"}), 404

    return jsonify({"message": "Especialidad actualizada exitosamente"}), 200


@especialidades_bp.route("/especialidades/<id>", methods=["DELETE"])
def eliminar_especialidad(id):
    db = current_app.db

    """Endpoint para eliminar una especialidad por ID"""
    resultado = db.especialidades.delete_one({"codigo": id})

    if resultado.deleted_count == 0:
        return jsonify({"error": "Especialidad no encontrada"}), 404

    return jsonify({"message": "Especialidad eliminada exitosamente"}), 200
