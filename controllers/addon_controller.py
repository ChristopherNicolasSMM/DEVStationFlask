"""
controllers/addon_controller.py — Gerenciador de Addons (DS_ADDONS)
====================================================================
  GET  /api/addons                      → lista todos os addons
  GET  /api/addons/<code>               → detalhe + histórico de log
  POST /api/addons/upload               → faz upload do pacote ZIP do addon
  POST /api/addons/<code>/instalar      → inicia instalação (requer confirmação)
  POST /api/addons/<code>/ativar        → ativa addon instalado
  POST /api/addons/<code>/desativar     → desativa addon
  DELETE /api/addons/<code>             → remove addon (com confirmação)
  GET  /api/addons/<code>/logs          → histórico de ações do addon
"""

import os
import json
import zipfile
import datetime
import logging

from flask import Blueprint, jsonify, request, current_app
from models import db, Addon, AddonLog

bp  = Blueprint("addon", __name__)
log = logging.getLogger(__name__)


def _log(addon: Addon, action: str, status: str,
         detail: str = "", author: str = "sistema") -> AddonLog:
    """Registra uma ação no AddonLog. Sempre chamado ANTES de executar a ação."""
    entry = AddonLog(
        addon_id=addon.id,
        addon_code=addon.code,
        action=action,
        status=status,
        detail=detail,
        triggered_by=author,
    )
    db.session.add(entry)
    return entry


# ── Listagem ──────────────────────────────────────────────────────────────────

@bp.route("/api/addons")
def list_addons():
    addons = Addon.query.order_by(Addon.name).all()
    return jsonify([a.to_dict() for a in addons])


@bp.route("/api/addons/<string:code>")
def get_addon(code: str):
    addon = Addon.query.filter_by(code=code).first_or_404()
    logs  = (AddonLog.query
             .filter_by(addon_id=addon.id)
             .order_by(AddonLog.created_at.desc())
             .limit(50).all())
    d = addon.to_dict()
    d["logs"] = [l.to_dict() for l in logs]
    return jsonify(d)


@bp.route("/api/addons/<string:code>/logs")
def addon_logs(code: str):
    addon = Addon.query.filter_by(code=code).first_or_404()
    logs  = (AddonLog.query
             .filter_by(addon_id=addon.id)
             .order_by(AddonLog.created_at.desc())
             .all())
    return jsonify([l.to_dict() for l in logs])


# ── Upload de pacote ──────────────────────────────────────────────────────────

@bp.route("/api/addons/upload", methods=["POST"])
def upload_addon():
    """
    Recebe o ZIP do addon, valida o manifesto addon.json e
    registra o addon como 'available' — NÃO instala automaticamente.
    """
    author = request.form.get("triggered_by", "usuario")

    if "file" not in request.files:
        return jsonify({"error": "Arquivo não enviado"}), 400

    file = request.files["file"]
    if not file.filename.endswith(".zip"):
        return jsonify({"error": "Apenas arquivos .zip são aceitos"}), 400

    addons_dir = current_app.config.get("ADDONS_DIR",
                                        os.path.join(os.path.dirname(__file__), "../addons"))
    os.makedirs(addons_dir, exist_ok=True)

    # Salva o ZIP temporariamente
    tmp_path = os.path.join(addons_dir, f"_upload_{file.filename}")
    file.save(tmp_path)

    # Valida e lê manifesto
    try:
        with zipfile.ZipFile(tmp_path, "r") as zf:
            names = zf.namelist()
            manifest_candidates = [n for n in names if n.endswith("addon.json")]
            if not manifest_candidates:
                os.remove(tmp_path)
                return jsonify({"error": "addon.json não encontrado no pacote"}), 400

            manifest_raw = zf.read(manifest_candidates[0])
            manifest     = json.loads(manifest_raw)
    except (zipfile.BadZipFile, json.JSONDecodeError) as exc:
        if os.path.isfile(tmp_path):
            os.remove(tmp_path)
        return jsonify({"error": f"Pacote inválido: {exc}"}), 400

    code = manifest.get("code")
    if not code:
        os.remove(tmp_path)
        return jsonify({"error": "Campo 'code' ausente no addon.json"}), 400

    # Verifica se já existe
    existing = Addon.query.filter_by(code=code).first()
    if existing:
        os.remove(tmp_path)
        return jsonify({"error": f"Addon '{code}' já registrado. Remova primeiro."}), 409

    # Registra addon como 'available' (não instalado)
    addon = Addon(
        code=code,
        name=manifest.get("name", code),
        description=manifest.get("description"),
        version=manifest.get("version", "1.0.0"),
        author=manifest.get("author"),
        addon_type=manifest.get("type", "component"),
        package_path=tmp_path,
        manifest=manifest,
        status="available",
        is_active=False,
    )
    db.session.add(addon)
    db.session.flush()

    _log(addon, "upload_package", "success",
         f"Pacote {file.filename} recebido. Entidades: {', '.join(names[:5])}.", author)
    db.session.commit()

    log.info("Addon '%s' carregado (aguardando instalação)", code)
    return jsonify({"ok": True, "addon": addon.to_dict()}), 201


