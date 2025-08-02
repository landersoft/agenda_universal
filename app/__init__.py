from flask import Flask
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from flasgger import Swagger

load_dotenv()


def create_app():
    app = Flask(__name__)
    swagger = Swagger(app)


    mongo_uri = os.getenv("MONGO_URI")
    client = MongoClient(mongo_uri)
    app.db = client["agenda"]

    # from .routes import bp as main_bp

    # app.register_blueprint(main_bp)

    # Registrar Blueprints
    # from app.routes.index import bp as index_bp
    from app.routes.especialidades import especialidades_bp as especialidades_bp
    from .routes.index import bp as index_bp

    # from app.routes.profesionales import bp as profesionales_bp

    # app.register_blueprint(index_bp)  # Sin prefix, para que maneje "/"
    app.register_blueprint(index_bp)
    app.register_blueprint(especialidades_bp, url_prefix="/")
    # app.register_blueprint(profesionales_bp, url_prefix="/profesionales")

    return app
