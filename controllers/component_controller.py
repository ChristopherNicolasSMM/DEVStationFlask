"""
controllers/component_controller.py — API de Componentes
==========================================================
Expõe o catálogo de tipos disponíveis e operações sobre
instâncias individuais de componentes.

  GET  /api/componentes/catalogo           → catálogo completo
  GET  /api/componentes/tipo/<type>        → defaults de um tipo
  POST /api/componentes/<cid>/eventos      → salva eventos
  POST /api/componentes/<cid>/regras       → salva regras
  DEL  /api/componentes/<cid>             → remove
"""

from flask import Blueprint, jsonify, request
from models import db, Component
from components import ComponentRegistry

bp = Blueprint("component", __name__)


@bp.route("/api/componentes/catalogo")
def catalog():
    """Retorna o catálogo completo de tipos de componentes."""
    return jsonify(ComponentRegistry.get_catalog())


@bp.route("/api/componentes/tipo/<string:comp_type>")
def type_defaults(comp_type: str):
    """Retorna as propriedades padrão, eventos e regras de um tipo."""
    entry = ComponentRegistry.get(comp_type)
    if not entry:
        return jsonify({"error": f"Tipo '{comp_type}' não encontrado"}), 404
    return jsonify(entry)


@bp.route("/api/componentes/<int:cid>/eventos", methods=["POST"])
def save_events(cid: int):
    """Salva o mapa de eventos de um componente."""
    comp = Component.query.get_or_404(cid)
    data = request.get_json(force=True) or {}
    comp.events = data.get("events", {})
    db.session.commit()
    return jsonify({"ok": True, "events": comp.events})


@bp.route("/api/componentes/<int:cid>/regras", methods=["POST"])
def save_rules(cid: int):
    """Salva a lista de regras de um componente."""
    comp = Component.query.get_or_404(cid)
    data = request.get_json(force=True) or {}
    comp.rules = data.get("rules", [])
    db.session.commit()
    return jsonify({"ok": True, "rules": comp.rules})


@bp.route("/api/componentes/<int:cid>", methods=["DELETE"])
def delete(cid: int):
    """Remove um componente pelo ID."""
    comp = Component.query.get_or_404(cid)
    db.session.delete(comp)
    db.session.commit()
    return jsonify({"ok": True})
