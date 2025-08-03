from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from datetime import timedelta


auth_bp = Blueprint("auth", __name__)

USERS = {
    "admin": "admin123",
    "rodrigo": "rodrigo123",
}


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username y password son necesarios"}), 400

    if username in USERS and USERS[username] == password:
        access_token = create_access_token(
            identity=username, expires_delta=timedelta(hours=1)
        )
        return jsonify(access_token=access_token), 200

    return jsonify({"error": "Invalid credentials"}), 401
