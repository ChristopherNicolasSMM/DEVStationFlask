"""
controllers/project_controller.py — CRUD de Projetos
======================================================
Responsável pelas rotas relacionadas a projetos:
  GET  /                         → dashboard (lista)
  POST /projetos/novo            → cria projeto
  POST /projetos/<id>/renomear   → renomeia
  POST /projetos/<id>/deletar    → deleta
  GET  /projetos/<id>/info       → retorna JSON do projeto
"""

import datetime
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from models import db, Project, Page, Menu

# Prefixo de URL vazio pois este controller serve a raiz
bp = Blueprint("project", __name__)


# ── Dashboard ─────────────────────────────────────────────────────────────────

@bp.route("/")
def dashboard():
    """Página principal — lista todos os projetos ordenados por atualização."""
    projects = Project.query.order_by(Project.updated_at.desc()).all()
    return render_template("dashboard.html", projects=projects)


# ── Criar ─────────────────────────────────────────────────────────────────────

@bp.route("/projetos/novo", methods=["POST"])
def create():
    """
    Cria um novo Projeto com uma Página inicial e os menus padrão.
    Body: form-data   name (str)
    """
    name = request.form.get("name", "Projeto Sem Título").strip() or "Projeto Sem Título"

    project = Project(name=name)
    db.session.add(project)
    db.session.flush()  # obtém o ID antes de commitar

    # Página inicial obrigatória
    home_page = Page(
        project_id=project.id,
        name="Início",
        title=name,
        slug="index",
        is_home=True,
        order=0,
    )
    db.session.add(home_page)

    # Menus padrão (main + sidebar)
    for menu in Menu.create_defaults(project.id):
        db.session.add(menu)

    db.session.commit()
    return jsonify(project.to_dict())


# ── Renomear ──────────────────────────────────────────────────────────────────

@bp.route("/projetos/<int:pid>/renomear", methods=["POST"])
def rename(pid: int):
    """
    Renomeia um projeto.
    Body: JSON  {name: str}
    """
    project = Project.query.get_or_404(pid)
    data = request.get_json(force=True) or {}
    new_name = (data.get("name") or "").strip()
    if new_name:
        project.name = new_name
        project.updated_at = datetime.datetime.utcnow()
        db.session.commit()
    return jsonify(project.to_dict())


# ── Deletar ───────────────────────────────────────────────────────────────────

@bp.route("/projetos/<int:pid>/deletar", methods=["POST"])
def delete(pid: int):
    """Remove permanentemente o projeto e todos os seus dados (cascade)."""
    project = Project.query.get_or_404(pid)
    db.session.delete(project)
    db.session.commit()
    return jsonify({"ok": True, "deleted_id": pid})


# ── Info ──────────────────────────────────────────────────────────────────────

@bp.route("/projetos/<int:pid>/info")
def info(pid: int):
    """Retorna dados completos do projeto em JSON."""
    project = Project.query.get_or_404(pid)
    data = project.to_dict()
    data["pages"] = [p.to_dict() for p in project.pages]
    return jsonify(data)
