"""
models/plugin.py — Registro de Plugins
========================================
Plugins são descobertos na pasta plugins/ ao iniciar a aplicação.
Só aparecem como ativos se is_active=True no banco.
Nunca são ativados automaticamente — requer ação do usuário.
"""

import datetime
from models import db


class Plugin(db.Model):
    """Plugin NDS_* descoberto na pasta plugins/."""

    __tablename__ = "plugins"

    # ── Identificação ─────────────────────────────────────────────
    id          = db.Column(db.Integer,     primary_key=True)
    code        = db.Column(db.String(100), unique=True, nullable=False)  # "fraterlink"
    name        = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    version     = db.Column(db.String(20),  default="1.0.0")
    author      = db.Column(db.String(100), nullable=True)

    # ── Localização ───────────────────────────────────────────────
    folder_path = db.Column(db.String(500), nullable=False)   # caminho no disco
    entry_point = db.Column(db.String(200), nullable=True)    # "fraterlink.transactions"

    # ── Transações registradas ────────────────────────────────────
    transaction_codes = db.Column(db.JSON, default=list)      # ["NDS_FRATER_MEMBRO", ...]

    # ── Status ────────────────────────────────────────────────────
    is_active    = db.Column(db.Boolean, default=False)        # requer ativação manual
    is_installed = db.Column(db.Boolean, default=False)        # foi registrado no banco

    # ── Timestamps ────────────────────────────────────────────────
    discovered_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    activated_at  = db.Column(db.DateTime, nullable=True)
    activated_by  = db.Column(db.String(100), nullable=True)

    def to_dict(self) -> dict:
        return {
            "id":                self.id,
            "code":              self.code,
            "name":              self.name,
            "description":       self.description,
            "version":           self.version,
            "author":            self.author,
            "folder_path":       self.folder_path,
            "entry_point":       self.entry_point,
            "transaction_codes": self.transaction_codes or [],
            "is_active":         self.is_active,
            "is_installed":      self.is_installed,
            "discovered_at":     self._fmt(self.discovered_at),
            "activated_at":      self._fmt(self.activated_at),
            "activated_by":      self.activated_by,
        }

    @staticmethod
    def _fmt(dt):
        return dt.strftime("%d/%m/%Y %H:%M") if dt else None

    def __repr__(self):
        return f"<Plugin code={self.code!r} active={self.is_active}>"
