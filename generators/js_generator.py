"""
generators/js_generator.py — Gerador de JavaScript
====================================================
Agrega o JS de eventos e regras de todos os componentes
de todas as páginas num único app.js para exportação ZIP.
"""

from components import ComponentRegistry


class JsGenerator:
    """Gera o app.js para exportação ZIP do projeto."""

    def __init__(self, project):
        self.project = project

    def render_all(self) -> str:
        """JS de todos os componentes de todas as páginas."""
        parts = [
            "// DevStation Builder — app.js",
            "// Gerado automaticamente — não edite manualmente",
            "document.addEventListener('DOMContentLoaded', () => {",
        ]
        for page in self.project.pages:
            if page.components:
                parts.append(f"\n  // ── Página: {page.name} ──")
                for comp in page.components:
                    js = ComponentRegistry.render_js(comp)
                    if js.strip():
                        parts.append("  " + js.replace("\n", "\n  "))
        parts.append("\n  if (typeof DSB !== 'undefined') DSB.initAll();")
        parts.append("});")
        return "\n".join(parts)
