"""
versioning/snapshot.py — Snapshots e Backups .dsk
===================================================
Funções para criar snapshots de páginas e gerar backups
no formato .dsk (ZIP renomeado = DevStation Backup).

Regras:
 - Versões automáticas antigas NÃO são purgadas automaticamente.
 - O sistema SUGERE purga quando o count ultrapassa o limite.
 - Ao deletar qualquer versão, gera .dsk ANTES da remoção.
 - O backup fica registrado em VersionBackup para rastreabilidade.
"""

import datetime
import io
import json
import logging
import os
import zipfile

log = logging.getLogger(__name__)


# ── Criação de snapshots ─────────────────────────────────────


def create_auto_snapshot(
    page, tags: list = None, author: str = "sistema"
) -> "PageVersion":
    """
    Cria snapshot automático de uma página após save.
    Após criação, marca sugestão de purga se necessário.
    """
    from config import Config
    from models import PageVersion, db

    label = f"auto_{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    snap = page.to_dict(include_components=True)
    version = PageVersion(
        page_id=page.id,
        project_id=page.project_id,
        version_label=label,
        description="Snapshot automático gerado ao salvar.",
        author=author,
        is_auto=True,
        tags=tags or [],
        snapshot=snap,
    )
    db.session.add(version)
    db.session.flush()

    _suggest_purge_if_needed(page, Config.VERSION_AUTO_SUGGEST_PURGE_AFTER)
    db.session.commit()
    log.debug("Auto-snapshot criado: %s (page_id=%s)", label, page.id)
    return version


def create_named_snapshot(
    page, label: str, description: str = "", author: str = "usuario", tags: list = None
) -> "PageVersion":
    """Cria versão nomeada manualmente pelo desenvolvedor."""
    from models import PageVersion, db

    snap = page.to_dict(include_components=True)
    version = PageVersion(
        page_id=page.id,
        project_id=page.project_id,
        version_label=label,
        description=description,
        author=author,
        is_auto=False,
        tags=tags or [],
        snapshot=snap,
    )
    db.session.add(version)
    db.session.commit()
    log.info("Versão nomeada criada: %s (page_id=%s)", label, page.id)
    return version


# ── Restauração ──────────────────────────────────────────────


def restore_snapshot(version_id: int, triggered_by: str = "usuario") -> dict:
    """
    Restaura uma página para o estado de uma versão anterior.
    Cria snapshot pré-restauração antes de executar.

    Returns:
        {"ok": True, "pre_restore_version_id": N}
    """
    from models import Component, Page, PageVersion, db

    version = PageVersion.query.get_or_404(version_id)
    page = Page.query.get_or_404(version.page_id)

    # 1. Snapshot pré-restauração
    pre = create_named_snapshot(
        page,
        label=f"pre_restore_{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
        description=f"Snapshot automático antes de restaurar para '{version.version_label}'.",
        author=triggered_by,
        tags=["pre-restore"],
    )

    # 2. Remove componentes atuais
    for comp in list(page.components):
        db.session.delete(comp)
    db.session.flush()

    # 3. Recria a partir do snapshot
    snap_comps = (version.snapshot or {}).get("components", [])
    for c_data in snap_comps:
        comp = Component(
            page_id=page.id,
            type=c_data.get("type", "label"),
            name=c_data.get("name", "comp"),
            x=int(c_data.get("x", 100)),
            y=int(c_data.get("y", 100)),
            width=int(c_data.get("width", 150)),
            height=int(c_data.get("height", 40)),
            z_index=int(c_data.get("z_index", 1)),
            properties=c_data.get("properties", {}),
            events=c_data.get("events", {}),
            rules=c_data.get("rules", []),
        )
        db.session.add(comp)

    page.updated_at = datetime.datetime.utcnow()
    db.session.commit()
    log.info("Página %s restaurada para versão '%s'", page.id, version.version_label)
    return {"ok": True, "pre_restore_version_id": pre.id}


# ── Purga com backup .dsk ────────────────────────────────────


