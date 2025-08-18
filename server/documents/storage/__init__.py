"""Almacenamiento simple de documentos con metadatos."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional
import os
import shutil
import uuid


@dataclass
class Document:
    """Representa un documento cargado por un usuario."""

    id: str
    filename: str
    content_type: str
    path: Path
    url: Optional[str] = None
    status: str = "pending"  # pending, approved, rejected


_STORAGE_DIR = Path(
    os.environ.get("EXTERNAL_STORAGE_DIR", Path(__file__).resolve().parent / "files")
)
_BASE_URL = os.environ.get("EXTERNAL_STORAGE_URL")
_METADATA: Dict[str, Document] = {}

# Nos aseguramos de que exista el directorio físico donde guardar los archivos.
_STORAGE_DIR.mkdir(parents=True, exist_ok=True)


def save(file) -> Document:
    """Guarda un archivo y almacena sus metadatos."""

    doc_id = str(uuid.uuid4())
    filename = file.filename
    path = _STORAGE_DIR / f"{doc_id}_{filename}"
    file.save(path)
    url = f"{_BASE_URL.rstrip('/')}/{path.name}" if _BASE_URL else None
    doc = Document(
        id=doc_id,
        filename=filename,
        content_type=file.mimetype,
        path=path,
        url=url,
    )
    _METADATA[doc_id] = doc
    return doc


def get(doc_id: str) -> Optional[Document]:
    """Recupera un documento por su identificador."""

    return _METADATA.get(doc_id)


def list_pending() -> List[Document]:
    """Lista los documentos pendientes de revisión."""

    return [d for d in _METADATA.values() if d.status == "pending"]


def set_status(doc_id: str, status: str) -> bool:
    """Actualiza el estado de un documento."""

    if doc_id in _METADATA:
        _METADATA[doc_id].status = status
        return True
    return False


def migrate_from_public_uploads(src: Path = Path("public/uploads")) -> None:
    """Mueve archivos existentes desde ``public/uploads`` al almacenamiento externo."""

    if not src.exists():
        return
    for file in src.iterdir():
        if file.is_file():
            dest = _STORAGE_DIR / file.name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(file), dest)


__all__ = [
    "Document",
    "save",
    "get",
    "list_pending",
    "set_status",
    "migrate_from_public_uploads",
]
