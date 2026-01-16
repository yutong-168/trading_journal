import os
import imghdr
import uuid
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image

from app.repos.attachment_repo import (
    insert_attachment,
    list_attachments_by_journal,
    get_attachment,
    delete_attachment as repo_delete_attachment,
)
from app.repos.journal_repo import get_journal_by_id

ALLOWED_MIMES = {"image/jpeg", "image/png", "image/webp", "image/avif"}
ALLOWED_EXTS = {"jpg", "jpeg", "png", "webp", "avif"}
MAX_SIZE_BYTES = 5 * 1024 * 1024  # 5MB

def _ensure_uploads_dir(base_uploads: Path):
    base_uploads.mkdir(parents=True, exist_ok=True)

def _detect_extension(data: bytes) -> Optional[str]:
    kind = imghdr.what(None, h=data)
    if kind == "jpeg":
        return "jpg"
    return kind

def _open_image_get_size(filepath: Path) -> Tuple[Optional[int], Optional[int]]:
    try:
        with Image.open(filepath) as img:
            width, height = img.size
            return width, height
    except Exception:
        return None, None

def save_attachment_file(
    *,
    base_uploads: Path,
    user_id: int,
    journal_id: int,
    filename: str,
    content_type: str,
    data: bytes,
) -> dict:
    if content_type not in ALLOWED_MIMES:
        raise ValueError("Invalid file type")
    if len(data) > MAX_SIZE_BYTES:
        raise ValueError("File too large (max 5MB)")

    # Validate journal ownership
    journal = get_journal_by_id(journal_id)
    if journal is None:
        raise ValueError("Journal not found")
    journal_user_id = journal[1]
    if journal_user_id != user_id:
        raise PermissionError("No permission to add attachment to this journal")

    _ensure_uploads_dir(base_uploads)

    # Build path: uploads/{user_id}/{journal_id}/{uuid}.{ext}
    ext = (filename.split(".")[-1] or "").lower()
    if ext not in ALLOWED_EXTS:
        ext_from_sig = _detect_extension(data)
        if not ext_from_sig or ext_from_sig not in ALLOWED_EXTS:
            raise ValueError("Unsupported image format")
        ext = ext_from_sig

    key = f"{user_id}/{journal_id}/{uuid.uuid4().hex}.{ext}"
    file_path = base_uploads / key
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(data)

    width, height = _open_image_get_size(file_path)

    public_url = f"/uploads/{key}"
    attachment_id = insert_attachment(
        journal_id=journal_id,
        user_id=user_id,
        storage_key=key,
        public_url=public_url,
        mime=content_type,
        size=len(data),
        width=width,
        height=height,
    )

    return {
        "attachment_id": attachment_id,
        "journal_id": journal_id,
        "user_id": user_id,
        "storage_key": key,
        "public_url": public_url,
        "mime": content_type,
        "size": len(data),
        "width": width,
        "height": height,
    }

def list_attachments(journal_id: int):
    rows = list_attachments_by_journal(journal_id)
    result = []
    for r in rows:
        result.append(
            {
                "attachment_id": r[0],
                "journal_id": r[1],
                "user_id": r[2],
                "storage_key": r[3],
                "public_url": r[4],
                "mime": r[5],
                "size": r[6],
                "width": r[7],
                "height": r[8],
                "created_at": r[9],
            }
        )
    return result

def delete_attachment(*, base_uploads: Path, user_id: int, journal_id: int, attachment_id: int):
    row = get_attachment(attachment_id)
    if row is None:
        raise ValueError("Attachment not found")
    _attachment_id, _journal_id, _user_id, storage_key, *_ = row
    if _journal_id != journal_id or _user_id != user_id:
        raise PermissionError("No permission to delete this attachment")
    # Delete file
    file_path = base_uploads / storage_key
    try:
        if file_path.exists():
            file_path.unlink()
    except Exception:
        # ignore file delete errors; db delete still proceeds
        pass
    repo_delete_attachment(attachment_id)

