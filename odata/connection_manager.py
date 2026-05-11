"""
odata/connection_manager.py — Gerenciador de Conexões OData v3.0.2
===================================================================
Descoberta inteligente do $metadata seguindo a ordem de prioridade:

  1. Faz GET na URL base e extrai "@odata.context" do corpo JSON
     → ex.: "@odata.context": "http://host/odata/$metadata#Customers"
     → tenta http://host/odata/$metadata.json  (prioridade JSON)
     → tenta http://host/odata/$metadata
  2. {base}/$metadata.json
  3. {base}/%24metadata.json
  4. {base}/metadata.json
  5. Variantes XML: $metadata → %24metadata → metadata (sem .json)

Sempre valida se a resposta é JSON ou XML antes de processar.
Suporta retorno de ambos os formatos.
"""

import datetime
import json
import logging
import re
import urllib.error
import urllib.parse
import urllib.request
from typing import Optional

log = logging.getLogger(__name__)


class ODataConnectionManager:
    """Serviço de acesso a servidores OData V4 com descoberta de metadados."""

    def __init__(self, connection):
        self.conn = connection

    # ── Metadados (ponto de entrada público) ─────────────────────

    def fetch_metadata(self, force_refresh: bool = False) -> dict:
        """
        Retorna os metadados do servidor OData com cache de 5 minutos.
        Usa a cadeia de descoberta inteligente se o cache estiver expirado.
        """
        from config import Config

        if (
            not force_refresh
            and self.conn.metadata_cache
            and self.conn.metadata_cached_at
        ):
            age = (
                datetime.datetime.utcnow() - self.conn.metadata_cached_at
            ).total_seconds()
            if age < Config.ODATA_METADATA_TTL_SECONDS:
                return self.conn.metadata_cache

        data = self._discover_and_fetch_metadata()

        from models import db

        self.conn.metadata_cache = data
        self.conn.metadata_cached_at = datetime.datetime.utcnow()
        db.session.commit()

        return data

    # ── Cadeia de descoberta ──────────────────────────────────────

    def _discover_and_fetch_metadata(self) -> dict:
        """
        Executa a cadeia completa de descoberta de metadados.
        Retorna dict normalizado {"entities": [...]} ou lança RuntimeError.
        """
        base = self.conn.base_url.rstrip("/")
        tried: set = set()
        candidates = []
        errors = []

        # ── Fase 1: @odata.context da URL raiz ───────────────────
        ctx_base = self._extract_context_base(base)
        if ctx_base:
            log.info("@odata.context encontrado → base de metadata: %s", ctx_base)
            # Tenta versão .json primeiro (prioritário)
            candidates.append((ctx_base + ".json", "json"))
            candidates.append((ctx_base, "auto"))

        # ── Fase 2: Variantes JSON canônicas ─────────────────────
        for path in ("/$metadata.json", "/%24metadata.json", "/metadata.json"):
            candidates.append((base + path, "json"))

        # ── Fase 3: Variantes XML ─────────────────────────────────
        for path in ("/$metadata", "/%24metadata", "/metadata"):
            candidates.append((base + path, "xml"))

        for url, fmt_hint in candidates:
            clean = url.split("#")[0]  # Remove fragmento #Entity
            if clean in tried:
                continue
            tried.add(clean)
            log.debug("Testando metadata URL: %s [%s]", clean, fmt_hint)

            try:
                raw = self._get(clean, accept=_accept_header(fmt_hint))
                parsed = self._parse_response(raw, clean)
                log.info("Metadata obtido com sucesso: %s", clean)
                return parsed

            except urllib.error.HTTPError as e:
                errors.append(f"HTTP {e.code}: {clean}")
            except urllib.error.URLError as e:
                errors.append(f"URLError ({e.reason}): {clean}")
            except _ParseError as e:
                errors.append(f"ParseError ({e}): {clean}")
            except Exception as e:
                errors.append(f"{type(e).__name__} ({e}): {clean}")

        # Nada funcionou
        raise RuntimeError(
            "Não foi possível encontrar o $metadata do servidor OData.\n"
            "URLs tentadas:\n" + "\n".join(f"  • {e}" for e in errors) + "\n\n"
            "Verifique se o servidor expõe /$metadata.json (JSON) ou /$metadata (XML)."
        )

    def _extract_context_base(self, base_url: str) -> Optional[str]:
        """
        Faz GET na URL base e busca '@odata.context' no JSON retornado.
        Retorna a URL do $metadata sem o fragmento #Entity.

        Exemplo:
          "@odata.context": "http://localhost:8000/odata/$metadata#Customers"
          retorna:           "http://localhost:8000/odata/$metadata"
        """
        try:
            raw = self._get(base_url, accept="application/json")
            body = json.loads(raw)
            ctx = body.get("@odata.context") or body.get("odata.context") or ""
            if not ctx:
                return None
            # Remove fragmento #Entity
            return ctx.split("#")[0]
        except Exception as exc:
            log.debug("_extract_context_base falhou (%s): %s", base_url, exc)
            return None

    # ── Parser de resposta ────────────────────────────────────────

    def _parse_response(self, raw: str, url: str) -> dict:
        """
        Detecta automaticamente se a resposta é JSON ou XML
        e normaliza para o formato interno {"entities": [...]}.
        """
        text = (raw if isinstance(raw, str) else raw.decode("utf-8")).strip()
        if not text:
            raise _ParseError("Resposta vazia")

        # ── XML ───────────────────────────────────────────────────
        if text.startswith("<") or "<?xml" in text[:200]:
            return self._parse_xml(text, url)

        # ── JSON ──────────────────────────────────────────────────
        try:
            data = json.loads(text)
            return self._normalize_json(data, url)
        except json.JSONDecodeError as exc:
            raise _ParseError(f"Nem JSON nem XML reconhecido: {exc}") from exc

    def _normalize_json(self, data: dict, url: str) -> dict:
        """
        Converte vários formatos de JSON metadata para o formato interno.
        Suporta:
          - Formato S2MOdataPy: {"entities": [...]}
          - EDMX JSON (EntityType, Property)
          - Lista direta de entidades
        """
        if isinstance(data, dict) and "entities" in data:
            data["_source_format"] = "json"
            return data

        entities = []

        # EDMX JSON com EntityType
        if isinstance(data, dict) and (
            "EntityType" in data or "EntityContainer" in data
        ):
            ets = data.get("EntityType", [])
            if isinstance(ets, dict):
                ets = [ets]
            for et in ets:
                name = et.get("Name") or et.get("name", "Unknown")
                props = et.get("Property") or et.get("properties", [])
                if isinstance(props, dict):
                    props = [props]
                fields = [_edm_prop_to_field(p) for p in props]
                entities.append(
                    {"name": name, "label": name, "fields": fields, "ui": {}}
                )
            return {"entities": entities, "_source_format": "json"}

        # Lista direta
        if isinstance(data, list):
            return {"entities": data, "_source_format": "json"}

        log.warning("Formato JSON de metadata não reconhecido em %s", url)
        return {"entities": [], "_source_format": "json"}

    def _parse_xml(self, xml_text: str, url: str) -> dict:
        """
        Faz parse de EDMX XML → formato interno.
        Extrai EntityType e suas propriedades considerando namespaces.
        """
        try:
            import xml.etree.ElementTree as ET

            root = ET.fromstring(xml_text)
        except Exception as exc:
            raise _ParseError(f"XML inválido: {exc}") from exc

        entities = []
        # Busca EntityType em todos os níveis e com qualquer namespace
        for el in root.iter():
            local = el.tag.split("}")[-1]  # remove namespace
            if local != "EntityType":
                continue
            name = el.get("Name", "Unknown")
            fields = []
            for child in el:
                child_local = child.tag.split("}")[-1]
                if child_local == "Property":
                    fields.append(_edm_prop_to_field(child.attrib))
            entities.append({"name": name, "label": name, "fields": fields, "ui": {}})

        if not entities:
            log.warning("XML EDMX sem EntityType em %s", url)

        return {"entities": entities, "_source_format": "xml"}

    # ── Dados ─────────────────────────────────────────────────────

    def list_entities(self) -> list[dict]:
        meta = self.fetch_metadata()
        return [
            {
                "name": e.get("name", ""),
                "label": e.get("label", e.get("name", "")),
                "description": e.get("description", ""),
                "fields": e.get("fields", []),
                "ui": e.get("ui", {}),
            }
            for e in meta.get("entities", [])
        ]

    def get_entity(self, entity_name: str) -> Optional[dict]:
        for ent in self.list_entities():
            if ent["name"] == entity_name:
                return ent
        return None

    def query(self, entity: str, params: dict = None) -> dict:
        """GET na coleção com parâmetros OData ($filter, $orderby, etc.)."""
        qs = ""
        if params:
            parts = [
                f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items() if v
            ]
            if parts:
                qs = "?" + "&".join(parts)
        raw = self._get(self._build_url(f"{entity}{qs}"))
        return json.loads(raw) if isinstance(raw, (str, bytes)) else raw

    def patch(self, entity: str, key: str, data: dict) -> dict:
        """PATCH num registro individual."""
        url = self._build_url(f"{entity}({key})")
        raw = self._request("PATCH", url, data)
        return json.loads(raw) if isinstance(raw, (str, bytes)) else {}

    # ── Teste de conexão ─────────────────────────────────────────

    def test_connection(self) -> dict:
        """
        Testa a conexão e retorna detalhes do formato encontrado.
        """
        try:
            meta = self.fetch_metadata(force_refresh=True)
            n = len(meta.get("entities", []))
            fmt = meta.get("_source_format", "json")
            return {
                "ok": True,
                "entities_count": n,
                "source_format": fmt,
                "message": f"{n} entidade(s) encontrada(s) (formato: {fmt})",
            }
        except RuntimeError as exc:
            return {"ok": False, "error": str(exc)}
        except Exception as exc:
            log.warning("test_connection falhou: %s", exc)
            return {"ok": False, "error": str(exc)}

    # ── HTTP helpers ──────────────────────────────────────────────

    def _build_url(self, path: str) -> str:
        return self.conn.base_url.rstrip("/") + "/" + path

    def _auth_headers(self) -> dict:
        h = {}
        if self.conn.auth_type == "bearer" and self.conn.auth_value:
            h["Authorization"] = f"Bearer {self.conn.auth_value}"
        elif self.conn.auth_type == "basic" and self.conn.auth_value:
            import base64

            creds = base64.b64encode(self.conn.auth_value.encode()).decode()
            h["Authorization"] = f"Basic {creds}"
        return h

    def _get(self, url: str, accept: str = "application/json") -> str:
        headers = {"Accept": accept, **self._auth_headers()}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read().decode("utf-8")

    def _request(self, method: str, url: str, body: dict) -> str:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            **self._auth_headers(),
        }
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read().decode("utf-8")


