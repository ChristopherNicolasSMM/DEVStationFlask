"""
components/base_component.py — Classe Base Abstrata
=====================================================
Todo componente do sistema herda desta classe.
Garante uma interface uniforme para:
  - Propriedades padrão
  - Listagem de eventos e regras disponíveis
  - Geração de HTML/CSS/JS

Para adicionar um novo componente:
  1. Crie components/meu_componente.py herdando BaseComponent
  2. Implemente os métodos abstratos
  3. Registre em components/__init__.py
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseComponent(ABC):
    """Interface comum a todos os componentes do Designer."""

    # ── Identidade ────────────────────────────────────────────────
    @property
    @abstractmethod
    def type(self) -> str:
        """Identificador único do tipo (ex: 'button', 'textbox')."""

    @property
    @abstractmethod
    def label(self) -> str:
        """Nome legível para exibir na paleta (ex: 'Botão', 'Campo Texto')."""

    @property
    @abstractmethod
    def icon(self) -> str:
        """Classe Bootstrap Icon (ex: 'bi-app', 'bi-input-cursor-text')."""

    @property
    def group(self) -> str:
        """Grupo na paleta (Entrada / Visualização / Container / Dados / Ação / Feedback / Navegação)."""
        return "Outros"

    # ── Propriedades ──────────────────────────────────────────────
    @property
    @abstractmethod
    def default_properties(self) -> Dict[str, Any]:
        """
        Mapa de propriedades padrão do componente.
        Exibidas e editáveis no painel de propriedades.
        """

    @property
    def default_size(self) -> Dict[str, int]:
        """Tamanho padrão ao ser solto no canvas."""
        return {"width": 150, "height": 40}

    # ── Eventos ───────────────────────────────────────────────────
    @property
    def available_events(self) -> List[str]:
        """
        Eventos que este componente pode disparar.
        Combinados com eventos universais no EventRegistry.
        """
        return []

    # ── Regras ────────────────────────────────────────────────────
    @property
    def available_rules(self) -> List[str]:
        """Tipos de regras aplicáveis a este componente."""
        return ["visivel_se", "habilitado_se"]

    # ── Geração de Código ─────────────────────────────────────────
    @abstractmethod
    def render_html(self, comp_id: str, name: str,
                    props: Dict, x: int, y: int,
                    width: int, height: int, z_index: int) -> str:
        """Gera o HTML do componente para exportação."""

    def render_css(self, comp_id: str, props: Dict) -> str:
        """CSS específico do componente (opcional — a maioria usa Bootstrap)."""
        return ""

    def render_js(self, comp_id: str, events: Dict, rules: List) -> str:
        """Gera o JavaScript para eventos e regras deste componente."""
        lines = [f"/* --- {comp_id} ({self.type}) --- */"]
        for event_name, action_code in (events or {}).items():
            if action_code.strip():
                lines.append(
                    f'document.getElementById("{comp_id}")'
                    f'.addEventListener("{_js_event(event_name)}", function(e) {{\n'
                    f'  {action_code}\n}});'
                )
        return "\n".join(lines)

    # ── Serialização para o catálogo ──────────────────────────────
    def to_catalog_entry(self) -> Dict:
        """Serializa o tipo para o catálogo enviado ao frontend."""
        return {
            "type":               self.type,
            "label":              self.label,
            "icon":               self.icon,
            "group":              self.group,
            "default_properties": self.default_properties,
            "default_size":       self.default_size,
            "available_events":   self.available_events,
            "available_rules":    self.available_rules,
        }

    # ── Helper comum para posicionamento ─────────────────────────
    @staticmethod
    def position_style(x: int, y: int, w: int, h: int, z: int,
                       extra: str = "") -> str:
        """Gera o CSS inline de posicionamento absoluto."""
        return (
            f"position:absolute;left:{x}px;top:{y}px;"
            f"width:{w}px;min-height:{h}px;z-index:{z};"
            f"box-sizing:border-box;{extra}"
        )


# ── Mapeamento nomes de evento (Delphi-style → DOM-style) ───────────────────

_EVENT_MAP = {
    "onClick":       "click",
    "onDoubleClick": "dblclick",
    "onMouseEnter":  "mouseenter",
    "onMouseLeave":  "mouseleave",
    "onRightClick":  "contextmenu",
    "onFocus":       "focus",
    "onBlur":        "blur",
    "onChange":      "change",
    "onKeyUp":       "keyup",
    "onKeyDown":     "keydown",
    "onInput":       "input",
    "onScroll":      "scroll",
}


def _js_event(name: str) -> str:
    """Converte onClick → click, etc."""
    return _EVENT_MAP.get(name, name.replace("on", "", 1).lower())
