"""
generators/css_generator.py — Gerador de CSS do Projeto
=========================================================
Agrega o CSS de todos os componentes de todas as páginas
num único arquivo style.css para exportação em ZIP.
"""

from components import ComponentRegistry


class CssGenerator:
    """Gera o style.css para exportação ZIP do projeto."""

    def __init__(self, project):
        self.project = project

    def render_all(self) -> str:
        """CSS base + CSS customizado de todos os componentes."""
        parts = [self._base_css()]
        for page in self.project.pages:
            for comp in page.components:
                css = ComponentRegistry.render_css(comp)
                if css.strip():
                    parts.append(f"/* Página: {page.name} — {comp.type} #{comp.id} */")
                    parts.append(css)
        return "\n".join(parts)

    def _base_css(self) -> str:
        w  = self.project.canvas_w  or 1280
        bg = self.project.canvas_bg or "#ffffff"
        return f"""
/* DevStation Builder — style.css */
*, *::before, *::after {{ box-sizing: border-box; }}
body {{ margin: 0; padding: 16px; background: #f0f4ff;
        font-family: 'Segoe UI', system-ui, sans-serif; }}
.dsb-canvas {{
  position: relative; width: {w}px; background: {bg};
  margin: 0 auto; box-shadow: 0 2px 20px rgba(0,0,0,.1); overflow: hidden;
}}
@media (max-width: {w}px) {{
  .dsb-canvas {{ width: 100%; }}
  [style*="position:absolute"] {{
    position: relative !important; left: auto !important;
    top: auto !important; width: 100% !important; margin-bottom: 8px;
  }}
}}
#dsb-toast-container {{
  position: fixed; top: 20px; right: 20px; z-index: 9999;
  display: flex; flex-direction: column; gap: 8px;
}}
.dsb-toast {{
  padding: 12px 20px; border-radius: 6px; color: #fff;
  font-size: 14px; min-width: 220px;
  animation: dsb-slide-in .3s ease;
}}
@keyframes dsb-slide-in {{
  from {{ transform: translateX(120%); opacity: 0; }}
  to   {{ transform: translateX(0);    opacity: 1; }}
}}
.dsb-toast.info    {{ background: #0d6efd; }}
.dsb-toast.success {{ background: #198754; }}
.dsb-toast.warning {{ background: #fd7e14; }}
.dsb-toast.error   {{ background: #dc3545; }}
"""