# ── Helpers de módulo ─────────────────────────────────────────


def _accept_header(fmt_hint: str) -> str:
    if fmt_hint == "xml":
        return "application/xml,application/atom+xml;q=0.9,*/*;q=0.8"
    if fmt_hint == "json":
        return "application/json"
    return "application/json,application/xml;q=0.8,*/*;q=0.5"


def _edm_prop_to_field(prop: dict) -> dict:
    """Converte atributos de <Property> EDMX para campo interno DSB."""
    name = prop.get("Name") or prop.get("name", "")
    raw_type = prop.get("Type") or prop.get("type", "Edm.String")
    nullable = str(prop.get("Nullable", "true")).lower()
    maxlen = prop.get("MaxLength")

    EDM_MAP = {
        "Edm.String": "TEXT",
        "Edm.Int16": "NUMBER",
        "Edm.Int32": "NUMBER",
        "Edm.Int64": "NUMBER",
        "Edm.Decimal": "NUMBER",
        "Edm.Double": "NUMBER",
        "Edm.Single": "NUMBER",
        "Edm.Boolean": "BOOLEAN",
        "Edm.Date": "DATE",
        "Edm.DateTime": "DATE",
        "Edm.DateTimeOffset": "DATE",
        "Edm.Guid": "TEXT",
        "Edm.Binary": "TEXT",
    }
    dsb_type = EDM_MAP.get(raw_type, "TEXT")

    return {
        "name": name,
        "label": name,
        "type": dsb_type,
        "required": nullable == "false",
        "max_length": int(maxlen) if maxlen and str(maxlen).isdigit() else None,
    }


class _ParseError(Exception):
    """Erro interno de parse de metadata."""
