"""
tests/test_smoke.py — Smoke tests de todas as rotas principais v3.0
"""
import pytest


class TestProjectRoutes:
    def test_home_loads(self, client):
        r = client.get("/")
        assert r.status_code == 200

    def test_list_projects(self, client):
        r = client.get("/projetos")
        assert r.status_code == 200

    def test_create_project(self, client):
        r = client.post("/api/projetos", json={"name": "Projeto Smoke"})
        assert r.status_code == 201
        data = r.get_json()
        assert data["name"] == "Projeto Smoke"

    def test_update_project(self, client, project_id):
        r = client.put(f"/api/projetos/{project_id}", json={"name": "Projeto Renomeado"})
        assert r.status_code == 200

    def test_designer_loads(self, client, project_id):
        r = client.get(f"/designer/{project_id}")
        assert r.status_code == 200

    def test_delete_project_not_found(self, client):
        r = client.delete("/api/projetos/99999")
        assert r.status_code == 404


class TestPageRoutes:
    def test_list_pages(self, client, project_id):
        r = client.get(f"/api/projetos/{project_id}/paginas")
        assert r.status_code == 200

    def test_create_page(self, client, project_id):
        r = client.post(f"/api/projetos/{project_id}/paginas", json={"name": "Nova Página"})
        assert r.status_code == 201

    def test_get_page(self, client, page_id):
        r = client.get(f"/api/paginas/{page_id}")
        assert r.status_code == 200
        data = r.get_json()
        assert "components" in data

    def test_save_page(self, client, page_id):
        r = client.post(f"/api/paginas/{page_id}/salvar", json={
            "components": [
                {"type": "button", "name": "btnSave",
                 "x": 10, "y": 10, "width": 100, "height": 40,
                 "properties": {"text": "Salvar"}, "events": {}, "rules": []}
            ]
        })
        assert r.status_code == 200
        assert r.get_json()["ok"] is True

    def test_duplicate_page(self, client, page_id):
        r = client.post(f"/api/paginas/{page_id}/duplicar")
        assert r.status_code == 201

    def test_export_html(self, client, page_id):
        r = client.get(f"/api/paginas/{page_id}/exportar-html")
        assert r.status_code == 200
        assert b"<html" in r.data


class TestComponentRoutes:
    def test_add_component(self, client, page_id):
        r = client.post(f"/api/paginas/{page_id}/componentes", json={
            "type": "textbox", "name": "txbNome",
            "x": 50, "y": 50, "width": 200, "height": 40,
        })
        assert r.status_code == 201
        return r.get_json()["id"]

    def test_update_component(self, client, page_id):
        r = client.post(f"/api/paginas/{page_id}/componentes", json={
            "type": "label", "name": "lblTeste",
            "x": 10, "y": 10, "width": 100, "height": 30,
        })
        cid = r.get_json()["id"]
        r2  = client.put(f"/api/componentes/{cid}", json={"x": 200, "y": 200})
        assert r2.status_code == 200

    def test_delete_component(self, client, page_id):
        r = client.post(f"/api/paginas/{page_id}/componentes", json={
            "type": "label", "name": "lblDel", "x": 5, "y": 5, "width": 80, "height": 30,
        })
        cid = r.get_json()["id"]
        r2  = client.delete(f"/api/componentes/{cid}")
        assert r2.status_code == 200


class TestMenuRoutes:
    def test_list_menus(self, client, project_id):
        r = client.get(f"/api/projetos/{project_id}/menus")
        assert r.status_code == 200
        data = r.get_json()
        assert len(data) >= 1


class TestNavRoutes:
    def test_list_transactions(self, client):
        r = client.get("/api/transacoes")
        assert r.status_code == 200
        data = r.get_json()
        assert any(t["code"] == "DS_HOME" for t in data)

    def test_search_transactions(self, client):
        r = client.get("/api/transacoes?q=designer")
        assert r.status_code == 200
        data = r.get_json()
        assert any("DESIGNER" in t["code"] for t in data)

    def test_get_transaction_detail(self, client):
        r = client.get("/api/transacoes/DS_HOME")
        assert r.status_code == 200

    def test_navigate_ds_home(self, client):
        r = client.get("/transacoes/DS_HOME")
        # Should redirect to /
        assert r.status_code in (200, 302)

    def test_navigate_invalid_code(self, client):
        r = client.get("/transacoes/TX_INEXISTENTE")
        assert r.status_code == 404
