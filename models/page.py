"""
models/page.py — Model de Página v3.0
"""

import datetime

from models import db


class Page(db.Model):
    __tablename__ = "pages"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False, default="Página")
    title = db.Column(db.String(200), nullable=True)
    slug = db.Column(db.String(100), nullable=True)
    is_home = db.Column(db.Boolean, default=False)
    order = db.Column(db.Integer, default=0)
    canvas_w = db.Column(db.Integer, nullable=True)
    canvas_h = db.Column(db.Integer, nullable=True)
    canvas_bg = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    components = db.relationship(
        "Component",
        backref="page",
        cascade="all, delete-orphan",
        order_by="Component.z_index",
    )

    def to_dict(self, include_components: bool = False) -> dict:
        d = {
            "id": self.id,
            "project_id": self.project_id,
            "name": self.name,
            "title": self.title or self.name,
            "slug": self.slug or "index",
            "is_home": self.is_home,
            "order": self.order,
            "canvas_w": self.canvas_w or self.project.canvas_w,
            "canvas_h": self.canvas_h or self.project.canvas_h,
            "canvas_bg": self.canvas_bg or self.project.canvas_bg,
        }
        if include_components:
            d["components"] = [c.to_dict() for c in self.components]
        return d

    def __repr__(self):
        return f"<Page id={self.id} name={self.name!r} project={self.project_id}>"
