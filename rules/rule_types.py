"""
rules/rule_types.py — Catálogo de Regras de Negócio
====================================================
Define as regras disponíveis para aplicar a componentes.
Cada regra tem: id, label, grupo, parâmetros e template JS
executado em runtime pelo rule_engine.js do frontend.

Grupos:
  Validação    → campos obrigatórios, formatos, limites
  Visibilidade → mostrar/ocultar/habilitar baseado em valor
  Cálculo      → somar, calcular, formatar, progresso
  Status       → mapear valor para texto/cor
"""

RULE_CATALOG = [

    # ── VALIDAÇÃO ─────────────────────────────────────────────
    {
        "group": "Validação",
        "rules": [
            {
                "id":       "obrigatorio",
                "label":    "Campo Obrigatório",
                "icon":     "bi-asterisk",
                "params":   [
                    {"name": "message", "label": "Mensagem de Erro",
                     "type": "text", "default": "Campo obrigatório."}
                ],
                "js_check": "DSB.rules.required(el, '{message}')",
                "description": "Impede que o campo fique vazio."
            },
            {
                "id":       "min_length",
                "label":    "Tamanho Mínimo",
                "icon":     "bi-text-left",
                "params":   [
                    {"name": "min",     "label": "Mínimo de Caracteres", "type": "number", "default": "3"},
                    {"name": "message", "label": "Mensagem",             "type": "text",
                     "default": "Mínimo de {min} caracteres."}
                ],
                "js_check": "DSB.rules.minLength(el, {min}, '{message}')",
                "description": "Valida tamanho mínimo do texto."
            },
            {
                "id":       "max_length",
                "label":    "Tamanho Máximo",
                "icon":     "bi-text-right",
                "params":   [
                    {"name": "max",     "label": "Máximo de Caracteres", "type": "number", "default": "100"},
                    {"name": "message", "label": "Mensagem",             "type": "text",
                     "default": "Máximo de {max} caracteres."}
                ],
                "js_check": "DSB.rules.maxLength(el, {max}, '{message}')",
                "description": "Valida tamanho máximo do texto."
            },
            {
                "id":       "email",
                "label":    "Formato E-mail",
                "icon":     "bi-envelope",
                "params":   [
                    {"name": "message", "label": "Mensagem", "type": "text",
                     "default": "E-mail inválido."}
                ],
                "js_check": "DSB.rules.email(el, '{message}')",
                "description": "Valida formato de e-mail."
            },
            {
                "id":       "cpf",
                "label":    "CPF Válido",
                "icon":     "bi-person-vcard",
                "params":   [
                    {"name": "message", "label": "Mensagem", "type": "text",
                     "default": "CPF inválido."}
                ],
                "js_check": "DSB.rules.cpf(el, '{message}')",
                "description": "Valida CPF com dígito verificador."
            },
            {
                "id":       "cnpj",
                "label":    "CNPJ Válido",
                "icon":     "bi-building",
                "params":   [
                    {"name": "message", "label": "Mensagem", "type": "text",
                     "default": "CNPJ inválido."}
                ],
                "js_check": "DSB.rules.cnpj(el, '{message}')",
                "description": "Valida CNPJ com dígito verificador."
            },
            {
                "id":       "numero",
                "label":    "Apenas Números",
                "icon":     "bi-123",
                "params":   [
                    {"name": "message", "label": "Mensagem", "type": "text",
                     "default": "Apenas números são permitidos."}
                ],
                "js_check": "DSB.rules.onlyNumbers(el, '{message}')",
                "description": "Aceita somente dígitos."
            },
            {
                "id":       "min_valor",
                "label":    "Valor Mínimo",
                "icon":     "bi-arrow-down-circle",
                "params":   [
                    {"name": "min",     "label": "Valor Mínimo", "type": "number", "default": "0"},
                    {"name": "message", "label": "Mensagem",     "type": "text",
                     "default": "Valor deve ser ≥ {min}."}
                ],
                "js_check": "DSB.rules.minValue(el, {min}, '{message}')",
                "description": "Valor numérico mínimo."
            },
            {
                "id":       "max_valor",
                "label":    "Valor Máximo",
                "icon":     "bi-arrow-up-circle",
                "params":   [
                    {"name": "max",     "label": "Valor Máximo", "type": "number", "default": "9999"},
                    {"name": "message", "label": "Mensagem",     "type": "text",
                     "default": "Valor deve ser ≤ {max}."}
                ],
                "js_check": "DSB.rules.maxValue(el, {max}, '{message}')",
                "description": "Valor numérico máximo."
            },
            {
                "id":       "data_valida",
                "label":    "Data Válida",
                "icon":     "bi-calendar-check",
                "params":   [
                    {"name": "message", "label": "Mensagem", "type": "text",
                     "default": "Data inválida."}
                ],
                "js_check": "DSB.rules.validDate(el, '{message}')",
                "description": "Verifica se a data é válida."
            },
        ]
    },

    # ── VISIBILIDADE / HABILITAÇÃO ─────────────────────────────
    {
        "group": "Visibilidade",
        "rules": [
            {
                "id":       "visivel_se",
                "label":    "Visível Se",
                "icon":     "bi-eye",
                "params":   [
                    {"name": "source_id", "label": "Campo Origem (ID)",  "type": "text",   "default": "comp_1"},
                    {"name": "operator",  "label": "Operador",           "type": "select",
                     "options": ["==","!=",">","<",">=","<=","contains"], "default": "=="},
                    {"name": "value",     "label": "Valor Comparado",    "type": "text",   "default": "sim"},
                ],
                "js_check": "DSB.rules.visibleIf(el, '{source_id}', '{operator}', '{value}')",
                "description": "Mostra este componente quando a condição for verdadeira."
            },
            {
                "id":       "oculto_se",
                "label":    "Oculto Se",
                "icon":     "bi-eye-slash",
                "params":   [
                    {"name": "source_id", "label": "Campo Origem (ID)", "type": "text",   "default": "comp_1"},
                    {"name": "operator",  "label": "Operador",          "type": "select",
                     "options": ["==","!=",">","<",">=","<="], "default": "=="},
                    {"name": "value",     "label": "Valor",             "type": "text",   "default": "nao"},
                ],
                "js_check": "DSB.rules.hiddenIf(el, '{source_id}', '{operator}', '{value}')",
                "description": "Oculta este componente quando a condição for verdadeira."
            },
            {
                "id":       "habilitado_se",
                "label":    "Habilitado Se",
                "icon":     "bi-toggle-on",
                "params":   [
                    {"name": "source_id", "label": "Campo Origem (ID)", "type": "text",   "default": "comp_1"},
                    {"name": "operator",  "label": "Operador",          "type": "select",
                     "options": ["==","!=","filled","empty"], "default": "filled"},
                    {"name": "value",     "label": "Valor (se ==)",     "type": "text",   "default": ""},
                ],
                "js_check": "DSB.rules.enabledIf(el, '{source_id}', '{operator}', '{value}')",
                "description": "Habilita o componente quando a condição for verdadeira."
            },
        ]
    },

    # ── CÁLCULO ───────────────────────────────────────────────
    {
        "group": "Cálculo",
        "rules": [
            {
                "id":       "calcular",
                "label":    "Calcular Expressão",
                "icon":     "bi-calculator",
                "params":   [
                    {"name": "expression", "label": "Expressão JS (use DSB.val('id'))",
                     "type": "text", "default": "DSB.val('comp_1') * 1.1"},
                    {"name": "target_id",  "label": "ID do Campo Destino",
                     "type": "text", "default": "comp_2"},
                ],
                "js_check": "DSB.rules.calculate('{target_id}', () => {expression})",
                "description": "Calcula e atribui resultado ao campo destino."
            },
            {
                "id":       "somar",
                "label":    "Somar Campos",
                "icon":     "bi-plus-circle",
                "params":   [
                    {"name": "ids",       "label": "IDs separados por vírgula",
                     "type": "text", "default": "comp_1,comp_2"},
                    {"name": "target_id", "label": "ID Destino",
                     "type": "text", "default": "comp_3"},
                ],
                "js_check": "DSB.rules.sum('{ids}'.split(','), '{target_id}')",
                "description": "Soma os valores dos campos e coloca no destino."
            },
            {
                "id":       "progresso",
                "label":    "Controlar ProgressBar",
                "icon":     "bi-bar-chart-steps",
                "params":   [
                    {"name": "source_id",  "label": "Campo Valor (ID)",       "type": "text",   "default": "comp_1"},
                    {"name": "min",        "label": "Valor Mínimo",           "type": "number", "default": "0"},
                    {"name": "max",        "label": "Valor Máximo",           "type": "number", "default": "100"},
                    {"name": "target_id",  "label": "ID da ProgressBar",      "type": "text",   "default": "comp_2"},
                ],
                "js_check": "DSB.rules.linkProgress('{source_id}', {min}, {max}, '{target_id}')",
                "description": "Vincula um campo numérico a uma barra de progresso."
            },
            {
                "id":       "status_map",
                "label":    "Mapear Status",
                "icon":     "bi-signpost-2",
                "params":   [
                    {"name": "source_id", "label": "Campo Origem (ID)",   "type": "text",
                     "default": "comp_1"},
                    {"name": "mapping",   "label": "JSON {valor: texto}", "type": "textarea",
                     "default": '{"1":"Ativo","0":"Inativo"}'},
                    {"name": "target_id", "label": "ID StatusBar/Label",  "type": "text",
                     "default": "comp_2"},
                ],
                "js_check": "DSB.rules.statusMap('{source_id}', {mapping}, '{target_id}')",
                "description": "Mapeia valor para texto e atualiza StatusBar/Label."
            },
            {
                "id":       "formatar",
                "label":    "Formatar Valor",
                "icon":     "bi-textarea-t",
                "params":   [
                    {"name": "source_id", "label": "Campo Origem (ID)", "type": "text",
                     "default": "comp_1"},
                    {"name": "format",    "label": "Formato (R$ {v})", "type": "text",
                     "default": "R$ {v}"},
                    {"name": "target_id", "label": "ID Destino",        "type": "text",
                     "default": "comp_2"},
                ],
                "js_check": "DSB.rules.format('{source_id}', '{format}', '{target_id}')",
                "description": "Formata o valor e exibe no campo destino."
            },
        ]
    },
]
