"""
controllers/odata_controller.py — API OData
============================================
  GET    /api/projetos/<pid>/odata-connections
  POST   /api/projetos/<pid>/odata-connections
  DELETE /api/odata-connections/<cid>
  POST   /api/odata-connections/<cid>/testar
  GET    /api/odata-connections/<cid>/entidades
  POST   /api/odata-connections/<cid>/gerar-tela
"""

from flask import Blueprint, jsonify, request
from models import db, Project, ODataConnection
from odata  import ODataConnectionManager, ODataScreenGenerator

bp = Blueprint("odata", __name__)


# ── CRUD ──────────────────────────────────────────────────────────────────────

@bp.route("/api/projetos/<int:pid>/odata-connections")
def list_connections(pid: int):
    Project.query.get_or_404(pid)
    conns = ODataConnection.query.filter_by(project_id=pid).all()
    return jsonify([c.to_dict() for c in conns])


@bp.route("/api/projetos/<int:pid>/odata-connections", methods=["POST"])
def create_connection(pid: int):
    project = Project.query.get_or_404(pid)
    data    = request.get_json(force=True) or {}

    name    = (data.get("name") or "").strip()
    base_url = (data.get("base_url") or "").strip()
    if not name or not base_url:
        return jsonify({"error": "name e base_url são obrigatórios"}), 400

    conn = ODataConnection(
        project_id=project.id,
        name=name,
        base_url=base_url,
        auth_type=data.get("auth_type", "none"),
        auth_value=data.get("auth_value"),
    )
    db.session.add(conn)
    db.session.commit()
    return jsonify(conn.to_dict()), 201


@bp.route("/api/odata-connections/<int:cid>", methods=["DELETE"])
def delete_connection(cid: int):
    conn = ODataConnection.query.get_or_404(cid)
    db.session.delete(conn)
    db.session.commit()
    return jsonify({"ok": True})


# ── Testar conexão ────────────────────────────────────────────────────────────

@bp.route("/api/odata-connections/<int:cid>/testar", methods=["POST"])
def test_connection(cid: int):
    """Testa a conexão, atualiza cache de metadata e retorna resultado."""
    conn   = ODataConnection.query.get_or_404(cid)
    mgr    = ODataConnectionManager(conn)
    result = mgr.test_connection()
    return jsonify(result)


# ── Entidades ─────────────────────────────────────────────────────────────────

@bp.route("/api/odata-connections/<int:cid>/entidades")
def list_entities(cid: int):
    """Lista entidades disponíveis no servidor OData com anotações de UI."""
    conn    = ODataConnection.query.get_or_404(cid)
    mgr     = ODataConnectionManager(conn)
    try:
        entities = mgr.list_entities()
        return jsonify(entities)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 502


# ── Geração de telas ──────────────────────────────────────────────────────────

@bp.route("/api/odata-connections/<int:cid>/gerar-tela", methods=["POST"])
def generate_screen(cid: int):
    """
    Gera página(s) automaticamente a partir dos metadados de uma entidade.

    Body JSON:
        {
          "entity":    "Customers",
          "mode":      "list" | "form" | "both",
          "page_name": "Lista de Clientes"   (opcional)
        }
    """
    conn    = ODataConnection.query.get_or_404(cid)
    project = Project.query.get_or_404(conn.project_id)
    data    = request.get_json(force=True) or {}

    entity    = (data.get("entity") or "").strip()
    mode      = data.get("mode", "list")
    page_name = data.get("page_name") or None

    if not entity:
        return jsonify({"error": "entity é obrigatório"}), 400
    if mode not in ("list", "form", "both"):
        return jsonify({"error": "mode deve ser 'list', 'form' ou 'both'"}), 400

    try:
        gen   = ODataScreenGenerator(conn, project)
        pages = gen.generate(entity, mode, page_name)
        return jsonify({"ok": True, "pages": pages})
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 404
    except Exception as exc:
        return jsonify({"error": f"Erro na geração: {exc}"}), 500
