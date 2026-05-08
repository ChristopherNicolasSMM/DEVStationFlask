"""
odata/screen_generator.py — Gerador de Telas OData v3.0.3
===========================================================
Correções v3.0.3:
 - grp_h baseado em LINHAS (ceil(fields/cols)) e não total de campos
 - Largura de coluna proporcional ao canvas do projeto (~metade do canvas)
 - Campos com propriedades visuais completas (label, placeholder, text)
 - fy calculado a partir do legend real do groupbox
 - z-index correto: groupbox sempre abaixo dos campos
"""

import math
import logging
from typing import Literal

log = logging.getLogger(__name__)

# ── Mapeamento de tipos ────────────────────────────────────────
_FIELD_TYPE_MAP = {
    "TEXT":     "textbox",
    "NUMBER":   "numberbox",
    "DATE":     "datepicker",
    "BOOLEAN":  "switch",
    "DROPDOWN": "combobox",
}

# ── Constantes de layout ─────────────────────────────────────
_SIDE_PAD    = 24    # margem lateral do canvas
_COL_GAP     = 20    # gap horizontal entre colunas
_COLS        = 2     # campos por linha
_FIELD_H     = 66    # altura de cada campo (label 18 + input 38 + margem 10)
_FIELD_VGAP  = 14    # gap vertical entre campos
_LEGEND_H    = 34    # altura do legend (texto do grupo)
_GRP_PAD_B   = 18    # padding interno inferior do groupbox
_GRP_GAP     = 20    # gap entre grupos
_HEADING_Y   = 20    # Y do heading
_HEADING_H   = 52
_FIRST_GRP_Y = 86    # Y do primeiro grupo (heading + gap)


