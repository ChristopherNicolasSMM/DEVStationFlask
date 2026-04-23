"""
controllers/export_controller.py — Exportação de Projetos
==========================================================
Gera o HTML/CSS/JS de cada página e empacota em ZIP.

  GET /projetos/<pid>/preview/<pgid>   → HTML ao vivo (nova aba)
  GET /projetos/<pid>/exportar         → download do ZIP
"""

import io
import zipfile
from flask import Blueprint, send_file, make_response
from models import Project, Page
from generators.html_generator import HtmlGenerator
from generators.css_generator  import CssGenerator
from generators.js_generator   import JsGenerator

bp = Blueprint("export", __name__)


@bp.route("/projetos/<int:pid>/preview/<int:pgid>")
def preview(pid: int, pgid: int):
    """Gera e retorna o HTML da página para preview em nova aba."""
    project = Project.query.get_or_404(pid)
    page    = Page.query.get_or_404(pgid)

    html = HtmlGenerator(project, page).render(inline_css=True, inline_js=True)
    return make_response(html, 200, {"Content-Type": "text/html; charset=utf-8"})


@bp.route("/projetos/<int:pid>/exportar")
def export_zip(pid: int):
    """Exporta todas as páginas do projeto em um arquivo ZIP."""
    project = Project.query.get_or_404(pid)
    buf = io.BytesIO()

    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        # Arquivo CSS compartilhado
        css = CssGenerator(project).render_all()
        zf.writestr("style.css", css)

        # Arquivo JS compartilhado (eventos + regras)
        js = JsGenerator(project).render_all()
        zf.writestr("app.js", js)

        # Uma página HTML por página
        for page in project.pages:
            filename = (page.slug or "index") + ".html"
            html = HtmlGenerator(project, page).render(
                inline_css=False, inline_js=False
            )
            zf.writestr(filename, html)

        # README
        zf.writestr("README.txt",
            f"Projeto: {project.name}\n"
            f"Gerado por DevStation Builder\n"
            f"Páginas: {', '.join(p.slug or 'index' for p in project.pages)}\n"
        )

    buf.seek(0)
    safe_name = "".join(c for c in project.name if c.isalnum() or c in " -_").strip() or "site"
    return send_file(
        buf,
        as_attachment=True,
        download_name=f"{safe_name}.zip",
        mimetype="application/zip",
    )
