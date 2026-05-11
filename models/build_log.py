"""
models/build_log.py — Log de Builds
=====================================
Registra cada execução de pytest e geração de ZIP pelo DS_BUILD.
"""

import datetime

from models import db


class BuildLog(db.Model):
    """Registro de uma execução do pipeline de build."""

    __tablename__ = "build_logs"

    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.String(20), nullable=False, default="3.0.0")
    status = db.Column(db.String(20), nullable=False, default="running")
    # running | passed | failed | error

    # ── Resultados dos testes ─────────────────────────────────────
    tests_total = db.Column(db.Integer, default=0)
    tests_passed = db.Column(db.Integer, default=0)
    tests_failed = db.Column(db.Integer, default=0)
    tests_errors = db.Column(db.Integer, default=0)
    test_output = db.Column(db.Text, nullable=True)  # saída completa do pytest

    # ── Artefato gerado ───────────────────────────────────────────
    zip_path = db.Column(db.String(500), nullable=True)
    zip_name = db.Column(db.String(200), nullable=True)
    zip_size_bytes = db.Column(db.Integer, nullable=True)

    # ── Timestamps ────────────────────────────────────────────────
    triggered_by = db.Column(db.String(100), default="sistema")
    started_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    finished_at = db.Column(db.DateTime, nullable=True)

    @property
    def duration_seconds(self) -> int | None:
        if self.started_at and self.finished_at:
            return int((self.finished_at - self.started_at).total_seconds())
        return None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "version": self.version,
            "status": self.status,
            "tests_total": self.tests_total,
            "tests_passed": self.tests_passed,
            "tests_failed": self.tests_failed,
            "tests_errors": self.tests_errors,
            "test_output": self.test_output,
            "zip_path": self.zip_path,
            "zip_name": self.zip_name,
            "zip_size_bytes": self.zip_size_bytes,
            "triggered_by": self.triggered_by,
            "started_at": self._fmt(self.started_at),
            "finished_at": self._fmt(self.finished_at),
            "duration_seconds": self.duration_seconds,
        }

    @staticmethod
    def _fmt(dt):
        return dt.strftime("%d/%m/%Y %H:%M:%S") if dt else None

    def __repr__(self):
        return (
            f"<BuildLog id={self.id} status={self.status!r} version={self.version!r}>"
        )
