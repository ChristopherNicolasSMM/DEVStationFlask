"""
tests/conftest.py — Fixtures globais para pytest
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

from app import create_app
from models import ODataConnection, Page, Project
from models import db as _db


@pytest.fixture(scope="session")
def app():
    """Cria a aplicação em modo de teste com banco em memória."""
    application = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SECRET_KEY": "test-secret",
            "BUILD_DIST_DIR": "/tmp/dsb_test_dist",
            "ADDONS_DIR": "/tmp/dsb_test_addons",
            "PLUGINS_DIR": "/tmp/dsb_test_plugins",
            "EXPORT_TEMP_DIR": "/tmp/dsb_test_exports",
        }
    )
    with application.app_context():
        _db.create_all()
        _seed_test_data()
        yield application


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def project_id(app):
    with app.app_context():
        p = Project.query.first()
        return p.id


@pytest.fixture()
def page_id(app):
    with app.app_context():
        pg = Page.query.first()
        return pg.id


@pytest.fixture()
def odata_conn_id(app, project_id):
    with app.app_context():
        conn = ODataConnection.query.filter_by(project_id=project_id).first()
        return conn.id if conn else None


# ── Seed de dados de teste ─────────────────────────────────────────────────


def _seed_test_data():
    from models import Component, Menu, Page, Project, Transaction, db
    from transactions.catalog import DS_TRANSACTIONS

    project = Project(
        name="Projeto Teste", description="Projeto para testes automatizados"
    )
    _db.session.add(project)
    _db.session.flush()

    page = Page(
        project_id=project.id, name="Página Teste", slug="index", is_home=True, order=0
    )
    _db.session.add(page)
    _db.session.flush()

    comp = Component(
        page_id=page.id,
        type="button",
        name="btnTeste",
        x=100,
        y=100,
        width=120,
        height=40,
        z_index=1,
        properties={"text": "Teste"},
        events={},
        rules=[],
    )
    _db.session.add(comp)

    for menu in Menu.create_defaults(project.id):
        _db.session.add(menu)

    for tx_data in DS_TRANSACTIONS:
        if not Transaction.query.filter_by(code=tx_data["code"]).first():
            _db.session.add(Transaction(**tx_data))

    _db.session.commit()
