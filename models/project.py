"""
models/project.py — Model de Projeto v3.0
==========================================
Um Projeto agrupa múltiplas Páginas e um Menu configurável.
"""

import datetime

from models import db


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, default="Sem Título")
    description = db.Column(db.String(500), nullable=True)
    canvas_w = db.Column(db.Integer, default=1280)
    canvas_h = db.Column(db.Integer, default=900)
    canvas_bg = db.Column(db.String(20), default="#ffffff")
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    pages = db.relationship(
        "Page", backref="project", cascade="all, delete-orphan", order_by="Page.order"
    )
    menus = db.relationship("Menu", backref="project", cascade="all, delete-orphan")
    odata_connections = db.relationship(
        "ODataConnection",
        backref="project",
        cascade="all, delete-orphan",
        foreign_keys="ODataConnection.project_id",
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "canvas_w": self.canvas_w,
            "canvas_h": self.canvas_h,
            "canvas_bg": self.canvas_bg,
            "created_at": self._fmt(self.created_at),
            "updated_at": self._fmt(self.updated_at),
            "page_count": len(self.pages),
        }

    @staticmethod
    def _fmt(dt) -> str:
        return dt.strftime("%d/%m/%Y %H:%M") if dt else "—"

    def __repr__(self):
        return f"<Project id={self.id} name={self.name!r}>"
