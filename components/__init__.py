"""
components/__init__.py — Registry de Componentes
=================================================
Padrão Registry / Singleton:
  - Mantém um dicionário de type → instância de BaseComponent
  - Fornece métodos estáticos para consulta
  - Centraliza a descoberta de componentes disponíveis

Para registrar um novo componente:
  1. Crie a classe em definitions.py
  2. Adicione ao _COMPONENTS_LIST abaixo
"""

from typing import Dict, Optional

from .base_component import BaseComponent
from .definitions import (  # Entrada; Visualização; Container; Dados; Feedback; Navegação; Tempo
    AccordionComponent, AlertComponent, BadgeComponent, BreadcrumbComponent,
    ButtonComponent, CardComponent, ChartComponent, CheckBoxComponent,
    ComboBoxComponent, CountdownComponent, DataGridComponent,
    DatePickerComponent, FileUploadComponent, GroupBoxComponent,
    HeadingComponent, IconComponent, ImageComponent, LabelComponent,
    ModalComponent, NavbarComponent, NumberBoxComponent, PaginationComponent,
    PanelComponent, ProgressBarComponent, RadioButtonComponent,
    RatingComponent, SeparatorComponent, SliderComponent, SpinnerComponent,
    StatusBarComponent, StepperComponent, SwitchComponent, TabsComponent,
    TextAreaComponent, TextBoxComponent, TimerComponent)

# ── Lista ordenada de todos os componentes disponíveis ────────
_COMPONENTS_LIST = [
    # Entrada
    ButtonComponent(),
    TextBoxComponent(),
    TextAreaComponent(),
    NumberBoxComponent(),
    CheckBoxComponent(),
    RadioButtonComponent(),
    ComboBoxComponent(),
    SwitchComponent(),
    SliderComponent(),
    DatePickerComponent(),
    RatingComponent(),
    FileUploadComponent(),
    # Visualização
    LabelComponent(),
    HeadingComponent(),
    ImageComponent(),
    IconComponent(),
    BadgeComponent(),
    ProgressBarComponent(),
    StatusBarComponent(),
    SeparatorComponent(),
    SpinnerComponent(),
    # Container
    PanelComponent(),
    CardComponent(),
    GroupBoxComponent(),
    TabsComponent(),
    AccordionComponent(),
    # Dados
    DataGridComponent(),
    ChartComponent(),
    PaginationComponent(),
    # Feedback
    AlertComponent(),
    ModalComponent(),
    # Navegação
    NavbarComponent(),
    BreadcrumbComponent(),
    StepperComponent(),
    # Tempo
    TimerComponent(),
    CountdownComponent(),
]

# ── Dicionário type → instância (para lookups rápidos) ────────
_REGISTRY: Dict[str, BaseComponent] = {c.type: c for c in _COMPONENTS_LIST}


class ComponentRegistry:
    """
    Ponto único de acesso ao catálogo de componentes.
    Stateless — todos os métodos são estáticos.
    """

    @staticmethod
    def get(comp_type: str) -> Optional[dict]:
        """
        Retorna o entry do catálogo para um tipo.
        Retorna None se o tipo não existir.
        """
        instance = _REGISTRY.get(comp_type)
        return instance.to_catalog_entry() if instance else None

    @staticmethod
    def get_instance(comp_type: str) -> Optional[BaseComponent]:
        """Retorna a instância do componente (para render_html etc.)."""
        return _REGISTRY.get(comp_type)

    @staticmethod
    def get_catalog() -> list:
        """
        Retorna o catálogo completo agrupado por grupo,
        no formato esperado pelo frontend da paleta.
        """
        groups: Dict[str, list] = {}
        for comp in _COMPONENTS_LIST:
            g = comp.group
            if g not in groups:
                groups[g] = []
            groups[g].append(comp.to_catalog_entry())
        return [{"group": g, "items": items} for g, items in groups.items()]

    @staticmethod
    def all_types() -> list:
        """Lista todos os type strings disponíveis."""
        return list(_REGISTRY.keys())

    @staticmethod
    def render_component(comp_model) -> str:
        """
        Dado um objeto Component (SQLAlchemy), retorna o HTML gerado.
        Usado pelos generators.
        """
        instance = _REGISTRY.get(comp_model.type)
        if not instance:
            # Fallback: caixa vazia com aviso
            return (
                f'<div id="comp_{comp_model.id}" style="position:absolute;'
                f"left:{comp_model.x}px;top:{comp_model.y}px;"
                f"width:{comp_model.width}px;height:{comp_model.height}px;"
                f"border:2px dashed #f00;display:flex;align-items:center;"
                f'justify-content:center;font-size:12px;color:#f00;">'
                f"Tipo desconhecido: {comp_model.type}</div>"
            )
        return instance.render_html(
            comp_id=f"comp_{comp_model.id}",
            name=comp_model.name or f"comp_{comp_model.id}",
            props=comp_model.properties or {},
            x=comp_model.x,
            y=comp_model.y,
            width=comp_model.width,
            height=comp_model.height,
            z_index=comp_model.z_index,
        )

    @staticmethod
    def render_js(comp_model) -> str:
        """Retorna o JS (eventos + regras) de um componente."""
        instance = _REGISTRY.get(comp_model.type)
        if not instance:
            return ""
        return instance.render_js(
            comp_id=f"comp_{comp_model.id}",
            events=comp_model.events or {},
            rules=comp_model.rules or [],
        )

    @staticmethod
    def render_css(comp_model) -> str:
        """Retorna CSS customizado de um componente."""
        instance = _REGISTRY.get(comp_model.type)
        if not instance:
            return ""
        return instance.render_css(
            comp_id=f"comp_{comp_model.id}",
            props=comp_model.properties or {},
        )
