"""controllers/rule_controller.py"""

from flask import Blueprint, jsonify, request

from models import Component, db

bp = Blueprint("rule", __name__)


@bp.route("/api/componentes/<int:cid>/regras", methods=["PUT"])
def save_rules(cid):
    comp = Component.query.get_or_404(cid)
    comp.rules = request.get_json(force=True) or []
    db.session.commit()
    return jsonify({"ok": True, "rules": comp.rules})
