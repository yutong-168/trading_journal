from flask import Blueprint, request, jsonify, current_app
from pathlib import Path

from app.services.attachment_service import (
    save_attachment_file,
    list_attachments,
    delete_attachment,
)

attachments_bp = Blueprint("attachments", __name__, url_prefix="/journals")

def _uploads_dir() -> Path:
    return Path(current_app.config["UPLOADS_DIR"])

@attachments_bp.route("/<int:journal_id>/attachments", methods=["GET"])
def list_journal_attachments(journal_id: int):
    try:
        result = list_attachments(journal_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@attachments_bp.route("/<int:journal_id>/attachments", methods=["POST"])
def upload_attachment(journal_id: int):
    user_id = request.form.get("user_id", type=int)
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    if "file" not in request.files:
        return jsonify({"error": "file is required"}), 400
    file = request.files["file"]
    try:
        data = file.read()
        content_type = file.mimetype or "application/octet-stream"
        meta = save_attachment_file(
            base_uploads=_uploads_dir(),
            user_id=user_id,
            journal_id=journal_id,
            filename=file.filename or "upload",
            content_type=content_type,
            data=data,
        )
        return jsonify(meta), 201
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@attachments_bp.route("/<int:journal_id>/attachments/<int:attachment_id>", methods=["DELETE"])
def remove_attachment(journal_id: int, attachment_id: int):
    user_id = request.get_json(silent=True) or {}
    user_id = user_id.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    try:
        delete_attachment(
            base_uploads=_uploads_dir(),
            user_id=int(user_id),
            journal_id=journal_id,
            attachment_id=attachment_id,
        )
        return jsonify({"message": "Attachment deleted"}), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