def _col_width(canvas_w: int) -> int:
    """Largura de cada coluna para um canvas de `canvas_w` pixels."""
    available = canvas_w - 2 * _SIDE_PAD - (_COLS - 1) * _COL_GAP
    return max(200, available // _COLS)


def _rows(n_fields: int) -> int:
    return math.ceil(n_fields / _COLS) if n_fields else 1


def _grp_h(n_fields: int) -> int:
    """Altura total do groupbox baseada no número REAL de linhas."""
    r = _rows(n_fields)
    return _LEGEND_H + r * _FIELD_H + (r - 1) * _FIELD_VGAP + _GRP_PAD_B


class ODataScreenGenerator:
    """Gera páginas no DS_DESIGNER a partir de metadados de uma entidade OData."""

    def __init__(self, connection, project):
        self.connection = connection
        self.project    = project
        # Usa a largura do canvas do projeto para cálculos proporcionais
        self._canvas_w  = getattr(project, "canvas_w", None) or 1280

    def generate(self, entity_name: str,
                 mode: Literal["list", "form", "both"],
                 page_name: str | None = None) -> list:
        from odata.connection_manager import ODataConnectionManager
        mgr    = ODataConnectionManager(self.connection)
        entity = mgr.get_entity(entity_name)
        if not entity:
            raise ValueError(f"Entidade '{entity_name}' não encontrada na conexão.")

        base_name = page_name or entity.get("label", entity_name)
        results   = []

        if mode in ("list", "both"):
            results.append(self._gen_list(entity, base_name).to_dict())
        if mode in ("form", "both"):
            results.append(self._gen_form(entity, base_name).to_dict())

        return results

    # ── Listagem ──────────────────────────────────────────────

    def _gen_list(self, entity: dict, base_name: str):
        from models import db, Component
        from versioning.snapshot import create_auto_snapshot

        page_name = f"{base_name} — Lista"
        page      = self._create_page(page_name)
        cw        = self._canvas_w
        grid_w    = cw - 2 * _SIDE_PAD

        # ── Heading ───────────────────────────────────────────
        db.session.add(Component(
            page_id=page.id, type="heading", name="hdgLista",
            x=_SIDE_PAD, y=_HEADING_Y, width=grid_w, height=_HEADING_H, z_index=1,
            properties={
                "text":       page_name,
                "tag":        "h2",
                "font_size":  26,
                "text_color": "#012970",
                "bold":       True,
            },
        ))

        # ── Barra de ações (botão Novo) ────────────────────────
        db.session.add(Component(
            page_id=page.id, type="button", name="btnNovo",
            x=_SIDE_PAD, y=_HEADING_Y + _HEADING_H + 10,
            width=140, height=38, z_index=2,
            properties={
                "text":    "＋ Novo",
                "variant": "primary",
                "bg_color": "#4154f1",
                "text_color": "#ffffff",
            },
        ))

        # ── Busca ─────────────────────────────────────────────
        db.session.add(Component(
            page_id=page.id, type="textbox", name="txtBusca",
            x=_SIDE_PAD + 160, y=_HEADING_Y + _HEADING_H + 10,
            width=320, height=38, z_index=3,
            properties={
                "placeholder": f"Buscar {entity.get('label', entity['name'])}...",
                "label":       "",
            },
        ))

        # ── DataGrid ──────────────────────────────────────────
        ui        = entity.get("ui", {})
        list_view = ui.get("list_view", {})
        raw_cols  = list_view.get("columns", self._default_columns(entity))
        columns   = [c.get("field", c) if isinstance(c, dict) else c for c in raw_cols]
        col_labels = [c.get("label", c.get("field", c)) if isinstance(c, dict) else c
                      for c in raw_cols]
        orderby   = list_view.get("default_sort", "")

        grid_y = _HEADING_Y + _HEADING_H + 62
        db.session.add(Component(
            page_id=page.id, type="datagrid", name="gridLista",
            x=_SIDE_PAD, y=grid_y, width=grid_w, height=360, z_index=4,
            properties={
                "columns":  col_labels,
                "rows":     [["—"] * len(col_labels)] * 3,   # linhas de exemplo
                "striped":  True,
                "hover":    True,
                "sortable": True,
                "odata": {
                    "connection_id": self.connection.id,
                    "entity":        entity["name"],
                    "mode":          "list",
                    "orderby":       orderby,
                    "page_size":     20,
                    "select":        ",".join(columns),
                    "columns":       columns,
                },
            },
        ))

        # ── Paginação ─────────────────────────────────────────
        db.session.add(Component(
            page_id=page.id, type="pagination", name="pgLista",
            x=_SIDE_PAD, y=grid_y + 370, width=300, height=38, z_index=5,
            properties={"total": 50, "per_page": 20, "current": 1},
        ))

        db.session.commit()
        create_auto_snapshot(page, tags=["odata-gen", "auto-list"])
        log.info("Lista OData gerada: %s (page_id=%s)", page_name, page.id)
        return page

    # ── Formulário ────────────────────────────────────────────

    def _gen_form(self, entity: dict, base_name: str):
        from models import db, Component
        from versioning.snapshot import create_auto_snapshot

        page_name = f"{base_name} — Formulário"
        page      = self._create_page(page_name)
        cw        = self._canvas_w
        grid_w    = cw - 2 * _SIDE_PAD
        col_w     = _col_width(cw)

        # ── Heading ───────────────────────────────────────────
        db.session.add(Component(
            page_id=page.id, type="heading", name="hdgForm",
            x=_SIDE_PAD, y=_HEADING_Y, width=grid_w, height=_HEADING_H, z_index=1,
            properties={
                "text":       page_name,
                "tag":        "h2",
                "font_size":  26,
                "text_color": "#012970",
                "bold":       True,
            },
        ))

        ui     = entity.get("ui", {})
        form   = ui.get("form", {})
        # Fallback: um grupo com todos os campos se não houver definição de form
        groups = form.get("groups") or [
            {"label": entity.get("label", "Dados"), "fields": entity.get("fields", [])}
        ]

        z     = 2
        y_cur = _FIRST_GRP_Y

        for group in groups:
            group_label = group.get("label", "Grupo")
            fields      = group.get("fields", [])
            n_rows      = _rows(len(fields))
            gh          = _grp_h(len(fields))

            # ── GroupBox ──────────────────────────────────────
            db.session.add(Component(
                page_id=page.id, type="groupbox",
                name=f"grp_{group_label[:12].replace(' ','_')}",
                x=_SIDE_PAD, y=y_cur, width=grid_w, height=gh, z_index=z,
                properties={"title": group_label, "border": "#ced4da"},
            ))
            z += 1

            col_idx = 0
            row_idx = 0

            for field in fields:
                fname    = (field.get("name", field) if isinstance(field, dict) else field) or "campo"
                flabel   = (field.get("label", fname) if isinstance(field, dict) else fname)
                ftype    = (field.get("type", "TEXT") if isinstance(field, dict) else "TEXT").upper()
                required = field.get("required", False) if isinstance(field, dict) else False
                maxlen   = field.get("max_length") if isinstance(field, dict) else None
                comp_type = _FIELD_TYPE_MAP.get(ftype, "textbox")

                # Posição proporcional ao canvas
                fx = _SIDE_PAD + col_idx * (col_w + _COL_GAP)
                fy = y_cur + _LEGEND_H + row_idx * (_FIELD_H + _FIELD_VGAP)

                # Propriedades ricas para o campo
                props: dict = {
                    "label":       flabel,
                    "placeholder": f"{flabel}...",
                    "font_size":   13,
                }
                if comp_type == "switch":
                    props["text"]    = flabel
                    props["checked"] = False
                elif comp_type == "combobox":
                    props["placeholder"] = f"Selecione {flabel}..."
                elif comp_type == "datepicker":
                    props["label"] = flabel
                elif comp_type == "numberbox":
                    props["placeholder"] = "0"
                if maxlen:
                    props["maxlength"] = maxlen

                # Indica binding OData nas props
                props["odata"] = {
                    "connection_id": self.connection.id,
                    "entity":        entity["name"],
                    "mode":          "field",
                    "field_binding": fname,
                }

                rules = []
                if required:
                    rules.append({
                        "id":     "obrigatorio",
                        "params": {"message": f"{flabel} é obrigatório."},
                    })
                if maxlen:
                    rules.append({
                        "id":     "max_length",
                        "params": {"max": maxlen, "message": f"Máximo {maxlen} caracteres."},
                    })

                db.session.add(Component(
                    page_id=page.id,
                    type=comp_type,
                    name=f"fld_{fname[:16]}",
                    x=fx, y=fy,
                    width=col_w, height=_FIELD_H,
                    z_index=z,
                    properties=props,
                    rules=rules,
                ))
                z += 1

                col_idx += 1
                if col_idx >= _COLS:
                    col_idx = 0
                    row_idx += 1

            y_cur += gh + _GRP_GAP

        # ── Botões de ação ─────────────────────────────────────
        btn_y = y_cur + 8
        db.session.add(Component(
            page_id=page.id, type="button", name="btnSalvar",
            x=_SIDE_PAD, y=btn_y, width=140, height=40, z_index=z,
            properties={
                "text":       "💾 Salvar",
                "variant":    "primary",
                "bg_color":   "#4154f1",
                "text_color": "#ffffff",
            },
        ))
        db.session.add(Component(
            page_id=page.id, type="button", name="btnCancelar",
            x=_SIDE_PAD + 160, y=btn_y, width=140, height=40, z_index=z + 1,
            properties={
                "text":       "✕ Cancelar",
                "variant":    "outline-secondary",
                "bg_color":   "#ffffff",
                "text_color": "#6c757d",
            },
        ))

        db.session.commit()
        create_auto_snapshot(page, tags=["odata-gen", "auto-form"])
        log.info("Formulário OData gerado: %s (page_id=%s)", page_name, page.id)
        return page

    # ── Helpers ───────────────────────────────────────────────

    def _create_page(self, name: str):
        from models import db, Page
        import re

        base_slug = re.sub(r"[^\w]+", "-", name.lower()).strip("-") or "pagina"
        slug      = base_slug
        existing  = Page.query.filter_by(project_id=self.project.id, slug=slug).first()
        if existing:
            count = Page.query.filter_by(project_id=self.project.id).count()
            slug  = f"{base_slug}-{count + 1}"

        next_order = max((p.order for p in self.project.pages), default=-1) + 1
        page = Page(
            project_id=self.project.id,
            name=name, title=name, slug=slug,
            is_home=False, order=next_order,
        )
        db.session.add(page)
        db.session.flush()
        return page

    def _default_columns(self, entity: dict) -> list:
        fields = entity.get("fields", [])
        if not fields:
            return [{"field": "ID", "label": "ID"},
                    {"field": "Nome", "label": "Nome"}]
        return [
            {"field": f.get("name", f) if isinstance(f, dict) else f,
             "label": f.get("label", f.get("name", f)) if isinstance(f, dict) else f}
            for f in fields[:6]
        ]
