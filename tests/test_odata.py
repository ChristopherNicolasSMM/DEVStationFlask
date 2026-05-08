"""
tests/test_odata.py — Testes da integração OData v3.0
Mock completo do servidor OData — não precisa de servidor real.
"""
import json
import pytest
from unittest.mock import patch, MagicMock

_MOCK_METADATA = {
    "entities": [
        {
            "name":  "Customers",
            "label": "Clientes",
            "fields": [
                {"name": "CustomerID",   "label": "ID",     "type": "TEXT",   "required": True},
                {"name": "CompanyName",  "label": "Empresa","type": "TEXT",   "required": True, "max_length": 100},
                {"name": "Country",      "label": "País",   "type": "TEXT"},
                {"name": "IsActive",     "label": "Ativo",  "type": "BOOLEAN"},
            ],
            "ui": {
                "list_view": {
                    "columns":      [{"field": "CustomerID","label":"ID"},
                                     {"field": "CompanyName","label":"Empresa"},
                                     {"field": "Country","label":"País"}],
                    "default_sort": "CompanyName asc",
                },
                "form": {
                    "groups": [
                        {
                            "label":  "Identificação",
                            "fields": [
                                {"name":"CustomerID","label":"ID","type":"TEXT","required":True},
                                {"name":"CompanyName","label":"Empresa","type":"TEXT","required":True,"max_length":100},
                            ]
                        },
                        {
                            "label":  "Detalhes",
                            "fields": [
                                {"name":"Country","label":"País","type":"TEXT"},
                                {"name":"IsActive","label":"Ativo","type":"BOOLEAN"},
                            ]
                        },
                    ]
                }
            }
        }
    ]
}


class TestODataConnections:
    def test_list_connections_empty(self, client, project_id):
        r = client.get(f"/api/projetos/{project_id}/odata-connections")
        assert r.status_code == 200
        assert r.get_json() == []

    def test_create_connection(self, client, project_id):
        r = client.post(f"/api/projetos/{project_id}/odata-connections", json={
            "name": "Servidor Clientes",
            "base_url": "http://localhost:8000/odata/",
        })
        assert r.status_code == 201
        data = r.get_json()
        assert data["name"] == "Servidor Clientes"
        assert data["auth_type"] == "none"

    def test_create_connection_missing_fields(self, client, project_id):
        r = client.post(f"/api/projetos/{project_id}/odata-connections", json={})
        assert r.status_code == 400

    def test_delete_connection(self, client, project_id):
        r = client.post(f"/api/projetos/{project_id}/odata-connections", json={
            "name": "Del Conn", "base_url": "http://del.test/"
        })
        cid = r.get_json()["id"]
        r2  = client.delete(f"/api/odata-connections/{cid}")
        assert r2.status_code == 200


class TestODataTest:
    @patch("odata.connection_manager.ODataConnectionManager.test_connection")
    def test_connection_success(self, mock_test, client, project_id):
        mock_test.return_value = {"ok": True, "entities_count": 1, "message": "1 entidade(s)"}
        r = client.post(f"/api/projetos/{project_id}/odata-connections", json={
            "name": "Test OK", "base_url": "http://test/"
        })
        cid = r.get_json()["id"]
        r2  = client.post(f"/api/odata-connections/{cid}/testar")
        assert r2.status_code == 200
        assert r2.get_json()["ok"] is True

    @patch("odata.connection_manager.ODataConnectionManager.test_connection")
    def test_connection_failure(self, mock_test, client, project_id):
        mock_test.return_value = {"ok": False, "error": "Connection refused"}
        r = client.post(f"/api/projetos/{project_id}/odata-connections", json={
            "name": "Test Fail", "base_url": "http://fail/"
        })
        cid = r.get_json()["id"]
        r2  = client.post(f"/api/odata-connections/{cid}/testar")
        assert r2.status_code == 200
        assert r2.get_json()["ok"] is False


class TestODataScreenGenerator:
    def _get_or_create_conn(self, client, project_id) -> int:
        r = client.post(f"/api/projetos/{project_id}/odata-connections", json={
            "name": "Mock Server", "base_url": "http://mock/"
        })
        return r.get_json()["id"]

    @patch("odata.connection_manager.ODataConnectionManager.get_entity")
    def test_generate_list(self, mock_entity, client, project_id):
        mock_entity.return_value = _MOCK_METADATA["entities"][0]
        cid = self._get_or_create_conn(client, project_id)
        r   = client.post(f"/api/odata-connections/{cid}/gerar-tela", json={
            "entity": "Customers", "mode": "list", "page_name": "Lista de Clientes"
        })
        assert r.status_code == 200
        data = r.get_json()
        assert data["ok"] is True
        assert len(data["pages"]) == 1
        page = data["pages"][0]
        assert "Lista" in page["name"] or "Clientes" in page["name"]

    @patch("odata.connection_manager.ODataConnectionManager.get_entity")
    def test_generate_form(self, mock_entity, client, project_id):
        mock_entity.return_value = _MOCK_METADATA["entities"][0]
        cid = self._get_or_create_conn(client, project_id)
        r   = client.post(f"/api/odata-connections/{cid}/gerar-tela", json={
            "entity": "Customers", "mode": "form"
        })
        assert r.status_code == 200
        assert r.get_json()["ok"] is True

    @patch("odata.connection_manager.ODataConnectionManager.get_entity")
    def test_generate_both(self, mock_entity, client, project_id):
        mock_entity.return_value = _MOCK_METADATA["entities"][0]
        cid = self._get_or_create_conn(client, project_id)
        r   = client.post(f"/api/odata-connections/{cid}/gerar-tela", json={
            "entity": "Customers", "mode": "both"
        })
        data = r.get_json()
        assert data["ok"] is True
        assert len(data["pages"]) == 2

    @patch("odata.connection_manager.ODataConnectionManager.get_entity")
    def test_invalid_mode(self, mock_entity, client, project_id):
        mock_entity.return_value = _MOCK_METADATA["entities"][0]
        cid = self._get_or_create_conn(client, project_id)
        r   = client.post(f"/api/odata-connections/{cid}/gerar-tela", json={
            "entity": "Customers", "mode": "invalid"
        })
        assert r.status_code == 400

    @patch("odata.connection_manager.ODataConnectionManager.get_entity")
    def test_html_export_contains_odata_runtime(self, mock_entity, client, project_id):
        """Verifica que o HTML exportado contém DSB.odata quando binding OData está configurado."""
        mock_entity.return_value = _MOCK_METADATA["entities"][0]
        cid = self._get_or_create_conn(client, project_id)
        # Gera página de listagem
        r_gen = client.post(f"/api/odata-connections/{cid}/gerar-tela", json={
            "entity": "Customers", "mode": "list"
        })
        page_id = r_gen.get_json()["pages"][0]["id"]
        # Exporta HTML
        r_html = client.get(f"/api/paginas/{page_id}/exportar-html")
        assert r_html.status_code == 200
        assert b"DSB.odata" in r_html.data
        assert b"DSB.odata.bind" in r_html.data
