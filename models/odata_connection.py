"""
models/odata_connection.py — Conexão OData
============================================
Armazena conexões a servidores OData V4 com cache de metadata.
"""

import datetime

from models import db


class ODataConnection(db.Model):
    """Representa um servidor OData registrado num projeto."""

    __tablename__ = "odata_connections"

    # ── Identificação ─────────────────────────────────────────────
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)  # "Servidor de Clientes"
    base_url = db.Column(
        db.String(500), nullable=False
    )  # "http://localhost:8000/odata/"

    # ── Autenticação ──────────────────────────────────────────────
    auth_type = db.Column(db.String(20), default="none")  # none | basic | bearer
    auth_value = db.Column(db.String(500), nullable=True)  # token ou "user:pass"

    # ── Cache de metadados ────────────────────────────────────────
    metadata_cache = db.Column(db.JSON, nullable=True)
    metadata_cached_at = db.Column(db.DateTime, nullable=True)

    # ── Timestamps ────────────────────────────────────────────────
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "project_id": self.project_id,
            "name": self.name,
            "base_url": self.base_url,
            "auth_type": self.auth_type,
            "has_metadata_cache": self.metadata_cache is not None,
            "metadata_cached_at": self._fmt(self.metadata_cached_at),
            "created_at": self._fmt(self.created_at),
        }

    @staticmethod
    def _fmt(dt):
        return dt.strftime("%d/%m/%Y %H:%M:%S") if dt else None

    def __repr__(self):
        return (
            f"<ODataConnection id={self.id} name={self.name!r} url={self.base_url!r}>"
        )
