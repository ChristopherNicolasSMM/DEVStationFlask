"""
models/project.py — Model de Projeto
======================================
Um Projeto agrupa múltiplas Páginas e um Menu configurável.
Cada projeto tem configurações globais (canvas, tema, etc.).
"""

import datetime
from models import db


class Project(db.Model):
    """
    Entidade raiz do sistema.
    Relacionamentos:
        pages  → 1:N Page  (cascade delete)
        menus  → 1:N Menu  (cascade delete)
    """

    __tablename__ = "projects"

    # ── Identificação ─────────────────────────────────────────────
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(200), nullable=False, default="Sem Título")
    description = db.Column(db.String(500), nullable=True)

    # ── Canvas Global ─────────────────────────────────────────────
    canvas_w    = db.Column(db.Integer,     default=1280)
    canvas_h    = db.Column(db.Integer,     default=900)
    canvas_bg   = db.Column(db.String(20),  default="#ffffff")

    # ── Timestamps ────────────────────────────────────────────────
    created_at  = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.datetime.utcnow,
                            onupdate=datetime.datetime.utcnow)

    # ── Relacionamentos ───────────────────────────────────────────
    pages = db.relationship(
        "Page", backref="project",
        cascade="all, delete-orphan",
        order_by="Page.order"
    )
    menus = db.relationship(
        "Menu", backref="project",
        cascade="all, delete-orphan"
    )

    # ── Serialização ──────────────────────────────────────────────
    def to_dict(self) -> dict:
        """Converte para dicionário (usado nas respostas JSON)."""
        return {
            "id":          self.id,
            "name":        self.name,
            "description": self.description,
            "canvas_w":    self.canvas_w,
            "canvas_h":    self.canvas_h,
            "canvas_bg":   self.canvas_bg,
            "created_at":  self._fmt(self.created_at),
            "updated_at":  self._fmt(self.updated_at),
            "page_count":  len(self.pages),
        }

    @staticmethod
    def _fmt(dt) -> str:
        return dt.strftime("%d/%m/%Y %H:%M") if dt else "—"

    def __repr__(self):
        return f"<Project id={self.id} name={self.name!r}>"
