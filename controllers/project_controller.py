"""
controllers/project_controller.py — Projetos v3.0
(carry-over de v2.2 com save_page gerando auto-snapshot)
"""
from flask import Blueprint, jsonify, request, render_template, redirect, url_for
from models import db, Project, Page, Menu, Component
from versioning import create_auto_snapshot

bp = Blueprint("project", __name__)


@bp.route("/projetos")
def list_projects():
    projects = Project.query.order_by(Project.updated_at.desc()).all()
    return jsonify([p.to_dict() for p in projects])


@bp.route("/api/projetos", methods=["POST"])
def create_project():
    data = request.get_json(force=True) or {}
    project = Project(
        name=data.get("name", "Novo Projeto"),
        description=data.get("description", ""),
        canvas_w=int(data.get("canvas_w", 1280)),
        canvas_h=int(data.get("canvas_h", 900)),
        canvas_bg=data.get("canvas_bg", "#ffffff"),
    )
    db.session.add(project)
    db.session.flush()

    # Página inicial padrão
    home = Page(project_id=project.id, name="Página Inicial",
                title="Página Inicial", slug="index", is_home=True, order=0)
    db.session.add(home)

    # Menus padrão
    for menu in Menu.create_defaults(project.id):
        db.session.add(menu)

    db.session.commit()
    return jsonify(project.to_dict()), 201


@bp.route("/api/projetos/<int:pid>", methods=["PUT"])
def update_project(pid: int):
    project = Project.query.get_or_404(pid)
    data = request.get_json(force=True) or {}
    for key in ("name", "description", "canvas_w", "canvas_h", "canvas_bg"):
        if key in data:
            setattr(project, key, data[key])
    db.session.commit()
    return jsonify(project.to_dict())


@bp.route("/api/projetos/<int:pid>", methods=["DELETE"])
def delete_project(pid: int):
    project = Project.query.get_or_404(pid)
    db.session.delete(project)
    db.session.commit()
    return jsonify({"ok": True})


@bp.route("/designer/<int:pid>")
def open_designer(pid: int):
    project = Project.query.get_or_404(pid)
    pages   = Page.query.filter_by(project_id=pid).order_by(Page.order).all()
    page    = next((p for p in pages if p.is_home), pages[0] if pages else None)
    return render_template("designer.html", project=project, pages=pages,
                           current_page=page, components=page.components if page else [])


@bp.route("/designer/<int:pid>/<int:pgid>")
def open_designer_page(pid: int, pgid: int):
    project = Project.query.get_or_404(pid)
    pages   = Page.query.filter_by(project_id=pid).order_by(Page.order).all()
    page    = Page.query.get_or_404(pgid)
    return render_template("designer.html", project=project, pages=pages,
                           current_page=page, components=page.components if page else [])
