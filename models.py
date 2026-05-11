import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Projeto(db.Model):
    __tablename__ = "projetos"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False, default="Sem Título")
    canvas_json = db.Column(db.Text, default="[]")
    canvas_bg = db.Column(db.String(20), default="#ffffff")
    canvas_w = db.Column(db.Integer, default=1200)
    canvas_h = db.Column(db.Integer, default=800)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "canvas_bg": self.canvas_bg,
            "canvas_w": self.canvas_w,
            "canvas_h": self.canvas_h,
            "created_at": (
                self.created_at.strftime("%d/%m/%Y %H:%M") if self.created_at else ""
            ),
            "updated_at": (
                self.updated_at.strftime("%d/%m/%Y %H:%M") if self.updated_at else ""
            ),
        }
