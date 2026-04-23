"""
DevStation Builder — Entry Point
=================================
Inicializa o Flask, registra os Blueprints (controllers) e
garante a criação das tabelas no banco na primeira execução.
"""

from flask import Flask
from config import Config
from models import db
from controllers import register_blueprints


def create_app(config_class=Config) -> Flask:
    """
    Application Factory Pattern.
    Permite instanciar a app com configurações diferentes
    (produção, teste, desenvolvimento).
    """
    app = Flask(
        __name__,
        template_folder="views",      # camada VIEW em /views/
        static_folder="static",
    )
    app.config.from_object(config_class)

    # ── Inicializa extensões ──────────────────────────────────────
    db.init_app(app)

    # ── Registra todos os Blueprints (Controllers) ────────────────
    register_blueprints(app)

    # ── Cria tabelas se não existirem ─────────────────────────────
    with app.app_context():
        db.create_all()

    return app


# Ponto de entrada direto
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
