"""
config.py — Configurações Centralizadas
========================================
Todas as configurações ficam aqui para não ficar espalhadas
pelo código. Para múltiplos ambientes, basta herdar Config.
"""

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Configuração base (development)."""

    # ── Flask ─────────────────────────────────────────────────────
    SECRET_KEY = os.environ.get("SECRET_KEY", "devstation-builder-secret-2024")
    DEBUG = os.environ.get("DEBUG", "true").lower() == "true"

    # ── Banco de Dados ────────────────────────────────────────────
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(BASE_DIR, 'instance/devstation.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ── Canvas defaults ───────────────────────────────────────────
    DEFAULT_CANVAS_W = 1280
    DEFAULT_CANVAS_H = 900
    DEFAULT_CANVAS_BG = "#ffffff"

    # ── Exportação ────────────────────────────────────────────────
    EXPORT_TEMP_DIR = os.path.join(BASE_DIR, "tmp_exports")


class ProductionConfig(Config):
    """Sobreposição para produção."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", Config.SQLALCHEMY_DATABASE_URI)
