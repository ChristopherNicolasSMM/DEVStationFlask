"""
controllers/event_controller.py — Tipos de Eventos Disponíveis
===============================================================
"""
from flask import Blueprint, jsonify
from events.event_types import EVENT_CATALOG
from events.event_actions import ACTION_CATALOG

bp = Blueprint("event", __name__)


@bp.route("/api/eventos/tipos")
def event_types():
    """Retorna catálogo de tipos de eventos por categoria de componente."""
    return jsonify(EVENT_CATALOG)


@bp.route("/api/eventos/acoes")
def event_actions():
    """Retorna todas as ações disponíveis para associar a eventos."""
    return jsonify(ACTION_CATALOG)
