"""Almacenamiento simple de documentos con metadatos."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional
import uuid


@dataclass
class Document:
    """Representa un documento cargado por un usuario."""

    id: str
    filename: str
    content_type: str
    path: Path
    status: str = "pending"  # pending, approved, rejected


_STORAGE_DIR = Path(__file__).resolve().parent / "files"
_METADATA: Dict[str, Document] = {}

# Nos aseguramos de que exista el directorio físico donde guardar los archivos.
_STORAGE_DIR.mkdir(parents=True, exist_ok=True)


def save(file) -> Document:
    """Guarda un archivo y almacena sus metadatos."""

    doc_id = str(uuid.uuid4())
    filename = file.filename
    path = _STORAGE_DIR / f"{doc_id}_{filename}"
    file.save(path)
    doc = Document(id=doc_id, filename=filename, content_type=file.mimetype, path=path)
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


__all__ = [
    "Document",
    "save",
    "get",
    "list_pending",
    "set_status",
]
