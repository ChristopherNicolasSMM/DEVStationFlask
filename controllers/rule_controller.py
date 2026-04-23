"""
controllers/rule_controller.py — Tipos de Regras Disponíveis
=============================================================
"""
from flask import Blueprint, jsonify
from rules.rule_types import RULE_CATALOG

bp = Blueprint("rule", __name__)


@bp.route("/api/regras/tipos")
def rule_types():
    """Retorna catálogo de regras disponíveis com parâmetros e descrição."""
    return jsonify(RULE_CATALOG)
