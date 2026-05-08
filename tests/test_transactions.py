"""
tests/test_transactions.py — Testes de Navegação por Transações v3.0
"""
import pytest


class TestTransactionCatalog:
    def test_all_ds_transactions_seeded(self, client):
        r = client.get("/api/transacoes")
        assert r.status_code == 200
        codes = [t["code"] for t in r.get_json()]
        required = ["DS_HOME", "DS_DESIGNER", "DS_ODATA", "DS_VERSIONS",
                    "DS_BUILD", "DS_PLUGINS", "DS_ADDONS", "DS_MENU"]
        for code in required:
            assert code in codes, f"Transação {code} não encontrada"

    def test_search_by_code(self, client):
        r = client.get("/api/transacoes?q=DS_ODATA")
        data = r.get_json()
        assert any(t["code"] == "DS_ODATA" for t in data)

    def test_search_by_label(self, client):
        r = client.get("/api/transacoes?q=designer")
        data = r.get_json()
        assert len(data) >= 1

    def test_get_transaction_detail(self, client):
        r = client.get("/api/transacoes/DS_HOME")
        assert r.status_code == 200
        data = r.get_json()
        assert data["code"] == "DS_HOME"
        assert data["is_standard"] is True
        assert data["group"] == "Core"

    def test_unknown_transaction_404(self, client):
        r = client.get("/api/transacoes/TX_NAO_EXISTE")
        assert r.status_code == 404

    def test_transactions_have_routes(self, client):
        r    = client.get("/api/transacoes")
        txs  = r.get_json()
        for tx in txs:
            assert tx["route"], f"Transação {tx['code']} sem rota definida"

    def test_transactions_have_icons(self, client):
        r   = client.get("/api/transacoes")
        txs = r.get_json()
        for tx in txs:
            assert tx["icon"], f"Transação {tx['code']} sem ícone"

    def test_transactions_grouped(self, client):
        r      = client.get("/api/transacoes")
        txs    = r.get_json()
        groups = set(t["group"] for t in txs)
        assert "Core"        in groups
        assert "Design"      in groups
        assert "Integration" in groups
        assert "DevOps"      in groups
        assert "Platform"    in groups


class TestNavigation:
    def test_navigate_ds_versions(self, client):
        r = client.get("/transacoes/DS_VERSIONS")
        assert r.status_code == 200

    def test_navigate_ds_plugins(self, client):
        r = client.get("/transacoes/DS_PLUGINS")
        assert r.status_code == 200

    def test_navigate_ds_addons(self, client):
        r = client.get("/transacoes/DS_ADDONS")
        assert r.status_code == 200

    def test_navigate_ds_build(self, client):
        r = client.get("/transacoes/DS_BUILD")
        assert r.status_code == 200

    def test_navigate_ds_menu(self, client):
        r = client.get("/transacoes/DS_MENU")
        assert r.status_code == 200

    def test_navigate_ds_odata(self, client):
        r = client.get("/transacoes/DS_ODATA")
        assert r.status_code == 200

    def test_navigate_inactive_transaction(self, client, app):
        """Transação inativa não deve ser acessível via /transacoes/<code>."""
        from models import db, Transaction
        with app.app_context():
            tx = Transaction.query.filter_by(code="DS_AUDIT").first()
            if tx:
                tx.is_active = False
                db.session.commit()

        r = client.get("/transacoes/DS_AUDIT")
        assert r.status_code == 404

        # Restaura
        with app.app_context():
            tx = Transaction.query.filter_by(code="DS_AUDIT").first()
            if tx:
                tx.is_active = True
                db.session.commit()
