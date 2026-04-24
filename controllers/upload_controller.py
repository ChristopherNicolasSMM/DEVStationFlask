"""
controllers/upload_controller.py — Upload de Imagens
======================================================
Gerencia upload de imagens para uso nos componentes.

  POST /upload/imagem          → faz upload e retorna URL
  GET  /upload/listar          → lista imagens disponíveis
  DEL  /upload/imagem/<nome>   → remove uma imagem
"""

import os
import uuid
import datetime
from flask import Blueprint, request, jsonify, current_app

bp = Blueprint("upload", __name__)

# Extensões permitidas para upload
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "svg"}
MAX_SIZE_MB = 5


def _allowed(filename: str) -> bool:
    """Verifica se a extensão do arquivo é permitida."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def _upload_dir() -> str:
    """Retorna o caminho absoluto da pasta de uploads, criando se necessário."""
    upload_path = os.path.join(current_app.static_folder, "uploads")
    os.makedirs(upload_path, exist_ok=True)
    return upload_path


@bp.route("/upload/imagem", methods=["POST"])
def upload_image():
    """
    Recebe um arquivo de imagem via multipart/form-data.
    Retorna JSON com a URL pública da imagem.
    """
    if "file" not in request.files:
        return jsonify({"ok": False, "error": "Nenhum arquivo enviado."}), 400

    file = request.files["file"]

    if not file.filename:
        return jsonify({"ok": False, "error": "Nome de arquivo vazio."}), 400

    if not _allowed(file.filename):
        return jsonify({
            "ok": False,
            "error": f"Extensão não permitida. Use: {', '.join(ALLOWED_EXTENSIONS)}"
        }), 400

    # Verifica tamanho (lê até MAX_SIZE + 1 byte para checar)
    file.seek(0, 2)  # Vai para o final
    size_bytes = file.tell()
    file.seek(0)     # Volta ao início
    if size_bytes > MAX_SIZE_MB * 1024 * 1024:
        return jsonify({"ok": False, "error": f"Arquivo muito grande. Máximo: {MAX_SIZE_MB}MB"}), 400

    # Gera nome único para evitar colisões
    ext       = file.filename.rsplit(".", 1)[1].lower()
    unique_name = f"{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.{ext}"
    save_path = os.path.join(_upload_dir(), unique_name)

    file.save(save_path)

    url = f"/static/uploads/{unique_name}"
    return jsonify({
        "ok":       True,
        "url":      url,
        "filename": unique_name,
        "size_kb":  round(size_bytes / 1024, 1),
    })


@bp.route("/upload/listar")
def list_images():
    """
    Retorna lista de imagens já enviadas.
    Útil para o seletor de imagem no painel de propriedades.
    """
    try:
        upload_path = _upload_dir()
        files = []
        for fname in sorted(os.listdir(upload_path), reverse=True):
            if _allowed(fname):
                fpath = os.path.join(upload_path, fname)
                fsize = os.path.getsize(fpath)
                files.append({
                    "filename": fname,
                    "url":      f"/static/uploads/{fname}",
                    "size_kb":  round(fsize / 1024, 1),
                    "modified": os.path.getmtime(fpath),
                })
        return jsonify({"ok": True, "images": files, "count": len(files)})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@bp.route("/upload/imagem/<string:filename>", methods=["DELETE"])
def delete_image(filename: str):
    """Remove uma imagem da pasta de uploads."""
    # Sanitização: não permite navegação de diretórios
    if ".." in filename or "/" in filename or "\\" in filename:
        return jsonify({"ok": False, "error": "Nome de arquivo inválido."}), 400

    try:
        file_path = os.path.join(_upload_dir(), filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return jsonify({"ok": True, "deleted": filename})
        return jsonify({"ok": False, "error": "Arquivo não encontrado."}), 404
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500
