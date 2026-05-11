"""
app.py — Application Factory v3.0
====================================
Cria e configura a aplicação Flask com todos os blueprints,
modelos, seed de transações e descoberta de plugins.
"""

from flask import Flask

from config import Config
from models import db


def create_app(test_config: dict = None) -> Flask:
    """
    Fábrica da aplicação Flask.

    Args:
        test_config: dicionário de overrides de configuração para testes.
    """
    app = Flask(__name__, template_folder="views", static_folder="static")
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    # ── Banco de Dados ────────────────────────────────────────────
    db.init_app(app)
    with app.app_context():
        db.create_all()

    # ── Blueprints ────────────────────────────────────────────────
    from controllers import register_blueprints

    register_blueprints(app)

    # ── Seed inicial de transações DS_* ───────────────────────────
    with app.app_context():
        from transactions.registry import discover_plugins, seed_transactions

        seed_transactions(app)
        discover_plugins(app)

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(debug=True, port=5000)
