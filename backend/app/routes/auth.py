from flask import Blueprint, request, jsonify

from app.services.auth_service import register_user, login_user

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    
    if not data or "email" not in data or "password" not in data:
        return jsonify({"error": "Missing email or password"}), 400
    
    try:
        register_user(data["email"], data["password"])
        return jsonify({"message": "User registered successfully"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 409


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    
    if not data or "email" not in data or "password" not in data:
        return jsonify({"error": "Missing email or password"}), 400
    
    try:
        user = login_user(data["email"], data["password"])
        return jsonify(user), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
