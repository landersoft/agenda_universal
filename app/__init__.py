from flask import Flask
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()


def create_app():
    app = Flask(__name__)

    mongo_uri = os.getenv("MONGO_URI")
    client = MongoClient(mongo_uri)
    app.db = client["agenda"]

    from .routes import bp as main_bp

    app.register_blueprint(main_bp)

    return app
