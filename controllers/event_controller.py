"""controllers/event_controller.py"""

from flask import Blueprint, jsonify, request

from models import Component, db

bp = Blueprint("event", __name__)


@bp.route("/api/componentes/<int:cid>/eventos", methods=["PUT"])
def save_events(cid):
    comp = Component.query.get_or_404(cid)
    comp.events = request.get_json(force=True) or {}
    db.session.commit()
    return jsonify({"ok": True, "events": comp.events})
