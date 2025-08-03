from flask import Flask
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from flasgger import Swagger
from flask_jwt_extended import JWTManager

load_dotenv()


def create_app():
    app = Flask(__name__)
    swagger = Swagger(app)

    mongo_uri = os.getenv("MONGO_URI")
    client = MongoClient(mongo_uri)
    app.db = client["agenda"]

    app.config["SECRET_KEY"] = "superclave_123"

    jwt = JWTManager(app)

    # Registrar Blueprints

    # app.register_blueprint(index_bp)  # Sin prefix, para que maneje "/"
    from .routes.index import bp as index_bp

    app.register_blueprint(index_bp)

    from app.routes.especialidades import especialidades_bp as especialidades_bp

    app.register_blueprint(especialidades_bp, url_prefix="/")

    from .routes.auth import auth_bp as auth_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")

    return app
