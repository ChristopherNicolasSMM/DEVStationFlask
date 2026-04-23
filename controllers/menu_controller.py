"""
controllers/menu_controller.py — Gerenciamento de Menus
========================================================
"""
from flask import Blueprint, jsonify, request
from models import db, Menu

bp = Blueprint("menu", __name__)


@bp.route("/api/projetos/<int:pid>/menus")
def get_menus(pid: int):
    menus = Menu.query.filter_by(project_id=pid).all()
    return jsonify([m.to_dict() for m in menus])


@bp.route("/api/menus/<int:mid>", methods=["POST"])
def update_menu(mid: int):
    menu = Menu.query.get_or_404(mid)
    data = request.get_json(force=True) or {}
    menu.config = data.get("config", menu.config)
    db.session.commit()
    return jsonify(menu.to_dict())
