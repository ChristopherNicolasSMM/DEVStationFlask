"""
controllers/page_controller.py — Páginas v3.0
Gera auto-snapshot a cada save_page.
"""
import json, datetime
from flask import Blueprint, jsonify, request
from models import db, Page, Component, Project
from versioning import create_auto_snapshot

bp = Blueprint("page", __name__)


@bp.route("/api/projetos/<int:pid>/paginas")
def list_pages(pid: int):
    Project.query.get_or_404(pid)
    pages = Page.query.filter_by(project_id=pid).order_by(Page.order).all()
    return jsonify([p.to_dict() for p in pages])


@bp.route("/api/projetos/<int:pid>/paginas", methods=["POST"])
def create_page(pid: int):
    project = Project.query.get_or_404(pid)
    data    = request.get_json(force=True) or {}
    count   = Page.query.filter_by(project_id=pid).count()
    page = Page(
        project_id=pid,
        name=data.get("name", f"Página {count + 1}"),
        title=data.get("title", ""),
        slug=data.get("slug", f"pagina-{count + 1}"),
        is_home=data.get("is_home", False),
        order=count,
    )
    db.session.add(page)
    db.session.commit()
    return jsonify(page.to_dict()), 201


@bp.route("/api/paginas/<int:pgid>")
def get_page(pgid: int):
    page = Page.query.get_or_404(pgid)
    return jsonify(page.to_dict(include_components=True))


@bp.route("/api/paginas/<int:pgid>", methods=["PUT"])
def update_page_meta(pgid: int):
    page = Page.query.get_or_404(pgid)
    data = request.get_json(force=True) or {}
    for key in ("name", "title", "slug", "is_home", "canvas_w", "canvas_h", "canvas_bg"):
        if key in data:
            setattr(page, key, data[key])
    db.session.commit()
    return jsonify(page.to_dict())


@bp.route("/api/paginas/<int:pgid>", methods=["DELETE"])
def delete_page(pgid: int):
    page = Page.query.get_or_404(pgid)
    db.session.delete(page)
    db.session.commit()
    return jsonify({"ok": True})


@bp.route("/api/paginas/<int:pgid>/salvar", methods=["POST"])
def save_page(pgid: int):
    """
    Salva todos os componentes da página e gera auto-snapshot.
    Body: { "components": [ { ...comp_data } ] }
    """
    page = Page.query.get_or_404(pgid)
    data = request.get_json(force=True) or {}

    # Recria todos os componentes
    for comp in list(page.components):
        db.session.delete(comp)
    db.session.flush()

    for c_data in (data.get("components") or []):
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
    db.session.flush()

    # Auto-snapshot a cada save
    create_auto_snapshot(page, author=data.get("author", "usuario"))
    db.session.commit()

    return jsonify({"ok": True, "page": page.to_dict(include_components=True)})


@bp.route("/api/paginas/<int:pgid>/duplicar", methods=["POST"])
def duplicate_page(pgid: int):
    src   = Page.query.get_or_404(pgid)
    count = Page.query.filter_by(project_id=src.project_id).count()
    copy  = Page(
        project_id=src.project_id,
        name=f"{src.name} (cópia)",
        title=src.title, slug=f"{src.slug}-copia-{count}",
        is_home=False, order=count,
        canvas_w=src.canvas_w, canvas_h=src.canvas_h, canvas_bg=src.canvas_bg,
    )
    db.session.add(copy)
    db.session.flush()

    for comp in src.components:
        c_copy = Component(
            page_id=copy.id, type=comp.type, name=comp.name,
            x=comp.x, y=comp.y, width=comp.width, height=comp.height,
            z_index=comp.z_index, properties=dict(comp.properties or {}),
            events=dict(comp.events or {}), rules=list(comp.rules or []),
        )
        db.session.add(c_copy)

    db.session.commit()
    return jsonify(copy.to_dict(include_components=True)), 201
