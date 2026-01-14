from flask import Blueprint, request, jsonify
from app.services.journal_service import stats_summary

stats_bp = Blueprint("stats", __name__, url_prefix="/stats")

@stats_bp.route("/summary", methods=["GET"])
def get_summary():
    user_id = request.args.get("user_id", type=int)
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    result = stats_summary(user_id)
    return jsonify(result), 200
