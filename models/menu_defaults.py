"""
models/menu_defaults.py — Configurações Padrão de Menu
========================================================
Define a estrutura JSON padrão para menu principal e sidebar.
Separado do model para manter o arquivo de model limpo.
"""

DEFAULT_MAIN_MENU = {
    "arquivo": {
        "label": "Arquivo", "ordem": 1,
        "items": [
            {"label": "Novo Projeto",     "shortcut": "Ctrl+N", "action": "new_project"},
            {"label": "Abrir Projeto",    "shortcut": "Ctrl+O", "action": "open_project"},
            {"separator": True},
            {"label": "Salvar",           "shortcut": "Ctrl+S", "action": "save"},
            {"label": "Salvar Como...",                          "action": "save_as"},
            {"separator": True},
            {"label": "Exportar HTML",                           "action": "export_html"},
            {"label": "Exportar ZIP",                            "action": "export_zip"},
            {"separator": True},
            {"label": "Sair",             "shortcut": "Alt+F4", "action": "quit"},
        ]
    },
    "editar": {
        "label": "Editar", "ordem": 2,
        "items": [
            {"label": "Desfazer",         "shortcut": "Ctrl+Z", "action": "undo"},
            {"label": "Refazer",          "shortcut": "Ctrl+Y", "action": "redo"},
            {"separator": True},
            {"label": "Copiar",           "shortcut": "Ctrl+C", "action": "copy"},
            {"label": "Colar",            "shortcut": "Ctrl+V", "action": "paste"},
            {"label": "Recortar",         "shortcut": "Ctrl+X", "action": "cut"},
            {"separator": True},
            {"label": "Duplicar",         "shortcut": "Ctrl+D", "action": "duplicate"},
            {"label": "Excluir",          "shortcut": "Del",    "action": "delete"},
            {"separator": True},
            {"label": "Selecionar Todos", "shortcut": "Ctrl+A", "action": "select_all"},
        ]
    },
    "visualizar": {
        "label": "Visualizar", "ordem": 3,
        "items": [
            {"label": "Preview",          "shortcut": "F5",     "action": "preview"},
            {"separator": True},
            {"label": "Zoom +",           "shortcut": "Ctrl++", "action": "zoom_in"},
            {"label": "Zoom -",           "shortcut": "Ctrl+-", "action": "zoom_out"},
            {"label": "Zoom 100%",        "shortcut": "Ctrl+0", "action": "zoom_reset"},
            {"separator": True},
            {"label": "Mostrar Grid",     "type": "checkbox",   "action": "toggle_grid"},
            {"label": "Mostrar Régua",    "type": "checkbox",   "action": "toggle_ruler"},
        ]
    },
    "inserir": {
        "label": "Inserir", "ordem": 4,
        "items": [
            {"label": "Botão",            "action": "insert:button"},
            {"label": "Campo de Texto",   "action": "insert:textbox"},
            {"label": "Textarea",         "action": "insert:textarea"},
            {"label": "Combo",            "action": "insert:combobox"},
            {"label": "CheckBox",         "action": "insert:checkbox"},
            {"separator": True},
            {"label": "DataGrid",         "action": "insert:datagrid"},
            {"label": "Chart",            "action": "insert:chart"},
            {"separator": True},
            {"label": "Card",             "action": "insert:card"},
            {"label": "Painel",           "action": "insert:panel"},
            {"label": "Abas (Tabs)",      "action": "insert:tabs"},
            {"separator": True},
            {"label": "Imagem",           "action": "insert:image"},
            {"label": "Ícone",            "action": "insert:icon"},
            {"label": "Progress Bar",     "action": "insert:progressbar"},
        ]
    },
    "ferramentas": {
        "label": "Ferramentas", "ordem": 5,
        "items": [
            {"label": "Editor de Eventos","action": "open_events"},
            {"label": "Editor de Regras", "action": "open_rules"},
            {"separator": True},
            {"label": "Gerador de Código","action": "generate_code"},
        ]
    },
    "ajuda": {
        "label": "Ajuda", "ordem": 6,
        "items": [
            {"label": "Documentação",     "shortcut": "F1",     "action": "open_docs"},
            {"label": "Sobre",                                   "action": "about"},
        ]
    },
}

DEFAULT_SIDEBAR = {
    "sections": [
        {
            "id": "pages",       "icon": "bi-files",       "label": "Páginas",
            "order": 1,          "expanded": True,
            "type": "pages_tree"
        },
        {
            "id": "components",  "icon": "bi-grid-3x3-gap","label": "Componentes",
            "order": 2,          "expanded": True,
            "type": "component_palette"
        },
        {
            "id": "outline",     "icon": "bi-list-nested", "label": "Outline",
            "order": 3,          "expanded": False,
            "type": "outline_tree"
        },
        {
            "id": "events",      "icon": "bi-lightning",   "label": "Eventos",
            "order": 4,          "expanded": False,
            "type": "events_panel"
        },
        {
            "id": "rules",       "icon": "bi-funnel",      "label": "Regras",
            "order": 5,          "expanded": False,
            "type": "rules_panel"
        },
    ]
}
