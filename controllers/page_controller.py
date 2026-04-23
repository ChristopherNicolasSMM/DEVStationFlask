"""
controllers/page_controller.py — CRUD de Páginas + Designer
=============================================================
Gerencia páginas dentro de um projeto e serve o designer.

  GET  /designer/<pid>/<pgid>           → abre o designer
  GET  /designer/<pid>                  → redireciona para home page
  POST /projetos/<pid>/paginas/nova     → cria página
  POST /paginas/<pgid>/renomear         → renomeia
  POST /paginas/<pgid>/deletar          → deleta
  GET  /api/paginas/<pgid>              → JSON da página + componentes
  POST /api/paginas/<pgid>/salvar       → salva lista de componentes
"""

import datetime
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from models import db, Project, Page, Component, Menu
from components import ComponentRegistry

bp = Blueprint("page", __name__)


# ── Designer ──────────────────────────────────────────────────────────────────

@bp.route("/designer/<int:pid>")
def designer_home(pid: int):
    """Redireciona para o designer da primeira página (home) do projeto."""
    project = Project.query.get_or_404(pid)
    home = next((p for p in project.pages if p.is_home), None) or project.pages[0]
    return redirect(url_for("page.designer", pid=pid, pgid=home.id))


@bp.route("/designer/<int:pid>/<int:pgid>")
def designer(pid: int, pgid: int):
    """
    Renderiza o Designer — a interface principal de drag & drop.
    Passa para o template:
      - project, current_page, all_pages
      - component_registry  (catálogo de tipos disponíveis)
      - menu_config         (menu principal em JSON)
    """
    project      = Project.query.get_or_404(pid)
    current_page = Page.query.get_or_404(pgid)

    # Menu principal do projeto (tipo 'main')
    main_menu = next((m for m in project.menus if m.type == "main"), None)
    menu_config = main_menu.config if main_menu else {}

    # Catálogo de componentes disponíveis (para a paleta)
    registry = ComponentRegistry.get_catalog()

    return render_template(
        "designer.html",
        project=project,
        current_page=current_page,
        all_pages=project.pages,
        registry=registry,
        menu_config=menu_config,
    )


# ── CRUD de Páginas ───────────────────────────────────────────────────────────

@bp.route("/projetos/<int:pid>/paginas/nova", methods=["POST"])
def create_page(pid: int):
    """Cria nova página dentro do projeto."""
    project = Project.query.get_or_404(pid)
    data    = request.get_json(force=True) or {}
    name    = (data.get("name") or "Nova Página").strip()

    # Próxima ordem
    next_order = max((p.order for p in project.pages), default=-1) + 1

    page = Page(
        project_id=project.id,
        name=name,
        title=name,
        slug=_slugify(name),
        is_home=False,
        order=next_order,
    )
    db.session.add(page)
    db.session.commit()
    return jsonify(page.to_dict())


@bp.route("/paginas/<int:pgid>/renomear", methods=["POST"])
def rename_page(pgid: int):
    page = Page.query.get_or_404(pgid)
    data = request.get_json(force=True) or {}
    name = (data.get("name") or "").strip()
    if name:
        page.name  = name
        page.title = data.get("title", name)
        page.slug  = _slugify(name)
    db.session.commit()
    return jsonify(page.to_dict())


@bp.route("/paginas/<int:pgid>/deletar", methods=["POST"])
def delete_page(pgid: int):
    page = Page.query.get_or_404(pgid)
    if page.is_home:
        return jsonify({"ok": False, "error": "Não é possível deletar a página inicial."}), 400
    pid = page.project_id
    db.session.delete(page)
    db.session.commit()
    return jsonify({"ok": True, "project_id": pid})


# ── API Save / Load ───────────────────────────────────────────────────────────

@bp.route("/api/paginas/<int:pgid>")
def load_page(pgid: int):
    """Retorna JSON completo da página com todos os componentes."""
    page = Page.query.get_or_404(pgid)
    return jsonify(page.to_dict(include_components=True))


@bp.route("/api/paginas/<int:pgid>/salvar", methods=["POST"])
def save_page(pgid: int):
    """
    Substitui todos os componentes da página pelo array recebido.
    Body: JSON  {components: [...], canvas_bg, canvas_w, canvas_h}

    Estratégia de upsert:
      - Componentes com id existente → atualiza
      - Componentes com id novo/ausente → cria
      - Componentes não presentes no payload → deleta
    """
    page = Page.query.get_or_404(pgid)
    data = request.get_json(force=True) or {}

    # Atualiza configurações do canvas da página
    page.canvas_bg  = data.get("canvas_bg", page.canvas_bg)
    page.canvas_w   = data.get("canvas_w",  page.canvas_w)
    page.canvas_h   = data.get("canvas_h",  page.canvas_h)
    page.updated_at = datetime.datetime.utcnow()

    incoming     = data.get("components", [])
    incoming_ids = {c["id"] for c in incoming if isinstance(c.get("id"), int)}

    # Remove componentes que não vieram no payload
    for comp in list(page.components):
        if comp.id not in incoming_ids:
            db.session.delete(comp)

    # Upsert
    existing = {c.id: c for c in page.components}
    for c_data in incoming:
        cid = c_data.get("id")
        if cid and cid in existing:
            _update_component(existing[cid], c_data)
        else:
            comp = _build_component(page.id, c_data)
            db.session.add(comp)

    db.session.commit()

    saved_at = datetime.datetime.utcnow().strftime("%H:%M:%S")
    return jsonify({"ok": True, "saved_at": saved_at})


# ── Helpers ───────────────────────────────────────────────────────────────────

def _slugify(name: str) -> str:
    """Converte nome em slug de arquivo."""
    import re
    slug = name.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_-]+", "-", slug)
    return slug or "pagina"


def _build_component(page_id: int, data: dict) -> Component:
    """Cria um novo objeto Component a partir do dicionário recebido."""
    return Component(
        page_id    = page_id,
        type       = data.get("type", "label"),
        name       = data.get("name", "comp"),
        x          = int(data.get("x", 100)),
        y          = int(data.get("y", 100)),
        width      = int(data.get("width", 150)),
        height     = int(data.get("height", 40)),
        z_index    = int(data.get("z_index", 1)),
        properties = data.get("properties", {}),
        events     = data.get("events", {}),
        rules      = data.get("rules", []),
    )


def _update_component(comp: Component, data: dict) -> None:
    """Atualiza um componente existente com dados do payload."""
    comp.type       = data.get("type",       comp.type)
    comp.name       = data.get("name",       comp.name)
    comp.x          = int(data.get("x",      comp.x))
    comp.y          = int(data.get("y",      comp.y))
    comp.width      = int(data.get("width",  comp.width))
    comp.height     = int(data.get("height", comp.height))
    comp.z_index    = int(data.get("z_index",comp.z_index))
    comp.properties = data.get("properties", comp.properties)
    comp.events     = data.get("events",     comp.events)
    comp.rules      = data.get("rules",      comp.rules)
    comp.updated_at = datetime.datetime.utcnow()
