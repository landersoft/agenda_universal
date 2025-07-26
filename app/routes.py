from flask import Blueprint, jsonify, current_app, request

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    # collection = current_app.db["mensajes"]
    # count = collection.count_documents({})
    return jsonify({"mensaje": "Hola Flask + Mongo"})


@bp.route("/test-db", methods=["GET"])
def test_db_get():
    db = current_app.db
    # collection = current_app.db["profesionales"]
    # usa la colección que desees
    documentos = list(db.profesionales.find({}, {"_id": 0}))
    # sin mostrar _id
    # docs = list(collection.find({}, {"_id": 0}))
    # # sin mostrar _id
    return jsonify(documentos), 200


@bp.route("/test-db", methods=["POST"])
def test_db_post():
    db = current_app.db
    data = request.get_json()
    if not data:
        nuevo_documento = {"nombre": "Anibal", "especialidad": "General"}
        result = db.profesionales.insert_one(nuevo_documento)
        return (
            jsonify({"mensaje": "Documento insertado", "id": str(result.inserted_id)}),
            200,
        )

    result = db.profesionales.insert_one(data)
    return (
        jsonify({"mensaje": "Documento insertado", "id": str(result.inserted_id)}),
        201,
    )


@bp.route("/especialidades")
def especialidades():
    db = current_app.db
    # collection = current_app.db["profesionales"]  # usa la colección que desees
    documentos = list(db.especialidades.find({}, {"_id": 0}))  # sin mostrar _id
    # docs = list(collection.find({}, {"_id": 0}))  # sin mostrar _id
    if documentos:
        return jsonify(documentos), 200
    else:
        return jsonify({"mensaje": "No hay especialidades disponibles"}), 404


@bp.route("/insert-db")
def insert_db():

    lista = [
        {
            "name": "Medicina General",
            "description": "Atención médica primaria para adultos y niños.",
            "taxonomy": [
                "médico general",
                "consulta general",
                "atención primaria",
                "doctor",
                "salud familiar",
            ],
        },
        {
            "name": "Pediatría",
            "description": "Atención médica para bebés, niños y adolescentes.",
            "taxonomy": ["niños", "bebés", "pediatra", "infantil", "adolescente"],
        },
        {
            "name": "Ginecología",
            "description": "Salud femenina, control ginecológico y obstetricia.",
            "taxonomy": ["ginecóloga", "mujer", "embarazo", "pap", "parto", "obstetra"],
        },
        {
            "name": "Dermatología",
            "description": "Diagnóstico y tratamiento de enfermedades de la piel.",
            "taxonomy": ["dermatólogo", "piel", "manchas", "acné", "eczema", "lunar"],
        },
        {
            "name": "Oftalmología",
            "description": "Diagnóstico y tratamiento de problemas visuales.",
            "taxonomy": ["vista", "ojos", "lentes", "oftalmólogo", "visión", "retina"],
        },
        {
            "name": "Traumatología",
            "description": "Tratamiento de lesiones óseas, musculares y articulares.",
            "taxonomy": [
                "traumatólogo",
                "huesos",
                "fractura",
                "dolor articular",
                "columna",
                "lesión",
            ],
        },
        {
            "name": "Kinesiología",
            "description": "Rehabilitación física y movilidad corporal.",
            "taxonomy": [
                "kine",
                "rehabilitación",
                "fisioterapia",
                "movilidad",
                "dolor muscular",
            ],
        },
        {
            "name": "Nutrición",
            "description": "Planes de alimentación saludable y control nutricional.",
            "taxonomy": [
                "nutricionista",
                "alimentación",
                "dieta",
                "comida",
                "peso",
                "obesidad",
            ],
        },
        {
            "name": "Psicología",
            "description": "Terapia individual, familiar y atención emocional.",
            "taxonomy": [
                "psicólogo",
                "terapia",
                "emocional",
                "ansiedad",
                "depresión",
                "psiquiatría",
            ],
        },
        {
            "name": "Cardiología",
            "description": "Prevención y tratamiento de enfermedades del corazón.",
            "taxonomy": [
                "cardiólogo",
                "corazón",
                "presión",
                "infarto",
                "electrocardiograma",
                "hipertensión",
            ],
        },
    ]

    db = current_app.db
    for item in lista:
        nuevo_documento = {
            "nombre": item["name"],
            "descripcion": item["description"],
            "taxonomia": item["taxonomy"],
        }

        print(nuevo_documento)
        result = db.especialidades.insert_one(nuevo_documento)
    return (
        jsonify({"mensaje": "Documento insertado", "id": str(result.inserted_id)}),
        201,
    )
