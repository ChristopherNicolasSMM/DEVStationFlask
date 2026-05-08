"""
models/transaction.py — Catálogo de Transações
================================================
Registra todas as transações DS_* (nativas) e NDS_* (customizadas/plugins).
Alimentado pelo seed inicial e pela descoberta automática de plugins.
"""

import datetime
from models import db


class Transaction(db.Model):
    """Transação navegável da plataforma DevStation."""

    __tablename__ = "transactions"

    # ── Identificação ─────────────────────────────────────────────
    id          = db.Column(db.Integer,     primary_key=True)
    code        = db.Column(db.String(50),  unique=True, nullable=False, index=True)  # DS_DESIGNER
    label       = db.Column(db.String(100), nullable=False)               # "Visual Designer"
    group       = db.Column(db.String(50),  nullable=False, default="Core")  # Design | Integration | DevOps | Admin
    description = db.Column(db.String(300), nullable=True)
    icon        = db.Column(db.String(50),  default="bi-app")             # Bootstrap Icon class

    # ── Roteamento ────────────────────────────────────────────────
    route       = db.Column(db.String(300), nullable=False)               # URL relativa Flask
    # Parâmetros da rota podem conter placeholders: /designer/{pid}
    route_params = db.Column(db.JSON, default=dict)

    # ── Controle de acesso ────────────────────────────────────────
    min_profile = db.Column(db.String(20), default="USER")               # USER|PUSER|BANALYST|DEVELOPER|...
    is_active   = db.Column(db.Boolean, default=True)
    is_standard = db.Column(db.Boolean, default=True)                    # False = NDS_* (plugin)

    # ── Origem ────────────────────────────────────────────────────
    plugin_code = db.Column(db.String(100), nullable=True)               # código do plugin de origem (NDS_*)

    # ── Timestamps ────────────────────────────────────────────────
    created_at  = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id":           self.id,
            "code":         self.code,
            "label":        self.label,
            "group":        self.group,
            "description":  self.description,
            "icon":         self.icon,
            "route":        self.route,
            "route_params": self.route_params or {},
            "min_profile":  self.min_profile,
            "is_active":    self.is_active,
            "is_standard":  self.is_standard,
            "plugin_code":  self.plugin_code,
            "created_at":   self.created_at.strftime("%d/%m/%Y %H:%M") if self.created_at else None,
        }

    def __repr__(self):
        return f"<Transaction code={self.code!r} label={self.label!r}>"
