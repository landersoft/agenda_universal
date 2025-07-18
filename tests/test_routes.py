from app import create_app


def test_index():
    app = create_app()
    with app.test_client() as client:
        response = client.get("/")
        assert response.status_code == 200


def test_insert_db():
    app = create_app()
    with app.test_client() as client:
        response = client.get("/insert-db")
        assert response.status_code == 201
        data = response.get_json()
        assert "inserted" in data
