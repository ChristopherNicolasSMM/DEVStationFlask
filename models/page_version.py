"""
models/page_version.py — Versionamento de Páginas
===================================================
Armazena snapshots completos de páginas (componentes incluídos).
Nunca purga automaticamente — exibe lista de sugestão para o usuário decidir.
Ao apagar uma versão, sempre gera backup .dsk antes.
"""

import datetime
from models import db


class PageVersion(db.Model):
    """Snapshot completo de uma página em um dado momento."""

    __tablename__ = "page_versions"

    # ── Identificação ─────────────────────────────────────────────
    id            = db.Column(db.Integer,     primary_key=True)
    page_id       = db.Column(db.Integer,     db.ForeignKey("pages.id"), nullable=False)
    project_id    = db.Column(db.Integer,     db.ForeignKey("projects.id"), nullable=False)

    # ── Metadados da versão ───────────────────────────────────────
    version_label = db.Column(db.String(50),  nullable=False)   # "v1.0", "pre-odata", "sprint-3"
    description   = db.Column(db.String(300), nullable=True)
    author        = db.Column(db.String(100), default="sistema")

    # ── Tipo ──────────────────────────────────────────────────────
    is_auto       = db.Column(db.Boolean, default=False)        # True = snapshot automático ao salvar
    tags          = db.Column(db.JSON,    default=list)          # ["odata-gen", "sprint-3"]

    # ── Conteúdo ──────────────────────────────────────────────────
    # Cópia completa de page.to_dict(include_components=True)
    snapshot      = db.Column(db.JSON, nullable=False)

    # ── Purga ─────────────────────────────────────────────────────
    purge_suggested = db.Column(db.Boolean, default=False)       # True = sugerido para purga
    purge_reason    = db.Column(db.String(200), nullable=True)   # motivo da sugestão
    deleted         = db.Column(db.Boolean, default=False)       # soft-delete (aguarda bkp)
    deleted_at      = db.Column(db.DateTime, nullable=True)
    deleted_by      = db.Column(db.String(100), nullable=True)
    backup_path     = db.Column(db.String(500), nullable=True)   # caminho do .dsk gerado

    # ── Timestamps ────────────────────────────────────────────────
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, index=True)

    def to_dict(self, include_snapshot: bool = False) -> dict:
        d = {
            "id":               self.id,
            "page_id":          self.page_id,
            "project_id":       self.project_id,
            "version_label":    self.version_label,
            "description":      self.description,
            "author":           self.author,
            "is_auto":          self.is_auto,
            "tags":             self.tags or [],
            "purge_suggested":  self.purge_suggested,
            "purge_reason":     self.purge_reason,
            "deleted":          self.deleted,
            "deleted_at":       self._fmt(self.deleted_at),
            "deleted_by":       self.deleted_by,
            "backup_path":      self.backup_path,
            "created_at":       self._fmt(self.created_at),
            "component_count":  len((self.snapshot or {}).get("components", [])),
        }
        if include_snapshot:
            d["snapshot"] = self.snapshot
        return d

    @staticmethod
    def _fmt(dt):
        return dt.strftime("%d/%m/%Y %H:%M:%S") if dt else None

    def __repr__(self):
        return f"<PageVersion id={self.id} label={self.version_label!r} page={self.page_id}>"
