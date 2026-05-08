"""
controllers/plugin_controller.py — Gerenciador de Plugins (DS_PLUGINS)
=======================================================================
  GET  /api/plugins                  → lista todos os plugins descobertos
  GET  /api/plugins/<code>           → detalhe de um plugin
  POST /api/plugins/<code>/ativar    → ativa plugin (requer confirmação)
  POST /api/plugins/<code>/desativar → desativa plugin
  POST /api/plugins/redescobrir      → re-escaneia pasta plugins/
"""

import datetime
import logging

from flask import Blueprint, jsonify, request, current_app
from models import db, Plugin

bp  = Blueprint("plugin", __name__)
log = logging.getLogger(__name__)


@bp.route("/api/plugins")
def list_plugins():
    plugins = Plugin.query.order_by(Plugin.name).all()
    return jsonify([p.to_dict() for p in plugins])


@bp.route("/api/plugins/<string:code>")
def get_plugin(code: str):
    plugin = Plugin.query.filter_by(code=code).first_or_404()
    return jsonify(plugin.to_dict())


@bp.route("/api/plugins/<string:code>/ativar", methods=["POST"])
def activate_plugin(code: str):
    """
    Ativa um plugin.
    Requer campo 'confirmed': true no body — nunca ativa automaticamente.
    """
    data      = request.get_json(force=True) or {}
    confirmed = data.get("confirmed", False)
    author    = data.get("triggered_by", "usuario")

    if not confirmed:
        return jsonify({
            "error": "Confirmação obrigatória. Envie confirmed: true para ativar."
        }), 400

    plugin = Plugin.query.filter_by(code=code).first_or_404()
    if plugin.is_active:
        return jsonify({"ok": True, "message": "Plugin já está ativo.", "plugin": plugin.to_dict()})

    plugin.is_active    = True
    plugin.activated_at = datetime.datetime.utcnow()
    plugin.activated_by = author
    db.session.commit()

    # Carrega o plugin na sessão atual
    from transactions.registry import _load_plugin
    _load_plugin(plugin, db)
    db.session.commit()

    log.info("Plugin %s ativado por %s", code, author)
    return jsonify({"ok": True, "plugin": plugin.to_dict()})


@bp.route("/api/plugins/<string:code>/desativar", methods=["POST"])
def deactivate_plugin(code: str):
    """Desativa plugin e marca suas transações NDS_* como inativas."""
    data   = request.get_json(force=True) or {}
    author = data.get("triggered_by", "usuario")

    plugin = Plugin.query.filter_by(code=code).first_or_404()
    if not plugin.is_active:
        return jsonify({"ok": True, "message": "Plugin já está inativo.", "plugin": plugin.to_dict()})

    plugin.is_active = False

    # Desativa as transações NDS_* do plugin
    from models import Transaction
    for tx_code in (plugin.transaction_codes or []):
        tx = Transaction.query.filter_by(code=tx_code).first()
        if tx:
            tx.is_active = False

    db.session.commit()
    log.info("Plugin %s desativado por %s", code, author)
    return jsonify({"ok": True, "plugin": plugin.to_dict()})


@bp.route("/api/plugins/redescobrir", methods=["POST"])
def rediscover_plugins():
    """Re-escaneia a pasta plugins/ e registra novos plugins encontrados."""
    from transactions.registry import discover_plugins
    discover_plugins(current_app._get_current_object())
    plugins = Plugin.query.order_by(Plugin.name).all()
    return jsonify({"ok": True, "total": len(plugins), "plugins": [p.to_dict() for p in plugins]})
