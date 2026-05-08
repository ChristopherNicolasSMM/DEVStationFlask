"""controllers/menu_controller.py — Menu v3.0"""
from flask import Blueprint, jsonify, request
from models import db, Menu, Project

bp = Blueprint("menu", __name__)

@bp.route("/api/projetos/<int:pid>/menus")
def list_menus(pid: int):
    Project.query.get_or_404(pid)
    menus = Menu.query.filter_by(project_id=pid).all()
    return jsonify([m.to_dict() for m in menus])

@bp.route("/api/menus/<int:mid>", methods=["PUT"])
def update_menu(mid: int):
    menu = Menu.query.get_or_404(mid)
    data = request.get_json(force=True) or {}
    if "config" in data:
        menu.config = data["config"]
    db.session.commit()
    return jsonify(menu.to_dict())