# ── Instalar ──────────────────────────────────────────────────────────────────

@bp.route("/api/addons/<string:code>/instalar", methods=["POST"])
def install_addon(code: str):
    """
    Inicia a instalação do addon.
    Requer 'confirmed': true — NUNCA instala automaticamente.
    Cada passo é registrado no AddonLog.
    """
    data      = request.get_json(force=True) or {}
    confirmed = data.get("confirmed", False)
    author    = data.get("triggered_by", "usuario")

    if not confirmed:
        return jsonify({
            "error": "Instalação requer confirmed: true. Revise o manifesto antes de confirmar."
        }), 400

    addon = Addon.query.filter_by(code=code).first_or_404()

    if addon.status == "installed":
        return jsonify({"ok": True, "message": "Addon já está instalado.", "addon": addon.to_dict()})

    if addon.status != "available":
        return jsonify({"error": f"Addon está em status '{addon.status}', não pode ser instalado."}), 400

    errors = []

    # ── Passo 1: Validar manifesto ────────────────────────────────
    addon.status = "pending_install"
    _log(addon, "validate_manifest", "pending", "Iniciando validação do manifesto.", author)
    db.session.flush()

    required_fields = ["code", "name", "version"]
    missing = [f for f in required_fields if not addon.manifest.get(f)]
    if missing:
        _log(addon, "validate_manifest", "error", f"Campos ausentes: {missing}", author)
        addon.status = "error"
        db.session.commit()
        return jsonify({"error": f"Manifesto inválido: campos ausentes: {missing}"}), 400

    _log(addon, "validate_manifest", "success", "Manifesto válido.", author)
    db.session.flush()

    # ── Passo 2: Extrair arquivos ─────────────────────────────────
    addons_dir   = current_app.config.get("ADDONS_DIR",
                                          os.path.join(os.path.dirname(__file__), "../addons"))
    install_path = os.path.join(addons_dir, code)
    os.makedirs(install_path, exist_ok=True)

    _log(addon, "extract_files", "pending", f"Extraindo para {install_path}", author)
    db.session.flush()

    try:
        with zipfile.ZipFile(addon.package_path, "r") as zf:
            zf.extractall(install_path)
        _log(addon, "extract_files", "success", "Arquivos extraídos.", author)
    except Exception as exc:
        _log(addon, "extract_files", "error", str(exc), author)
        addon.status = "error"
        db.session.commit()
        return jsonify({"error": f"Erro ao extrair: {exc}"}), 500

    db.session.flush()

    # ── Passo 3: Confirmar instalação ─────────────────────────────
    _log(addon, "confirm_install", "success",
         f"Addon {code} v{addon.version} instalado com sucesso.", author)

    addon.status       = "installed"
    addon.install_path = install_path
    addon.installed_at = datetime.datetime.utcnow()
    addon.installed_by = author
    # Não ativa automaticamente — requer ação adicional
    addon.is_active    = False

    db.session.commit()
    log.info("Addon '%s' instalado por '%s'", code, author)
    return jsonify({"ok": True, "addon": addon.to_dict()})


# ── Ativar / Desativar ────────────────────────────────────────────────────────

@bp.route("/api/addons/<string:code>/ativar", methods=["POST"])
def activate_addon(code: str):
    """Ativa addon instalado (requer confirmed: true)."""
    data      = request.get_json(force=True) or {}
    confirmed = data.get("confirmed", False)
    author    = data.get("triggered_by", "usuario")

    if not confirmed:
        return jsonify({"error": "Ativação requer confirmed: true."}), 400

    addon = Addon.query.filter_by(code=code).first_or_404()
    if addon.status != "installed":
        return jsonify({"error": f"Addon deve estar instalado. Status atual: '{addon.status}'"}), 400

    addon.is_active = True
    _log(addon, "activate", "success", f"Addon ativado por {author}.", author)
    db.session.commit()
    return jsonify({"ok": True, "addon": addon.to_dict()})


@bp.route("/api/addons/<string:code>/desativar", methods=["POST"])
def deactivate_addon(code: str):
    author = (request.get_json(force=True) or {}).get("triggered_by", "usuario")
    addon  = Addon.query.filter_by(code=code).first_or_404()
    addon.is_active = False
    _log(addon, "deactivate", "success", f"Addon desativado por {author}.", author)
    db.session.commit()
    return jsonify({"ok": True, "addon": addon.to_dict()})


# ── Remover ───────────────────────────────────────────────────────────────────

@bp.route("/api/addons/<string:code>", methods=["DELETE"])
def remove_addon(code: str):
    """Remove addon do banco (requer confirmed: true)."""
    data      = request.get_json(force=True) or {}
    confirmed = data.get("confirmed", False)
    author    = data.get("triggered_by", "usuario")

    if not confirmed:
        return jsonify({"error": "Remoção requer confirmed: true."}), 400

    addon = Addon.query.filter_by(code=code).first_or_404()
    _log(addon, "uninstall", "success", f"Addon removido por {author}.", author)
    db.session.flush()
    db.session.delete(addon)
    db.session.commit()
    return jsonify({"ok": True})
