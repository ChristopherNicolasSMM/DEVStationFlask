"""
models/component.py — Model de Componente v3.0
"""
import datetime
from models import db


class Component(db.Model):
    __tablename__ = "components"

    id         = db.Column(db.Integer,     primary_key=True)
    page_id    = db.Column(db.Integer,     db.ForeignKey("pages.id"), nullable=False)
    type       = db.Column(db.String(50),  nullable=False)
    name       = db.Column(db.String(100), nullable=False)
    x          = db.Column(db.Integer, default=100)
    y          = db.Column(db.Integer, default=100)
    width      = db.Column(db.Integer, default=150)
    height     = db.Column(db.Integer, default=40)
    z_index    = db.Column(db.Integer, default=1)
    # properties inclui bloco "odata" quando binding configurado
    properties = db.Column(db.JSON, default=dict, nullable=False)
    events     = db.Column(db.JSON, default=dict, nullable=False)
    rules      = db.Column(db.JSON, default=list, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow,
                           onupdate=datetime.datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id":         self.id,
            "page_id":    self.page_id,
            "type":       self.type,
            "name":       self.name,
            "x":          self.x,
            "y":          self.y,
            "width":      self.width,
            "height":     self.height,
            "z_index":    self.z_index,
            "properties": self.properties or {},
            "events":     self.events     or {},
            "rules":      self.rules      or [],
        }

    def __repr__(self):
        return f"<Component id={self.id} type={self.type!r} name={self.name!r}>"
