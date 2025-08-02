from app import create_app


def test_index():
    app = create_app()
    with app.test_client() as client:
        response = client.get("/")
        assert response.status_code == 200


def test_insert_db():
    app = create_app()
    with app.test_client() as client:
        response = client.get("/especialidades")
        assert response.status_code == 200
        data = response.get_json()
        assert "_id" in data
        assert "nombre" in data
        assert "codigo" in data
