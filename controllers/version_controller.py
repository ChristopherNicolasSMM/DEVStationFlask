"""
controllers/version_controller.py — API de Versionamento
==========================================================
  GET    /api/paginas/<pgid>/versoes               → lista versões da página
  POST   /api/paginas/<pgid>/versoes               → cria versão nomeada
  GET    /api/versoes/<vid>                         → detalhe de uma versão
  POST   /api/versoes/<vid>/restaurar              → restaura página para esta versão
  DELETE /api/versoes/<vid>                         → deleta (gera .dsk antes)
  GET    /api/paginas/<pgid>/versoes/sugestoes-purga → lista sugeridas para purga
  POST   /api/projetos/<pid>/reset                 → reset do projeto para versão/data
  GET    /api/versoes/backups/<project_id>         → lista backups .dsk do projeto
  GET    /api/versoes/backups/<bid>/download       → baixa arquivo .dsk
"""

import os

from flask import Blueprint, jsonify, request, send_file

from models import Page, PageVersion, Project, VersionBackup, db
from versioning import (create_named_snapshot, delete_version_with_backup,
                        diff_versions, get_purge_suggestions, restore_snapshot)

bp = Blueprint("version", __name__)


# ── Listar versões ────────────────────────────────────────────────────────────


@bp.route("/api/paginas/<int:pgid>/versoes")
def list_versions(pgid: int):
    page = Page.query.get_or_404(pgid)
    include_deleted = request.args.get("deleted", "0") == "1"

    query = PageVersion.query.filter_by(page_id=pgid)
    if not include_deleted:
        query = query.filter_by(deleted=False)

    versions = query.order_by(PageVersion.created_at.desc()).all()
    return jsonify([v.to_dict() for v in versions])


# ── Criar versão nomeada ──────────────────────────────────────────────────────


@bp.route("/api/paginas/<int:pgid>/versoes", methods=["POST"])
def create_version(pgid: int):
    page = Page.query.get_or_404(pgid)
    data = request.get_json(force=True) or {}

    label = (data.get("label") or "").strip()
    if not label:
        return jsonify({"error": "label é obrigatório"}), 400

    version = create_named_snapshot(
        page,
        label=label,
        description=data.get("description", ""),
        author=data.get("author", "usuario"),
        tags=data.get("tags", []),
    )
    return jsonify(version.to_dict()), 201


# ── Detalhe de uma versão ─────────────────────────────────────────────────────


@bp.route("/api/versoes/<int:vid>")
def get_version(vid: int):
    version = PageVersion.query.get_or_404(vid)
    include_snapshot = request.args.get("snapshot", "0") == "1"
    return jsonify(version.to_dict(include_snapshot=include_snapshot))


# ── Diff entre duas versões ───────────────────────────────────────────────────


@bp.route("/api/versoes/diff")
def diff_two_versions():
    """
    Compara duas versões.
    Query params: a=<vid_a>&b=<vid_b>
    """
    vid_a = request.args.get("a", type=int)
    vid_b = request.args.get("b", type=int)
    if not vid_a or not vid_b:
        return jsonify({"error": "Parâmetros a e b são obrigatórios"}), 400

    va = PageVersion.query.get_or_404(vid_a)
    vb = PageVersion.query.get_or_404(vid_b)

    result = diff_versions(va.snapshot or {}, vb.snapshot or {})
    result["version_a"] = va.to_dict()
    result["version_b"] = vb.to_dict()
    return jsonify(result)


# ── Restaurar versão ──────────────────────────────────────────────────────────


@bp.route("/api/versoes/<int:vid>/restaurar", methods=["POST"])
def restore_version(vid: int):
    """
    Restaura a página para o estado desta versão.
    Cria automaticamente snapshot pré-restauração.
    """
    data = request.get_json(force=True) or {}
    author = data.get("triggered_by", "usuario")

    result = restore_snapshot(vid, triggered_by=author)
    return jsonify(result)


# ── Deletar versão (com .dsk obrigatório) ─────────────────────────────────────


@bp.route("/api/versoes/<int:vid>", methods=["DELETE"])
def delete_version(vid: int):
    """
    Deleta versão APÓS gerar backup .dsk.
    O backup fica registrado em VersionBackup.
    """
    data = request.get_json(force=True) or {}
    author = data.get("triggered_by", "usuario")

    result = delete_version_with_backup(vid, triggered_by=author)
    if not result.get("ok"):
        return jsonify(result), 400
    return jsonify(result)


# ── Sugestões de purga ────────────────────────────────────────────────────────


@bp.route("/api/paginas/<int:pgid>/versoes/sugestoes-purga")
def purge_suggestions(pgid: int):
    Page.query.get_or_404(pgid)
    suggestions = get_purge_suggestions(pgid)
    return jsonify(suggestions)


# ── Reset de projeto ──────────────────────────────────────────────────────────


@bp.route("/api/projetos/<int:pid>/reset", methods=["POST"])
def project_reset(pid: int):
    """
    Restaura múltiplas páginas do projeto para versões especificadas.

    Body JSON:
        {
          "triggered_by": "usuario",
          "pages": [
            {"page_id": 1, "version_id": 5},
            {"page_id": 2, "version_id": 8}
          ]
        }

    Antes de qualquer restauração, cria snapshots pré-reset em todas as páginas.
    """
    project = Project.query.get_or_404(pid)
    data = request.get_json(force=True) or {}
    pages = data.get("pages", [])
    author = data.get("triggered_by", "usuario")

    if not pages:
        return jsonify({"error": "Forneça ao menos uma página para restaurar"}), 400

    results = []
    pre_snapshots = []

    for entry in pages:
        page_id = entry.get("page_id")
        version_id = entry.get("version_id")
        if not page_id or not version_id:
            continue

        page = Page.query.get(page_id)
        if not page or page.project_id != pid:
            results.append(
                {"page_id": page_id, "ok": False, "error": "Página não encontrada"}
            )
            continue

        result = restore_snapshot(version_id, triggered_by=author)
        results.append({"page_id": page_id, "version_id": version_id, **result})

    return jsonify({"ok": True, "results": results})


# ── Backups .dsk ──────────────────────────────────────────────────────────────


@bp.route("/api/versoes/backups/<int:project_id>")
def list_backups(project_id: int):
    Project.query.get_or_404(project_id)
    backups = (
        VersionBackup.query.filter_by(project_id=project_id)
        .order_by(VersionBackup.created_at.desc())
        .all()
    )
    return jsonify([b.to_dict() for b in backups])


@bp.route("/api/versoes/backups/<int:bid>/download")
def download_backup(bid: int):
    """Retorna o arquivo .dsk para download."""
    backup = VersionBackup.query.get_or_404(bid)
    if not os.path.isfile(backup.backup_path):
        return jsonify({"error": "Arquivo .dsk não encontrado no disco."}), 404

    return send_file(
        backup.backup_path,
        as_attachment=True,
        download_name=backup.backup_name,
        mimetype="application/zip",
    )
