"""
events/event_actions.py — Catálogo de Ações
============================================
Define todas as ações disponíveis para associar a eventos.
Cada ação tem: id, label, grupo, template de código JS
e parâmetros editáveis.
"""

ACTION_CATALOG = [
    # ── Navegação ──────────────────────────────────────────────
    {
        "group": "Navegação",
        "actions": [
            {
                "id": "nav_url",
                "label": "Navegar para URL",
                "params": [
                    {"name": "url", "label": "URL", "type": "text", "default": "/"}
                ],
                "template": "window.location.href = '{url}';",
            },
            {
                "id": "nav_page",
                "label": "Abrir Página do Projeto",
                "params": [
                    {
                        "name": "page",
                        "label": "Página",
                        "type": "text",
                        "default": "index.html",
                    }
                ],
                "template": "window.location.href = '{page}';",
            },
            {
                "id": "nav_back",
                "label": "Voltar",
                "params": [],
                "template": "window.history.back();",
            },
        ],
    },
    # ── UI ────────────────────────────────────────────────────
    {
        "group": "Interface",
        "actions": [
            {
                "id": "show_msg",
                "label": "Mostrar Mensagem",
                "params": [
                    {
                        "name": "msg",
                        "label": "Mensagem",
                        "type": "text",
                        "default": "Olá!",
                    },
                    {
                        "name": "type",
                        "label": "Tipo",
                        "type": "select",
                        "options": ["info", "success", "warning", "error"],
                        "default": "info",
                    },
                ],
                "template": "DSB.toast('{msg}', '{type}');",
            },
            {
                "id": "open_modal",
                "label": "Abrir Modal",
                "params": [
                    {
                        "name": "id",
                        "label": "ID do Modal",
                        "type": "text",
                        "default": "myModal",
                    }
                ],
                "template": "new bootstrap.Modal(document.getElementById('{id}_m')).show();",
            },
            {
                "id": "close_modal",
                "label": "Fechar Modal Atual",
                "params": [],
                "template": "bootstrap.Modal.getInstance(document.querySelector('.modal.show'))?.hide();",
            },
            {
                "id": "toggle_visible",
                "label": "Mostrar/Ocultar Componente",
                "params": [
                    {
                        "name": "id",
                        "label": "ID do Componente",
                        "type": "text",
                        "default": "comp_1",
                    }
                ],
                "template": "DSB.toggleVisible('{id}');",
            },
            {
                "id": "set_visible",
                "label": "Definir Visibilidade",
                "params": [
                    {"name": "id", "label": "ID", "type": "text", "default": "comp_1"},
                    {
                        "name": "visible",
                        "label": "Visível?",
                        "type": "select",
                        "options": ["true", "false"],
                        "default": "true",
                    },
                ],
                "template": "DSB.setVisible('{id}', {visible});",
            },
            {
                "id": "set_enabled",
                "label": "Habilitar/Desabilitar",
                "params": [
                    {"name": "id", "label": "ID", "type": "text", "default": "comp_1"},
                    {
                        "name": "enabled",
                        "label": "Habilitado?",
                        "type": "select",
                        "options": ["true", "false"],
                        "default": "true",
                    },
                ],
                "template": "DSB.setEnabled('{id}', {enabled});",
            },
            {
                "id": "focus_comp",
                "label": "Focar Componente",
                "params": [
                    {"name": "id", "label": "ID", "type": "text", "default": "comp_1"}
                ],
                "template": "document.getElementById('{id}')?.focus();",
            },
        ],
    },
    # ── Valores ───────────────────────────────────────────────
    {
        "group": "Valores",
        "actions": [
            {
                "id": "set_value",
                "label": "Definir Valor",
                "params": [
                    {
                        "name": "id",
                        "label": "ID do Campo",
                        "type": "text",
                        "default": "comp_1",
                    },
                    {"name": "value", "label": "Valor", "type": "text", "default": ""},
                ],
                "template": "DSB.setValue('{id}', '{value}');",
            },
            {
                "id": "clear_field",
                "label": "Limpar Campo",
                "params": [
                    {
                        "name": "id",
                        "label": "ID do Campo",
                        "type": "text",
                        "default": "comp_1",
                    }
                ],
                "template": "DSB.setValue('{id}', '');",
            },
            {
                "id": "set_text",
                "label": "Definir Texto/Label",
                "params": [
                    {"name": "id", "label": "ID", "type": "text", "default": "comp_1"},
                    {"name": "text", "label": "Texto", "type": "text", "default": ""},
                ],
                "template": "DSB.setText('{id}', '{text}');",
            },
            {
                "id": "set_progress",
                "label": "Definir Progresso",
                "params": [
                    {
                        "name": "id",
                        "label": "ID ProgressBar",
                        "type": "text",
                        "default": "comp_1",
                    },
                    {
                        "name": "val",
                        "label": "Valor (0-100)",
                        "type": "number",
                        "default": "50",
                    },
                ],
                "template": "DSB.setProgress('{id}', {val});",
            },
        ],
    },
    # ── Timer ────────────────────────────────────────────────
    {
        "group": "Timer",
        "actions": [
            {
                "id": "start_timer",
                "label": "Iniciar Timer",
                "params": [
                    {
                        "name": "id",
                        "label": "ID do Timer",
                        "type": "text",
                        "default": "comp_1",
                    },
                    {
                        "name": "ms",
                        "label": "Intervalo (ms)",
                        "type": "number",
                        "default": "1000",
                    },
                ],
                "template": "DSB.startTimer('{id}', {ms});",
            },
            {
                "id": "stop_timer",
                "label": "Parar Timer",
                "params": [
                    {
                        "name": "id",
                        "label": "ID do Timer",
                        "type": "text",
                        "default": "comp_1",
                    }
                ],
                "template": "DSB.stopTimer('{id}');",
            },
            {
                "id": "start_countdown",
                "label": "Iniciar Countdown",
                "params": [
                    {
                        "name": "id",
                        "label": "ID Countdown",
                        "type": "text",
                        "default": "comp_1",
                    }
                ],
                "template": "DSB.startCountdown('{id}');",
            },
        ],
    },
    # ── Dados / API ───────────────────────────────────────────
    {
        "group": "Dados / API",
        "actions": [
            {
                "id": "call_api",
                "label": "Chamar API",
                "params": [
                    {
                        "name": "url",
                        "label": "URL",
                        "type": "text",
                        "default": "/api/dados",
                    },
                    {
                        "name": "method",
                        "label": "Método",
                        "type": "select",
                        "options": ["GET", "POST", "PUT", "DELETE"],
                        "default": "GET",
                    },
                    {
                        "name": "target",
                        "label": "ID Grid/Label destino",
                        "type": "text",
                        "default": "",
                    },
                ],
                "template": "DSB.callApi('{url}', '{method}', '{target}');",
            },
            {
                "id": "export_pdf",
                "label": "Exportar PDF",
                "params": [],
                "template": "window.print();",
            },
            {
                "id": "export_csv",
                "label": "Exportar CSV da Grid",
                "params": [
                    {
                        "name": "id",
                        "label": "ID da DataGrid",
                        "type": "text",
                        "default": "comp_1",
                    }
                ],
                "template": "DSB.exportCsv('{id}');",
            },
        ],
    },
    # ── Validação ─────────────────────────────────────────────
    {
        "group": "Validação",
        "actions": [
            {
                "id": "validate_form",
                "label": "Validar Formulário",
                "params": [],
                "template": "DSB.validateAll();",
            },
            {
                "id": "clear_validations",
                "label": "Limpar Validações",
                "params": [],
                "template": "DSB.clearValidations();",
            },
        ],
    },
    # ── JavaScript Livre ──────────────────────────────────────
    {
        "group": "JavaScript",
        "actions": [
            {
                "id": "custom_js",
                "label": "Código JavaScript Livre",
                "params": [
                    {
                        "name": "code",
                        "label": "Código JS",
                        "type": "textarea",
                        "default": "// seu código aqui\nconsole.log('evento disparado');",
                    }
                ],
                "template": "{code}",
            },
        ],
    },
]
