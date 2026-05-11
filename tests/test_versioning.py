"""
tests/test_versioning.py — Testes de Versionamento v3.0
"""

import os
import zipfile

import pytest


class TestVersionCreate:
    def test_save_page_creates_auto_snapshot(self, client, page_id):
        r = client.post(
            f"/api/paginas/{page_id}/salvar",
            json={
                "components": [
                    {
                        "type": "label",
                        "name": "lbl1",
                        "x": 0,
                        "y": 0,
                        "width": 100,
                        "height": 30,
                        "properties": {},
                        "events": {},
                        "rules": [],
                    }
                ]
            },
        )
        assert r.status_code == 200

        # Deve ter ao menos 1 versão auto
        r2 = client.get(f"/api/paginas/{page_id}/versoes")
        versions = r2.get_json()
        auto = [v for v in versions if v["is_auto"]]
        assert len(auto) >= 1

    def test_create_named_version(self, client, page_id):
        r = client.post(
            f"/api/paginas/{page_id}/versoes",
            json={
                "label": "sprint-1",
                "description": "Versão de entrega do Sprint 1",
                "tags": ["sprint-1", "stable"],
            },
        )
        assert r.status_code == 201
        data = r.get_json()
        assert data["version_label"] == "sprint-1"
        assert data["is_auto"] is False
        assert "sprint-1" in data["tags"]

    def test_create_version_missing_label(self, client, page_id):
        r = client.post(f"/api/paginas/{page_id}/versoes", json={})
        assert r.status_code == 400

    def test_list_versions(self, client, page_id):
        r = client.get(f"/api/paginas/{page_id}/versoes")
        assert r.status_code == 200
        assert isinstance(r.get_json(), list)

    def test_get_version_detail(self, client, page_id):
        # Cria versão para buscar
        r = client.post(f"/api/paginas/{page_id}/versoes", json={"label": "v-detail"})
        vid = r.get_json()["id"]

        r2 = client.get(f"/api/versoes/{vid}")
        assert r2.status_code == 200
        assert r2.get_json()["version_label"] == "v-detail"

    def test_get_version_with_snapshot(self, client, page_id):
        r = client.post(f"/api/paginas/{page_id}/versoes", json={"label": "v-snap"})
        vid = r.get_json()["id"]
        r2 = client.get(f"/api/versoes/{vid}?snapshot=1")
        data = r2.get_json()
        assert "snapshot" in data


class TestVersionRestore:
    def test_restore_creates_pre_snapshot(self, client, page_id):
        # Cria versão estável
        r = client.post(f"/api/paginas/{page_id}/versoes", json={"label": "stable"})
        vid = r.get_json()["id"]

        # Restaura
        r2 = client.post(
            f"/api/versoes/{vid}/restaurar", json={"triggered_by": "tester"}
        )
        assert r2.status_code == 200
        data = r2.get_json()
        assert data["ok"] is True
        assert "pre_restore_version_id" in data

        # Pre-snapshot deve existir
        pre_vid = data["pre_restore_version_id"]
        r3 = client.get(f"/api/versoes/{pre_vid}")
        assert r3.status_code == 200
        pre = r3.get_json()
        assert "pre_restore" in pre["version_label"]


class TestVersionDelete:
    def test_delete_creates_dsk_backup(self, client, page_id, app, tmp_path):
        """Deletar versão deve criar backup .dsk antes."""
        import versioning.snapshot as snap_mod

        # Direciona backups para tmp_path do pytest
        backup_dir = str(tmp_path / "backups")
        original = snap_mod.delete_version_with_backup

        def _patched(vid, triggered_by="usuario", bd=None):
            return original(vid, triggered_by=triggered_by, backup_dir=backup_dir)

        snap_mod.delete_version_with_backup = _patched

        r = client.post(f"/api/paginas/{page_id}/versoes", json={"label": "to-delete"})
        vid = r.get_json()["id"]

        r2 = client.delete(f"/api/versoes/{vid}", json={"triggered_by": "tester"})
        snap_mod.delete_version_with_backup = original  # restaura

        assert r2.status_code == 200
        data = r2.get_json()
        assert data["ok"] is True
        assert "backup_name" in data
        assert data["backup_name"].endswith(".dsk")

        # Versão deve estar marcada como deleted
        r3 = client.get(f"/api/versoes/{vid}")
        v = r3.get_json()
        assert v["deleted"] is True
        assert v["backup_path"] is not None

    def test_delete_already_deleted_version(self, client, page_id, tmp_path):
        import versioning.snapshot as snap_mod

        backup_dir = str(tmp_path / "backups2")
        original = snap_mod.delete_version_with_backup

        def _patched(vid, triggered_by="usuario", bd=None):
            return original(vid, triggered_by=triggered_by, backup_dir=backup_dir)

        snap_mod.delete_version_with_backup = _patched

        r = client.post(f"/api/paginas/{page_id}/versoes", json={"label": "del-twice"})
        vid = r.get_json()["id"]

        client.delete(f"/api/versoes/{vid}", json={"triggered_by": "tester"})
        r2 = client.delete(f"/api/versoes/{vid}", json={"triggered_by": "tester"})
        snap_mod.delete_version_with_backup = original
        assert r2.status_code == 400


class TestVersionDiff:
    def test_diff_two_versions(self, client, page_id):
        # Salva página com comp A
        client.post(
            f"/api/paginas/{page_id}/salvar",
            json={
                "components": [
                    {
                        "type": "label",
                        "name": "compA",
                        "x": 10,
                        "y": 10,
                        "width": 100,
                        "height": 30,
                        "properties": {},
                        "events": {},
                        "rules": [],
                    }
                ]
            },
        )
        r1 = client.post(f"/api/paginas/{page_id}/versoes", json={"label": "diff-v1"})
        v1_id = r1.get_json()["id"]

        # Salva com comp B
        client.post(
            f"/api/paginas/{page_id}/salvar",
            json={
                "components": [
                    {
                        "type": "button",
                        "name": "compB",
                        "x": 20,
                        "y": 20,
                        "width": 100,
                        "height": 40,
                        "properties": {},
                        "events": {},
                        "rules": [],
                    }
                ]
            },
        )
        r2 = client.post(f"/api/paginas/{page_id}/versoes", json={"label": "diff-v2"})
        v2_id = r2.get_json()["id"]

        r_diff = client.get(f"/api/versoes/diff?a={v1_id}&b={v2_id}")
        assert r_diff.status_code == 200
        diff = r_diff.get_json()
        assert "added" in diff
        assert "removed" in diff
        assert "total_changes" in diff


class TestPurgeSuggestions:
    def test_purge_suggestions_listed(self, client, page_id):
        # Faz muitos saves para acumular auto-snapshots
        for i in range(12):
            client.post(
                f"/api/paginas/{page_id}/salvar",
                json={
                    "components": [
                        {
                            "type": "label",
                            "name": f"comp_{i}",
                            "x": i * 10,
                            "y": 0,
                            "width": 100,
                            "height": 30,
                            "properties": {},
                            "events": {},
                            "rules": [],
                        }
                    ]
                },
            )

        r = client.get(f"/api/paginas/{page_id}/versoes/sugestoes-purga")
        assert r.status_code == 200
        suggestions = r.get_json()
        # Deve haver pelo menos algumas sugestões
        assert isinstance(suggestions, list)
