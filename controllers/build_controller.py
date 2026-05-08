"""
controllers/build_controller.py — DS_BUILD Pipeline
=====================================================
  POST /api/build/run-tests    → executa pytest e salva BuildLog
  GET  /api/build/status       → último resultado de build
  POST /api/build/create-zip   → gera ZIP de distribuição
  GET  /api/build/logs         → histórico de builds
  GET  /api/build/logs/<id>    → detalhe de um build (com test_output)
"""

import os
import io
import zipfile
import datetime
import subprocess
import threading
import logging

from flask import Blueprint, jsonify, request, current_app, send_file
from models import db, BuildLog

bp  = Blueprint("build", __name__)
log = logging.getLogger(__name__)

# ── Executar testes ───────────────────────────────────────────────────────────

@bp.route("/api/build/run-tests", methods=["POST"])
def run_tests():
    """
    Executa o pytest de forma assíncrona (thread separada).
    Cria um BuildLog em status 'running' e retorna imediatamente.
    O resultado é atualizado no banco ao final.
    """
    data    = request.get_json(force=True) or {}
    author  = data.get("triggered_by", "usuario")
    version = current_app.config.get("BUILD_VERSION", "3.0.0")

    build = BuildLog(
        version=version,
        status="running",
        triggered_by=author,
    )
    db.session.add(build)
    db.session.commit()

    # Executa em thread para não bloquear a request
    thread = threading.Thread(
        target=_run_pytest,
        args=(build.id, current_app._get_current_object()),
        daemon=True,
    )
    thread.start()

    return jsonify({"ok": True, "build_id": build.id, "status": "running"})


def _run_pytest(build_id: int, app) -> None:
    """Executa pytest e atualiza o BuildLog no banco."""
    with app.app_context():
        build = BuildLog.query.get(build_id)
        if not build:
            return

        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        cmd      = ["python", "-m", "pytest", "tests/", "-v", "--tb=short", "--no-header"]

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=120, cwd=base_dir
            )
            output  = (result.stdout or "") + (result.stderr or "")
            passed  = output.count(" PASSED")
            failed  = output.count(" FAILED")
            errors  = output.count(" ERROR")

            build.tests_total  = passed + failed + errors
            build.tests_passed = passed
            build.tests_failed = failed
            build.tests_errors = errors
            build.test_output  = output[:20000]  # limita a 20k chars
            build.status       = "passed" if failed == 0 and errors == 0 else "failed"
            build.finished_at  = datetime.datetime.utcnow()

        except subprocess.TimeoutExpired:
            build.status      = "error"
            build.test_output = "Timeout após 120s"
            build.finished_at = datetime.datetime.utcnow()
        except Exception as exc:
            build.status      = "error"
            build.test_output = str(exc)
            build.finished_at = datetime.datetime.utcnow()

        db.session.commit()
        log.info("Build %s finalizado: %s", build_id, build.status)


# ── Status do último build ────────────────────────────────────────────────────

@bp.route("/api/build/status")
def build_status():
    latest = BuildLog.query.order_by(BuildLog.started_at.desc()).first()
    if not latest:
        return jsonify({"ok": True, "build": None})
    return jsonify({"ok": True, "build": latest.to_dict()})


# ── Gerar ZIP de distribuição ─────────────────────────────────────────────────

@bp.route("/api/build/create-zip", methods=["POST"])
def create_zip():
    """
    Gera o ZIP de distribuição do código.
    Só executa se o último build foi 'passed'.
    """
    data      = request.get_json(force=True) or {}
    force     = data.get("force", False)   # ignora checagem de build se True
    author    = data.get("triggered_by", "usuario")

    latest = BuildLog.query.order_by(BuildLog.started_at.desc()).first()
    if not force and latest and latest.status != "passed":
        return jsonify({
            "error": "Último build não passou nos testes. Use force=true para ignorar."
        }), 400

    version  = current_app.config.get("BUILD_VERSION", "3.0.0")
    dist_dir = current_app.config.get("BUILD_DIST_DIR",
                                      os.path.join(os.path.dirname(__file__), "../dist"))
    os.makedirs(dist_dir, exist_ok=True)

    ts       = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    zip_name = f"devstation_builder_v{version}_{ts}.zip"
    zip_path = os.path.join(dist_dir, zip_name)
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    _EXCLUDE_DIRS  = {".git", "__pycache__", "instance", "dist", ".venv",
                      "venv", "tmp_exports", ".pytest_cache", "node_modules"}
    _EXCLUDE_EXTS  = {".pyc", ".pyo", ".db", ".dsk"}

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(base_dir):
            dirs[:] = [d for d in dirs if d not in _EXCLUDE_DIRS]
            for fname in files:
                _, ext = os.path.splitext(fname)
                if ext in _EXCLUDE_EXTS:
                    continue
                full   = os.path.join(root, fname)
                arcname = os.path.relpath(full, base_dir)
                zf.write(full, arcname)

    zip_bytes = buf.getvalue()
    with open(zip_path, "wb") as f:
        f.write(zip_bytes)

    # Registra no último BuildLog ou cria um novo
    if latest:
        latest.zip_path       = zip_path
        latest.zip_name       = zip_name
        latest.zip_size_bytes = len(zip_bytes)
    else:
        record = BuildLog(version=version, status="passed",
                          triggered_by=author,
                          zip_path=zip_path, zip_name=zip_name,
                          zip_size_bytes=len(zip_bytes),
                          finished_at=datetime.datetime.utcnow())
        db.session.add(record)
    db.session.commit()

    return jsonify({
        "ok": True, "zip_name": zip_name,
        "zip_path": zip_path, "size_bytes": len(zip_bytes)
    })


@bp.route("/api/build/zip/<int:bid>/download")
def download_zip(bid: int):
    """Baixa o ZIP gerado pelo build."""
    build = BuildLog.query.get_or_404(bid)
    if not build.zip_path or not os.path.isfile(build.zip_path):
        return jsonify({"error": "ZIP não disponível para este build."}), 404
    return send_file(build.zip_path, as_attachment=True,
                     download_name=build.zip_name, mimetype="application/zip")


# ── Histórico de builds ───────────────────────────────────────────────────────

@bp.route("/api/build/logs")
def build_logs():
    limit = request.args.get("limit", 20, type=int)
    logs  = BuildLog.query.order_by(BuildLog.started_at.desc()).limit(limit).all()
    return jsonify([b.to_dict() for b in logs])


@bp.route("/api/build/logs/<int:bid>")
def build_log_detail(bid: int):
    build = BuildLog.query.get_or_404(bid)
    return jsonify(build.to_dict())
