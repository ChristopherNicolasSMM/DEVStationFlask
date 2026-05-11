"""
models/menu.py — Model de Menu v3.0
"""

from models import db

from .menu_defaults import DEFAULT_MAIN_MENU, DEFAULT_SIDEBAR


class Menu(db.Model):
    __tablename__ = "menus"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    type = db.Column(db.String(50), nullable=False, default="main")
    config = db.Column(db.JSON, default=dict, nullable=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "project_id": self.project_id,
            "type": self.type,
            "config": self.config or {},
        }

    @classmethod
    def create_defaults(cls, project_id: int) -> list:
        return [
            cls(project_id=project_id, type="main", config=DEFAULT_MAIN_MENU),
            cls(project_id=project_id, type="sidebar", config=DEFAULT_SIDEBAR),
        ]

    def __repr__(self):
        return f"<Menu id={self.id} type={self.type!r} project={self.project_id}>"
