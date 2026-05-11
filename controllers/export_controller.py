"""
controllers/export_controller.py — Exportação HTML v3.0.3
Rota /preview: abre inline no browser com styling do sistema.
Rota /exportar-html: download do arquivo HTML gerado.
"""

import datetime
import io
import json
import os
import zipfile

from flask import Blueprint, jsonify, render_template, request, send_file

from models import ODataConnection, Page, Project

bp = Blueprint("export", __name__)


# ── Preview inline (nova aba, com estilo do sistema) ─────────────────────────


@bp.route("/designer/<int:pid>/preview/<int:pgid>")
def preview_page(pid: int, pgid: int):
    """
    Preview inline da página no browser.
    Abre em nova aba usando o template preview.html do sistema.
    """
    project = Project.query.get_or_404(pid)
    page = Page.query.get_or_404(pgid)
    components = sorted(page.components, key=lambda c: c.z_index)

    canvas_w = page.canvas_w or project.canvas_w or 1280
    canvas_h = page.canvas_h or project.canvas_h or 900
    canvas_bg = page.canvas_bg or project.canvas_bg or "#ffffff"

    # Verifica se algum componente tem binding OData
    has_odata = any(c.properties.get("odata") for c in components)
    odata_init_js = _build_odata_init_js(components) if has_odata else ""

    return render_template(
        "preview.html",
        project=project,
        page=page,
        components=components,
        canvas_w=canvas_w,
        canvas_h=canvas_h,
        canvas_bg=canvas_bg,
        has_odata=has_odata,
        odata_init_js=odata_init_js,
    )


# ── Download HTML ─────────────────────────────────────────────────────────────


@bp.route("/api/paginas/<int:pgid>/exportar-html")
def export_html(pgid: int):
    page = Page.query.get_or_404(pgid)
    project = page.project
    html = _generate_standalone_html(page, project)
    buf = io.BytesIO(html.encode("utf-8"))
    return send_file(
        buf,
        as_attachment=True,
        download_name=f"{page.slug or 'pagina'}.html",
        mimetype="text/html",
    )


# ── Export ZIP ────────────────────────────────────────────────────────────────


@bp.route("/api/projetos/<int:pid>/exportar-zip")
def export_zip(pid: int):
    project = Project.query.get_or_404(pid)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for page in project.pages:
            html = _generate_standalone_html(page, project)
            zf.writestr(f"{page.slug or 'pagina'}.html", html)
    buf.seek(0)
    ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    name = f"{project.name.replace(' ','_')}_{ts}.zip"
    return send_file(
        buf, as_attachment=True, download_name=name, mimetype="application/zip"
    )


# ── Geração HTML standalone ───────────────────────────────────────────────────


def _generate_standalone_html(page, project) -> str:
    """Gera HTML standalone com Bootstrap embutido."""
    components = sorted(page.components, key=lambda c: c.z_index)
    canvas_w = page.canvas_w or project.canvas_w or 1280
    canvas_h = page.canvas_h or project.canvas_h or 900
    canvas_bg = page.canvas_bg or project.canvas_bg or "#ffffff"
    has_odata = any(c.properties.get("odata") for c in components)
    odata_init = _build_odata_init_js(components) if has_odata else ""
    comps_html = "\n".join(_render_component_html(c) for c in components)

    odata_runtime = (
        f"""
  <script>
  window.DSB_ODATA_CONFIG = window.DSB_ODATA_CONFIG || {{}};
  var DSB = {{
    odata: {{
      bind: function(id, base, entity, opts) {{
        var params = [];
        if (opts.filter)  params.push('$filter='  + encodeURIComponent(opts.filter));
        if (opts.orderby) params.push('$orderby=' + encodeURIComponent(opts.orderby));
        if (opts.select)  params.push('$select='  + encodeURIComponent(opts.select));
        if (opts.top)     params.push('$top=' + opts.top);
        var url = (window.DSB_ODATA_CONFIG.baseUrl || base).replace(/\\/$/, '') +
                  '/' + entity + (params.length ? '?' + params.join('&') : '');
        fetch(url).then(function(r){{return r.json();}})
          .then(function(d){{ DSB.odata._apply(id, d, opts); }})
          .catch(function(e){{ console.warn('[DSB.odata]', e); }});
      }},
      _apply: function(id, data, opts) {{
        var el = document.getElementById(id); if(!el) return;
        var rows = data.value || [];
        var type = el.dataset.type;
        if (type === 'datagrid') DSB.odata._fillGrid(el, rows, opts.columns);
        if (type === 'combobox') DSB.odata._fillSelect(el, rows, opts);
      }},
      _fillGrid: function(el, rows, cols) {{
        var tbody = el.querySelector('tbody'); if (!tbody) return;
        tbody.innerHTML = '';
        rows.forEach(function(r) {{
          var tr = document.createElement('tr');
          (cols || Object.keys(r)).forEach(function(c) {{
            var td = document.createElement('td'); td.textContent = r[c]||''; tr.appendChild(td);
          }});
          tbody.appendChild(tr);
        }});
      }},
      _fillSelect: function(el, rows, opts) {{
        var sel = el.querySelector('select'); if(!sel) return;
        sel.innerHTML = '';
        rows.forEach(function(r) {{
          var o = document.createElement('option');
          o.value = r[opts.valueField||'id']||'';
          o.textContent = r[opts.labelField||Object.keys(r)[1]||'name']||'';
          sel.appendChild(o);
        }});
      }}
    }}
  }};
  document.addEventListener('DOMContentLoaded', function() {{
    {odata_init}
  }});
  </script>"""
        if has_odata
        else ""
    )

    return f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{page.title or page.name}</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
  <style>
    body {{ margin:0; padding:16px; background:#f0f4ff;
            font-family:'Segoe UI',system-ui,sans-serif; }}
    .dsb-canvas {{ position:relative; width:{canvas_w}px; min-height:{canvas_h}px;
                   background:{canvas_bg}; margin:0 auto;
                   box-shadow:0 2px 20px rgba(0,0,0,.1); }}
    .dsb-comp {{ position:absolute; box-sizing:border-box; }}
  </style>
