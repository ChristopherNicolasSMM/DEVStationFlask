"""
events/event_types.py — Catálogo de Eventos
============================================
Define quais eventos cada categoria de componente pode disparar.
Combina eventos universais com eventos específicos.

Nomenclatura estilo Delphi:
  onClick, onChange, onTick ...
"""

# Eventos que TODOS os componentes suportam
UNIVERSAL_EVENTS = [
    {"name": "onClick", "label": "Clique", "dom": "click"},
    {"name": "onDoubleClick", "label": "Duplo Clique", "dom": "dblclick"},
    {"name": "onMouseEnter", "label": "Mouse Entrou", "dom": "mouseenter"},
    {"name": "onMouseLeave", "label": "Mouse Saiu", "dom": "mouseleave"},
    {"name": "onRightClick", "label": "Clique Direito", "dom": "contextmenu"},
    {"name": "onFocus", "label": "Ganhou Foco", "dom": "focus"},
    {"name": "onBlur", "label": "Perdeu Foco", "dom": "blur"},
]

# Eventos específicos agrupados por categoria de componente
EVENT_CATALOG = {
    "universal": UNIVERSAL_EVENTS,
    "input": [
        {"name": "onChange", "label": "Valor Alterado", "dom": "change"},
        {"name": "onKeyUp", "label": "Tecla Solta", "dom": "keyup"},
        {"name": "onKeyDown", "label": "Tecla Pressionada", "dom": "keydown"},
        {"name": "onInput", "label": "Digitando", "dom": "input"},
        {
            "name": "onEnterPress",
            "label": "Enter Pressionado",
            "dom": "keyup",
            "condition": "e.key==='Enter'",
        },
    ],
    "datagrid": [
        {"name": "onRowClick", "label": "Linha Clicada", "dom": "click"},
        {"name": "onCellEdit", "label": "Célula Editada", "dom": "change"},
        {"name": "onSort", "label": "Ordenação", "dom": "click"},
        {"name": "onFilter", "label": "Filtro Aplicado", "dom": "input"},
    ],
    "progressbar": [
        {"name": "onComplete", "label": "Chegou a 100%", "dom": "complete"},
        {"name": "onProgress", "label": "Progresso Atualizado", "dom": "progress"},
    ],
    "timer": [
        {"name": "onTick", "label": "Intervalo Disparado", "dom": "tick"},
    ],
    "countdown": [
        {"name": "onTick", "label": "Tick", "dom": "tick"},
        {"name": "onComplete", "label": "Chegou a Zero", "dom": "complete"},
    ],
    "modal": [
        {"name": "onOpen", "label": "Abrindo", "dom": "show.bs.modal"},
        {"name": "onClose", "label": "Fechando", "dom": "hide.bs.modal"},
        {"name": "onConfirm", "label": "Confirmado", "dom": "confirm"},
        {"name": "onCancel", "label": "Cancelado", "dom": "cancel"},
    ],
    "tabs": [
        {"name": "onTabChange", "label": "Aba Mudou", "dom": "shown.bs.tab"},
    ],
    "accordion": [
        {"name": "onSectionChange", "label": "Seção Mudou", "dom": "shown.bs.collapse"},
    ],
    "form": [
        {"name": "onLoad", "label": "Página Carregou", "dom": "load"},
        {"name": "onUnload", "label": "Página Saindo", "dom": "beforeunload"},
        {"name": "onBeforeSave", "label": "Antes de Salvar", "dom": "beforesave"},
        {"name": "onAfterSave", "label": "Após Salvar", "dom": "aftersave"},
    ],
    "scroll": [
        {"name": "onScroll", "label": "Rolagem", "dom": "scroll"},
    ],
}
