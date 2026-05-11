"""
models/version_backup.py — Registro de Backups .dsk
=====================================================
Cada backup gerado (ao deletar uma versão ou ao fazer reset)
fica registrado aqui para rastreabilidade completa.
"""

import datetime

from models import db


class VersionBackup(db.Model):
    """Log imutável de cada arquivo .dsk gerado pelo sistema."""

    __tablename__ = "version_backups"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    page_id = db.Column(db.Integer, nullable=True)  # None = backup de projeto inteiro
    version_id = db.Column(db.Integer, nullable=True)  # PageVersion.id de origem
    backup_path = db.Column(db.String(500), nullable=False)  # caminho absoluto do .dsk
    backup_name = db.Column(db.String(200), nullable=False)  # nome do arquivo .dsk
    reason = db.Column(
        db.String(200), nullable=False
    )  # "purge_version" | "project_reset" | "manual"
    triggered_by = db.Column(db.String(100), default="sistema")
    size_bytes = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, index=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "project_id": self.project_id,
            "page_id": self.page_id,
            "version_id": self.version_id,
            "backup_name": self.backup_name,
            "backup_path": self.backup_path,
            "reason": self.reason,
            "triggered_by": self.triggered_by,
            "size_bytes": self.size_bytes,
            "created_at": (
                self.created_at.strftime("%d/%m/%Y %H:%M:%S")
                if self.created_at
                else None
            ),
        }

    def __repr__(self):
        return f"<VersionBackup id={self.id} name={self.backup_name!r}>"
