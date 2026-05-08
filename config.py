"""
config.py — Configurações Centralizadas v3.0
=============================================
Todas as configurações ficam aqui para não ficar espalhadas
pelo código. Para múltiplos ambientes, basta herdar Config.
"""

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Configuração base (development)."""

    # ── Flask ─────────────────────────────────────────────────────
    SECRET_KEY = os.environ.get("SECRET_KEY", "devstation-builder-secret-v3")
    DEBUG = os.environ.get("DEBUG", "true").lower() == "true"

    # ── Banco de Dados ────────────────────────────────────────────
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(BASE_DIR, 'instance/devstation.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ── Canvas defaults ───────────────────────────────────────────
    DEFAULT_CANVAS_W  = 1280
    DEFAULT_CANVAS_H  = 900
    DEFAULT_CANVAS_BG = "#ffffff"

    # ── Exportação ────────────────────────────────────────────────
    EXPORT_TEMP_DIR = os.path.join(BASE_DIR, "tmp_exports")

    # ── Versionamento ─────────────────────────────────────────────
    # Número de snapshots automáticos a SUGERIR para purga (sem purga automática)
    VERSION_AUTO_SUGGEST_PURGE_AFTER = 10

    # Extensão dos backups DevStation
    DSK_EXTENSION = ".dsk"

    # ── Plugins ───────────────────────────────────────────────────
    PLUGINS_DIR = os.path.join(BASE_DIR, "plugins")

    # ── Addons ───────────────────────────────────────────────────
    ADDONS_DIR = os.path.join(BASE_DIR, "addons")

    # ── OData ─────────────────────────────────────────────────────
    ODATA_METADATA_TTL_SECONDS = 300   # cache de 5 min

    # ── Build ─────────────────────────────────────────────────────
    BUILD_DIST_DIR = os.path.join(BASE_DIR, "dist")
    BUILD_VERSION  = "3.0.0"


class ProductionConfig(Config):
    """Sobreposição para produção."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", Config.SQLALCHEMY_DATABASE_URI)
