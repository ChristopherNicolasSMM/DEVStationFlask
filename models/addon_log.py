"""
models/addon_log.py — Log de Instalação de Addons
===================================================
Registro imutável de TODAS as ações realizadas durante
instalação, ativação, desativação ou remoção de addons.
Nenhuma ação ocorre sem log registrado primeiro.
"""

import datetime
from models import db


class AddonLog(db.Model):
    """Log imutável de ações sobre addons."""

    __tablename__ = "addon_logs"

    id          = db.Column(db.Integer,     primary_key=True)
    addon_id    = db.Column(db.Integer,     db.ForeignKey("addons.id"), nullable=False)
    addon_code  = db.Column(db.String(100), nullable=False)         # desnormalizado para consulta

    # ── Ação ──────────────────────────────────────────────────────
    action      = db.Column(db.String(50),  nullable=False)
    # upload_package | validate_manifest | confirm_install | extract_files
    # register_components | activate | deactivate | uninstall | error

    status      = db.Column(db.String(20),  nullable=False)         # pending | success | error
    detail      = db.Column(db.Text,        nullable=True)          # mensagem detalhada
    triggered_by = db.Column(db.String(100), default="sistema")
    created_at  = db.Column(db.DateTime, default=datetime.datetime.utcnow, index=True)

    def to_dict(self) -> dict:
        return {
            "id":            self.id,
            "addon_id":      self.addon_id,
            "addon_code":    self.addon_code,
            "action":        self.action,
            "status":        self.status,
            "detail":        self.detail,
            "triggered_by":  self.triggered_by,
            "created_at":    self.created_at.strftime("%d/%m/%Y %H:%M:%S") if self.created_at else None,
        }

    def __repr__(self):
        return f"<AddonLog addon={self.addon_code!r} action={self.action!r} status={self.status!r}>"
