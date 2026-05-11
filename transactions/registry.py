"""
transactions/registry.py — Registry de Transações
===================================================
Responsável por:
 1. Fazer seed do catálogo DS_* no banco na primeira execução
 2. Escanear a pasta plugins/ e registrar plugins descobertos no banco
 3. Apenas plugins com is_active=True no banco são efetivamente carregados
"""

import importlib
import logging
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flask import Flask

log = logging.getLogger(__name__)


def seed_transactions(app) -> None:
    """Insere as transações DS_* se ainda não existirem no banco."""
    from models import Transaction, db
    from transactions.catalog import DS_TRANSACTIONS

    with app.app_context():
        for tx_data in DS_TRANSACTIONS:
            existing = Transaction.query.filter_by(code=tx_data["code"]).first()
            if not existing:
                tx = Transaction(**tx_data)
                db.session.add(tx)
                log.info("Transação seedada: %s", tx_data["code"])
        db.session.commit()


def discover_plugins(app) -> None:
    """
    Escaneia plugins/ e registra cada plugin no banco (is_active=False por padrão).
    Se o plugin já existe no banco, apenas atualiza metadados de descoberta.
    Plugins marcados como is_active=True no banco são então importados.
    """
    from config import Config
    from models import Plugin, Transaction, db

    plugins_dir = Config.PLUGINS_DIR
    if not os.path.isdir(plugins_dir):
        os.makedirs(plugins_dir, exist_ok=True)
        return

    with app.app_context():
        for entry in os.scandir(plugins_dir):
            if not entry.is_dir():
                continue

            manifest_path = os.path.join(entry.path, "plugin.json")
            if not os.path.isfile(manifest_path):
                continue

            import json

            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)

            code = manifest.get("code", entry.name)
            plugin = Plugin.query.filter_by(code=code).first()

            if not plugin:
                # Primeiro registro — inativo por padrão
                plugin = Plugin(
                    code=code,
                    name=manifest.get("name", code),
                    description=manifest.get("description"),
                    version=manifest.get("version", "1.0.0"),
                    author=manifest.get("author"),
                    folder_path=entry.path,
                    entry_point=manifest.get("entry_point"),
                    transaction_codes=manifest.get("transactions", []),
                    is_active=False,
                    is_installed=True,
                )
                db.session.add(plugin)
                log.info("Plugin descoberto (inativo): %s", code)
            else:
                # Atualiza metadados mas preserva is_active do banco
                plugin.name = manifest.get("name", code)
                plugin.description = manifest.get("description", plugin.description)
                plugin.version = manifest.get("version", plugin.version)
                plugin.folder_path = entry.path
                plugin.transaction_codes = manifest.get(
                    "transactions", plugin.transaction_codes
                )

        db.session.commit()

        # Importa apenas plugins ativos
        active_plugins = Plugin.query.filter_by(is_active=True, is_installed=True).all()
        for plugin in active_plugins:
            _load_plugin(plugin, db)

        db.session.commit()


def _load_plugin(plugin, db) -> None:
    """Importa o entry_point do plugin e registra suas transações NDS_*."""
    from models import Transaction

    if not plugin.entry_point:
        return

    try:
        mod = importlib.import_module(plugin.entry_point)
        tx_definitions = getattr(mod, "TRANSACTIONS", [])

        for tx_data in tx_definitions:
            existing = Transaction.query.filter_by(code=tx_data["code"]).first()
            if not existing:
                tx = Transaction(
                    code=tx_data["code"],
                    label=tx_data.get("label", tx_data["code"]),
                    group=tx_data.get("group", "Plugin"),
                    description=tx_data.get("description"),
                    icon=tx_data.get("icon", "bi-puzzle"),
                    route=tx_data.get("route", "#"),
                    min_profile=tx_data.get("min_profile", "DEVELOPER"),
                    is_standard=False,
                    plugin_code=plugin.code,
                )
                db.session.add(tx)
                log.info(
                    "Transação NDS_ registrada: %s (plugin: %s)",
                    tx_data["code"],
                    plugin.code,
                )

    except Exception as exc:
        log.error("Erro ao carregar plugin %s: %s", plugin.code, exc)
