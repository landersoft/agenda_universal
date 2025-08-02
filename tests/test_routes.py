from app import create_app
from flask import current_app


def test_index():
    app = create_app()
    with app.test_client() as client:
        response = client.get("/")
        assert response.status_code == 200


def test_insert_db():
    app = create_app()
    with app.app_context():
        db = current_app.db
        # Insertamos datos de prueba
        db.especialidades.insert_one(
            {
                "nombre": "Cardiología",
                "codigo": "CAR001",
                "descripcion": "Especialidad del corazón",
                "taxonomia": ["corazón", "cardiología"],
            }
        )


def test_especialidades():
    app = create_app()
    with app.test_client() as client:
        response = client.get("/especialidades")
        assert response.status_code == 200
        data = response.get_json()
        assert "nombre" in data[0]
        assert "codigo" in data[0]