</head>
<body>
  <div class="dsb-canvas" id="dsb_canvas">
{comps_html}
  </div>
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
  {odata_runtime}
</body>
</html>"""


def _render_component_html(comp) -> str:
    """Gera HTML simples de um componente para o export standalone."""
    p = comp.properties or {}
    style = (
        f"left:{comp.x}px;top:{comp.y}px;"
        f"width:{comp.width}px;min-height:{comp.height}px;"
        f"z-index:{comp.z_index};"
    )
    dtype = f'data-type="{comp.type}" data-dsb="{comp.name}"'

    if comp.type == "heading":
        tag = p.get("tag", "h2")
        fs = p.get("font_size", 22)
        col = p.get("text_color", "#012970")
        return f'<{tag} id="comp_{comp.id}" class="dsb-comp" style="{style}font-size:{fs}px;color:{col};font-weight:bold;margin:0;" {dtype}>{p.get("text","")}</{tag}>'
    if comp.type == "label":
        return f'<div id="comp_{comp.id}" class="dsb-comp" style="{style}" {dtype}>{p.get("text","")}</div>'
    if comp.type == "button":
        return f'<div id="comp_{comp.id}" class="dsb-comp" style="{style}" {dtype}><button class="btn btn-{p.get("variant","primary")}" style="width:100%;height:100%;">{p.get("text","Botão")}</button></div>'
    if comp.type in ("textbox", "numberbox", "datepicker"):
        itype = {"textbox": "text", "numberbox": "number", "datepicker": "date"}.get(
            comp.type, "text"
        )
        lbl = (
            f'<label style="font-size:11px;font-weight:600;display:block;margin-bottom:2px;">{p.get("label","")}</label>'
            if p.get("label")
            else ""
        )
        return f'<div id="comp_{comp.id}" class="dsb-comp" style="{style}" {dtype}>{lbl}<input type="{itype}" class="form-control form-control-sm" placeholder="{p.get("placeholder","")}"></div>'
    if comp.type == "combobox":
        lbl = (
            f'<label style="font-size:11px;font-weight:600;display:block;margin-bottom:2px;">{p.get("label","")}</label>'
            if p.get("label")
            else ""
        )
        opts = "".join(f"<option>{o}</option>" for o in p.get("items", []))
        return f'<div id="comp_{comp.id}" class="dsb-comp" style="{style}" {dtype}>{lbl}<select class="form-select form-select-sm"><option>{p.get("placeholder","Selecione...")}</option>{opts}</select></div>'
    if comp.type == "switch":
        return f'<div id="comp_{comp.id}" class="dsb-comp form-check form-switch" style="{style};display:flex;align-items:center;gap:8px;" {dtype}><input type="checkbox" class="form-check-input" role="switch"><label class="form-check-label">{p.get("text","")}</label></div>'
    if comp.type == "datagrid":
        cols = p.get("columns", [])
        ths = "".join(f"<th>{c}</th>" for c in cols)
        rows = "".join(
            "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>"
            for row in (p.get("rows") or [])
        )
        return (
            f'<div id="comp_{comp.id}" class="dsb-comp" style="{style};overflow:auto;" {dtype}>'
            f'<table class="table table-sm table-striped table-hover mb-0">'
            f'<thead class="table-dark"><tr>{ths}</tr></thead><tbody>{rows}</tbody></table></div>'
        )
    if comp.type == "groupbox":
        return (
            f'<fieldset id="comp_{comp.id}" class="dsb-comp" style="{style};border:1px solid #ced4da;border-radius:4px;padding:8px 12px;" {dtype}>'
            f'<legend style="font-size:12px;font-weight:600;padding:0 6px;color:#444;width:auto;">{p.get("title","Grupo")}</legend></fieldset>'
        )
    if comp.type == "alert":
        return f'<div id="comp_{comp.id}" class="dsb-comp alert alert-{p.get("variant","info")} mb-0" style="{style}" {dtype}>{p.get("text","")}</div>'
    # Fallback
    return f'<div id="comp_{comp.id}" class="dsb-comp" style="{style};border:1px dashed #ccc;border-radius:3px;padding:4px;font-size:12px;background:#f8f9fa;" {dtype}>{comp.type}: {p.get("text",comp.name)}</div>'


def _build_odata_init_js(components) -> str:
    """Gera código JS de inicialização do binding OData."""
    lines = []
    for comp in components:
        odata = (comp.properties or {}).get("odata")
        if not odata or not odata.get("connection_id"):
            continue
        conn = ODataConnection.query.get(odata["connection_id"])
        if not conn:
            continue
        base_url = conn.base_url.rstrip("/")
        entity = odata.get("entity", "")
        opts = json.dumps(
            {
                "filter": odata.get("filter", ""),
                "orderby": odata.get("orderby", ""),
                "select": odata.get("select", ""),
                "top": odata.get("page_size", 20),
                "columns": odata.get("columns", []),
            }
        )
        lines.append(
            f"    DSB.odata.bind('comp_{comp.id}', '{base_url}', '{entity}', {opts});"
        )
    return "\n".join(lines)
