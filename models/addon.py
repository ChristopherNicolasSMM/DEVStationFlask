"""
models/addon.py — Registro de Addons
=======================================
Addons estendem componentes visuais, integrações ou temas.
Instalação NUNCA é automática — requer confirmação explícita.
Todos os passos de instalação são registrados em AddonLog.
"""

import datetime
from models import db


class Addon(db.Model):
    """Addon disponível ou instalado."""

    __tablename__ = "addons"

    # ── Identificação ─────────────────────────────────────────────
    id          = db.Column(db.Integer,     primary_key=True)
    code        = db.Column(db.String(100), unique=True, nullable=False)  # "ds-charts-pro"
    name        = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    version     = db.Column(db.String(20),  default="1.0.0")
    author      = db.Column(db.String(100), nullable=True)
    addon_type  = db.Column(db.String(50),  default="component")  # component | integration | theme

    # ── Localização ───────────────────────────────────────────────
    package_path = db.Column(db.String(500), nullable=True)   # caminho do ZIP de origem
    install_path = db.Column(db.String(500), nullable=True)   # onde foi extraído

    # ── Manifesto ─────────────────────────────────────────────────
    manifest    = db.Column(db.JSON, nullable=True)            # conteúdo do addon.json

    # ── Status ────────────────────────────────────────────────────
    status      = db.Column(db.String(20), default="available")
    # available | pending_install | installed | disabled | error

    is_active   = db.Column(db.Boolean, default=False)        # ativo após instalação confirmada

    # ── Timestamps ────────────────────────────────────────────────
    discovered_at  = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    installed_at   = db.Column(db.DateTime, nullable=True)
    installed_by   = db.Column(db.String(100), nullable=True)

    def to_dict(self) -> dict:
        return {
            "id":            self.id,
            "code":          self.code,
            "name":          self.name,
            "description":   self.description,
            "version":       self.version,
            "author":        self.author,
            "addon_type":    self.addon_type,
            "status":        self.status,
            "is_active":     self.is_active,
            "manifest":      self.manifest or {},
            "discovered_at": self._fmt(self.discovered_at),
            "installed_at":  self._fmt(self.installed_at),
            "installed_by":  self.installed_by,
        }

    @staticmethod
    def _fmt(dt):
        return dt.strftime("%d/%m/%Y %H:%M") if dt else None

    def __repr__(self):
        return f"<Addon code={self.code!r} status={self.status!r}>"
