from app import create_app
from flask import current_app
import json


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


def obtener_token_de_prueba(client):

    response = client.post(
        "/auth/login", json={"username": "rodrigo", "password": "rodrigo123"}
    )
    data = json.loads(response.data)
    return data["access_token"]


def test_especialidades():
    app = create_app()
    with app.test_client() as client:

        token = obtener_token_de_prueba(client)
        headers = {"Authorization": "Bearer {}".format(token)}
        # Probamos el endpoint de obtener especialidades
        response = client.get("/especialidades", headers=headers)
        assert response.status_code == 200
        data = response.get_json()
        assert "nombre" in data[0]
        assert "codigo" in data[0]
