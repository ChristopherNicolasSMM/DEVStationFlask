"""
controllers/nav_controller.py — Navegação por Transações
==========================================================
Serve o DS_HOME (launchpad) que substitui o dashboard tradicional.

  GET  /                          → DS_HOME launchpad (projetos + transações + favoritos)
  GET  /transacoes/<code>         → navega para a tela da transação
  GET  /api/transacoes            → lista todas as transações (com busca)
  GET  /api/transacoes/<code>     → detalhe de uma transação
  GET  /transacoes/DS_VERSIONS    → tela de histórico de versões
  GET  /transacoes/DS_PLUGINS     → gerenciador de plugins
  GET  /transacoes/DS_ADDONS      → gerenciador de addons
  GET  /transacoes/DS_BUILD       → build pipeline
  GET  /transacoes/DS_MENU        → editor de menu visual
  GET  /transacoes/DS_ODATA       → gerenciador OData (overview)
  GET  /transacoes/DS_AUDIT       → console de auditoria (stub)
"""

from flask import (Blueprint, jsonify, redirect, render_template, request,
                   url_for)

from models import Addon, BuildLog, PageVersion, Plugin, Project, Transaction

bp = Blueprint("nav", __name__)


# ── DS_HOME — substitui o dashboard ──────────────────────────────────────────


@bp.route("/")
def home():
    """
    DS_HOME: launchpad que unifica projetos, transações e favoritos.
    Substituiu o dashboard simples da v2.2.
    """
    projects = Project.query.order_by(Project.updated_at.desc()).all()
    tab = request.args.get(
        "tab", "home"
    )  # home | projects | plugins | addons | favorites
    tx_groups = _get_tx_groups()
    plugins = Plugin.query.filter_by(is_active=True).all()
    addons = Addon.query.filter_by(is_active=True).all()

    return render_template(
        "dashboard.html",
        projects=projects,
        tx_groups=tx_groups,
        active_tab=tab,
        plugins=plugins,
        addons=addons,
        last_build=BuildLog.query.order_by(BuildLog.started_at.desc()).first(),
    )


# ── Navegação por código ──────────────────────────────────────────────────────


@bp.route("/transacoes/<string:code>")
def navigate(code: str):
    """Navega para a tela de uma transação pelo código."""
    tx = Transaction.query.filter_by(code=code, is_active=True).first()
    if not tx:
        return render_template("404_tx.html", code=code), 404

    # Mapeamento de rotas para views internas
    _HANDLERS = {
        "DS_VERSIONS": _view_versions,
        "DS_PLUGINS": _view_plugins,
        "DS_ADDONS": _view_addons,
        "DS_BUILD": _view_build,
        "DS_MENU": _view_menu_editor,
        "DS_ODATA": _view_odata_overview,
        "DS_AUDIT": _view_audit,
        "DS_USERS": _view_users,
    }

    handler = _HANDLERS.get(code)
    if handler:
        return handler()

    # Rota dinâmica com parâmetros (ex: /designer/{pid})
    if "{pid}" in tx.route:
        # Redireciona para o projeto mais recente se nenhum pid informado
        last = Project.query.order_by(Project.updated_at.desc()).first()
        if last:
            return redirect(tx.route.replace("{pid}", str(last.id)))

    return redirect(tx.route)


# ── API ───────────────────────────────────────────────────────────────────────


@bp.route("/api/transacoes")
def list_transactions():
    """Lista transações com suporte a busca por q= (código ou label)."""
    q = (request.args.get("q") or "").strip().lower()
    active = request.args.get("active", "1") == "1"

    query = Transaction.query
    if active:
        query = query.filter_by(is_active=True)
    if q:
        query = query.filter(
            db_or(
                Transaction.code.ilike(f"%{q}%"),
                Transaction.label.ilike(f"%{q}%"),
                Transaction.description.ilike(f"%{q}%"),
            )
        )

    txs = query.order_by(Transaction.group, Transaction.code).all()
    return jsonify([t.to_dict() for t in txs])


@bp.route("/api/transacoes/<string:code>")
def get_transaction(code: str):
    tx = Transaction.query.filter_by(code=code).first_or_404()
    return jsonify(tx.to_dict())


# ── Sub-views internas ────────────────────────────────────────────────────────


def _view_versions():
    from models import PageVersion, Project

    projects = Project.query.order_by(Project.name).all()
    recent = (
        PageVersion.query.filter_by(deleted=False)
        .order_by(PageVersion.created_at.desc())
        .limit(50)
        .all()
    )
    return render_template(
        "ds_versions.html", projects=projects, recent_versions=recent
    )


def _view_plugins():
    plugins_all = Plugin.query.order_by(Plugin.name).all()
    return render_template("ds_plugins.html", plugins=plugins_all)


def _view_addons():
    addons_all = Addon.query.order_by(Addon.name).all()
    return render_template("ds_addons.html", addons=addons_all)


def _view_build():
    from models import BuildLog

    logs = BuildLog.query.order_by(BuildLog.started_at.desc()).limit(20).all()
    return render_template("ds_build.html", build_logs=logs)


def _view_menu_editor():
    projects = Project.query.order_by(Project.updated_at.desc()).all()
    pid = request.args.get("pid", type=int)
    project = Project.query.get(pid) if pid else (projects[0] if projects else None)
    from models import Menu

    menu_main = (
        next((m for m in project.menus if m.type == "main"), None) if project else None
    )
    return render_template(
        "ds_menu_editor.html", project=project, projects=projects, menu=menu_main
    )


def _view_odata_overview():
    projects = Project.query.order_by(Project.updated_at.desc()).all()
    return render_template("ds_odata.html", projects=projects)


def _view_audit():
    return render_template("ds_audit_stub.html")


def _view_users():
    return render_template("ds_users_stub.html")


# ── Helpers ───────────────────────────────────────────────────────────────────


def _get_tx_groups() -> dict:
    """Agrupa transações ativas por grupo."""
    from sqlalchemy import or_ as _or

    txs = Transaction.query.filter_by(is_active=True).order_by(Transaction.code).all()
    groups = {}
    for tx in txs:
        groups.setdefault(tx.group, []).append(tx.to_dict())
    return groups


# SQLAlchemy or_ helper
from sqlalchemy import or_ as db_or  # noqa
