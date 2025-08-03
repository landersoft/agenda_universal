from flask import Blueprint, jsonify, request, current_app

# from bson import ObjectId
from app.models.especialidad import EspecialidadInput  # EspecialidadOutput
from pydantic import ValidationError
from flasgger import swag_from
import time
import datetime
from flask_jwt_extended import jwt_required


especialidades_bp = Blueprint("especialidades", __name__)


'''@especialidades_bp.route('')
@especialidades_bp.route('/')
def index():
    """Endpoint para la página de inicio de especialidades"""
    return jsonify({"message": "Bienvenido a la API de Especialidades"}), 200  '''


@especialidades_bp.route("/especialidades", methods=["GET"])
@swag_from(
    {
        "tags": ["Especialidades"],
        "summary": "Obtener todas las especialidades",
        "description": "Este endpoint devuelve una lista de todas las "
        "especialidades registradas en la base de datos.",
        "responses": {
            200: {
                "description": "Lista de especialidades",
                "content": {
                    "application/json": {
                        "example": [
                            {
                                "_id": "60c72b2f9b1e8d001c8e4a2f",
                                "nombre": "Cardiología",
                                "codigo": "CAR001",
                                "descripcion": "Especialidad del corazón",
                                "taxonomia": ["corazón", "cardiología"],
                            },
                            {
                                "_id": "60c72b2f9b1e8d001c8e4a30",
                                "nombre": "Neurología",
                                "codigo": "NEU001",
                                "descripcion": "Especialidad del sistema nervioso",
                                "taxonomia": ["sistema nervioso", "neurología"],
                            },
                        ]
                    }
                },
            },
            404: {"description": "No hay especialidades registradas"},
        },
    }
)
@jwt_required()
def obtener_especialidades():

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
        "nombre": data.nombre.capitalize(),
        "descripcion": data.descripcion,
        "taxonomia": data.taxonomia or [],
        "created_at": time.time(),
    }

    resultado = db.especialidades.insert_one(nueva)
    return (
        jsonify(
            {
                "id": str(resultado.inserted_id),
                "nombre": data.nombre,
                "codigo": data.codigo,
                "created_at": datetime.datetime.fromtimestamp(
                    nueva["created_at"]
                ).isoformat(),
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