def delete_version_with_backup(
    version_id: int, triggered_by: str = "usuario", backup_dir: str = None
) -> dict:
    """
    Deleta uma versão APÓS gerar backup .dsk.
    1. Gera arquivo ZIP com os dados da versão
    2. Renomeia para .dsk
    3. Registra em VersionBackup
    4. Marca PageVersion como deleted (soft-delete) e registra backup_path

    Returns:
        {"ok": True, "backup_path": "...", "backup_name": "..."}
    """
    from config import Config
    from models import PageVersion, VersionBackup, db

    version = PageVersion.query.get(version_id)
    if not version:
        return {"ok": False, "error": "Versão não encontrada."}

    if version.deleted:
        return {"ok": False, "error": "Versão já foi deletada."}

    # 1. Define diretório de backup
    if not backup_dir:
        backup_dir = os.path.join(
            os.path.abspath(os.path.dirname(__file__) + "/../"), "dist", "backups"
        )
    os.makedirs(backup_dir, exist_ok=True)

    # 2. Gera nome do arquivo .dsk
    ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    page_slug = str(version.page_id)
    bk_name = (
        f"version_page{page_slug}_{version.version_label}_{ts}{Config.DSK_EXTENSION}"
    )
    bk_path = os.path.join(backup_dir, bk_name)

    # 3. Cria o arquivo .dsk (ZIP com conteúdo JSON da versão)
    payload = {
        "meta": {
            "dsb_version": Config.BUILD_VERSION,
            "backup_type": "page_version",
            "exported_at": datetime.datetime.utcnow().isoformat(),
            "triggered_by": triggered_by,
        },
        "version": version.to_dict(include_snapshot=True),
    }
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("version.json", json.dumps(payload, ensure_ascii=False, indent=2))
        zf.writestr(
            "README.txt",
            f"DevStation Backup (.dsk)\n"
            f"Versão: {version.version_label}\n"
            f"Página ID: {version.page_id}\n"
            f"Gerado em: {datetime.datetime.utcnow()}\n"
            f"Gerado por: {triggered_by}\n"
            f"Restaure usando DS_VERSIONS → Importar Backup\n",
        )
    bk_bytes = buf.getvalue()
    with open(bk_path, "wb") as f:
        f.write(bk_bytes)

    # 4. Registra em VersionBackup
    bk_record = VersionBackup(
        project_id=version.project_id,
        page_id=version.page_id,
        version_id=version.id,
        backup_path=bk_path,
        backup_name=bk_name,
        reason="purge_version",
        triggered_by=triggered_by,
        size_bytes=len(bk_bytes),
    )
    db.session.add(bk_record)

    # 5. Soft-delete da versão
    version.deleted = True
    version.deleted_at = datetime.datetime.utcnow()
    version.deleted_by = triggered_by
    version.backup_path = bk_path

    db.session.commit()
    log.info("Versão %s deletada → backup: %s", version_id, bk_name)
    return {
        "ok": True,
        "backup_path": bk_path,
        "backup_name": bk_name,
        "size_bytes": len(bk_bytes),
    }


# ── Sugestão de purga ────────────────────────────────────────


def _suggest_purge_if_needed(page, threshold: int) -> None:
    """
    Conta versões automáticas não deletadas e, se ultrapassar threshold,
    marca as mais antigas como sugeridas para purga — NUNCA deleta automaticamente.
    """
    from models import PageVersion

    auto_versions = (
        PageVersion.query.filter_by(
            page_id=page.id, is_auto=True, deleted=False, purge_suggested=False
        )
        .order_by(PageVersion.created_at.asc())
        .all()
    )
    excess = len(auto_versions) - threshold
    if excess <= 0:
        return

    # Sugere purga nas mais antigas
    for v in auto_versions[:excess]:
        v.purge_suggested = True
        v.purge_reason = (
            f"Sugerido: existem mais de {threshold} snapshots automáticos "
            f"desta página. Revise e confirme manualmente."
        )
    log.info(
        "%d snapshot(s) automático(s) da página %s marcados como sugeridos para purga.",
        excess,
        page.id,
    )


def get_purge_suggestions(page_id: int) -> list[dict]:
    """Retorna versões sugeridas para purga (para exibição na UI)."""
    from models import PageVersion

    versions = (
        PageVersion.query.filter_by(
            page_id=page_id, purge_suggested=True, deleted=False
        )
        .order_by(PageVersion.created_at.asc())
        .all()
    )
    return [v.to_dict() for v in versions]
