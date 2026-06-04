import hashlib
import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
HASH_STORE = DATA_DIR / "file_hashes.json"


def _empty_registry() -> dict:
    return {"files": {}, "hashes": {}}


def _normalize_registry(raw_registry: dict) -> dict:
    if not isinstance(raw_registry, dict):
        return _empty_registry()

    if "files" in raw_registry and "hashes" in raw_registry:
        return {
            "files": raw_registry.get("files", {}),
            "hashes": raw_registry.get("hashes", {}),
        }

    normalized = _empty_registry()
    for file_path, file_hash in raw_registry.items():
        filename = Path(file_path).name
        normalized["files"][filename] = {"hash": file_hash, "path": file_path}
        normalized["hashes"][file_hash] = {"filename": filename, "path": file_path}
    return normalized


def get_bytes_hash(file_bytes: bytes) -> str:
    digest = hashlib.sha256()
    digest.update(file_bytes)
    return digest.hexdigest()


def load_stored_hashes() -> dict:
    if not HASH_STORE.exists():
        return _empty_registry()

    try:
        with open(HASH_STORE, "r", encoding="utf-8") as file_handle:
            return _normalize_registry(json.load(file_handle))
    except json.JSONDecodeError:
        return _empty_registry()


def save_hashes(hashes: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(HASH_STORE, "w", encoding="utf-8") as file_handle:
        json.dump(hashes, file_handle, indent=2)


def check_upload_status(filename: str, file_hash: str) -> dict:
    registry = load_stored_hashes()

    if filename in registry["files"]:
        return {
            "status": "duplicate_name",
            "reason": "This file name already uploaded previously.",
        }

    if file_hash in registry["hashes"]:
        return {
            "status": "duplicate_content",
            "reason": "Exact same knowledge base is already uploaded.",
        }

    return {"status": "new"}


def register_uploaded_file(filename: str, file_path: str, file_hash: str) -> None:
    registry = load_stored_hashes()
    registry["files"][filename] = {"hash": file_hash, "path": file_path}
    registry["hashes"][file_hash] = {"filename": filename, "path": file_path}
    save_hashes(registry)
