"""
controllers/template_controller.py — Galeria de Templates
==========================================================
Fornece templates de página prontos para uso no designer.

  GET  /api/templates          → lista todos os templates
  POST /api/templates/<id>/aplicar/<pgid>  → aplica template a uma página
"""

from flask import Blueprint, jsonify, request
from models import db, Page, Component

bp = Blueprint("template", __name__)


# ── Catálogo de templates ──────────────────────────────────────────────────────
# Cada template define uma lista de componentes pré-configurados.
# Os componentes usam o mesmo schema do model Component.

TEMPLATE_CATALOG = [

    # ── Template 1: Formulário de Login ───────────────────────────────────────
    {
        "id":          "login_form",
        "name":        "Formulário de Login",
        "description": "Tela de login com campos e-mail e senha, botão de entrar e link de recuperação.",
        "icon":        "bi-door-open",
        "category":    "Formulário",
        "canvas_bg":   "#f0f4ff",
        "canvas_w":    1280,
        "canvas_h":    900,
        "components": [
            # Card container centralizado
            {"type":"card", "name":"cardLogin", "x":390, "y":120, "width":500, "height":420,
             "z_index":1, "properties":{"title":"Acesso ao Sistema","header_bg":"#4154f1",
             "header_color":"#fff","body":"","shadow":True,"border_radius":12}},
            # Título
            {"type":"heading", "name":"lblBemVindo", "x":440, "y":195, "width":400, "height":40,
             "z_index":2, "properties":{"text":"Bem-vindo!", "tag":"h4","font_size":22,
             "text_color":"#012970","bold":True,"text_align":"center"}},
            # Campo E-mail
            {"type":"textbox", "name":"txtEmail", "x":440, "y":260, "width":400, "height":42,
             "z_index":2, "properties":{"placeholder":"seu@email.com","label":"E-mail",
             "input_type":"email","font_size":14}},
            # Campo Senha
            {"type":"textbox", "name":"txtSenha", "x":440, "y":335, "width":400, "height":42,
             "z_index":2, "properties":{"placeholder":"••••••••","label":"Senha",
             "input_type":"password","font_size":14}},
            # Checkbox lembrar
            {"type":"checkbox", "name":"chkLembrar", "x":440, "y":400, "width":200, "height":30,
             "z_index":2, "properties":{"text":"Lembrar acesso","checked":False,"font_size":13}},
            # Botão entrar
            {"type":"button", "name":"btnEntrar", "x":440, "y":450, "width":400, "height":46,
             "z_index":2, "properties":{"text":"Entrar","variant":"primary","font_size":15,
             "bg_color":"#4154f1","text_color":"#fff","border_radius":8},
             "events":{"onClick":"DSB.toast('Verificando credenciais...','info');"}},
            # Link esqueci senha
            {"type":"label", "name":"lnkEsqueci", "x":440, "y":510, "width":400, "height":30,
             "z_index":2, "properties":{"text":"Esqueci minha senha","font_size":13,
             "text_color":"#4154f1","text_align":"center"}},
        ]
    },

    # ── Template 2: Dashboard com KPIs ────────────────────────────────────────
    {
        "id":          "dashboard_kpi",
        "name":        "Dashboard KPI",
        "description": "Painel de indicadores com 4 cards de KPI, gráfico e tabela de dados.",
        "icon":        "bi-speedometer2",
        "category":    "Dashboard",
        "canvas_bg":   "#f6f9ff",
        "canvas_w":    1280,
        "canvas_h":    900,
        "components": [
            # Título
            {"type":"heading", "name":"lblTitulo", "x":30, "y":20, "width":500, "height":48,
             "z_index":1, "properties":{"text":"Dashboard Analítico","tag":"h2","font_size":26,
             "text_color":"#012970","bold":True}},
            # KPI 1 — Receita
            {"type":"card", "name":"kpiReceita", "x":30, "y":90, "width":280, "height":110,
             "z_index":1, "properties":{"title":"Receita Total","body":"R$ 128.450","shadow":True,
             "header_bg":"#4154f1","header_color":"#fff","border_radius":8}},
            # KPI 2 — Clientes
            {"type":"card", "name":"kpiClientes", "x":340, "y":90, "width":280, "height":110,
             "z_index":1, "properties":{"title":"Novos Clientes","body":"1.284","shadow":True,
             "header_bg":"#2eca6a","header_color":"#fff","border_radius":8}},
            # KPI 3 — Pedidos
            {"type":"card", "name":"kpiPedidos", "x":650, "y":90, "width":280, "height":110,
             "z_index":1, "properties":{"title":"Pedidos","body":"3.672","shadow":True,
             "header_bg":"#ff771d","header_color":"#fff","border_radius":8}},
            # KPI 4 — Satisfação
            {"type":"card", "name":"kpiSat", "x":960, "y":90, "width":280, "height":110,
             "z_index":1, "properties":{"title":"Satisfação","body":"94%","shadow":True,
             "header_bg":"#ff0060","header_color":"#fff","border_radius":8}},
            # ProgressBar vendas
            {"type":"progressbar", "name":"pbVendas", "x":30, "y":230, "width":600, "height":28,
             "z_index":1, "properties":{"value":72,"variant":"primary","show_text":True,
             "striped":False,"height":22}},
            {"type":"label", "name":"lblMeta", "x":30, "y":212, "width":300, "height":20,
             "z_index":1, "properties":{"text":"Meta mensal: 72% atingida","font_size":13,
             "text_color":"#555","bold":True}},
            # Status bar
            {"type":"statusbar", "name":"stAtual", "x":30, "y":272, "width":600, "height":32,
             "z_index":1, "properties":{"text":"Sistema operacional — última atualização: agora",
             "icon":"bi-check-circle","bg_color":"#d1e7dd","text_color":"#0a3622"}},
            # Gráfico
            {"type":"chart", "name":"chartVendas", "x":30, "y":325, "width":580, "height":280,
             "z_index":1, "properties":{"chart_type":"bar","label":"Vendas mensais",
             "labels":["Jan","Fev","Mar","Abr","Mai","Jun"],
             "data":[42000,55000,48000,72000,61000,89000],"color":"#4154f1"}},
            # DataGrid recentes
            {"type":"datagrid", "name":"tblRecentes", "x":640, "y":230, "width":600, "height":380,
             "z_index":1, "properties":{
                "columns":["#","Cliente","Valor","Status"],
                "rows":[["001","Maria Silva","R$ 1.250","Pago"],
                        ["002","João Pereira","R$ 780","Pendente"],
                        ["003","Ana Costa","R$ 2.100","Pago"],
                        ["004","Pedro Lima","R$ 450","Cancelado"],
                        ["005","Carla Souza","R$ 890","Pago"]],
                "striped":True,"hover":True,"small":True}},
        ]
    },

    # ── Template 3: Formulário CRM ────────────────────────────────────────────
    {
        "id":          "crm_form",
        "name":        "Formulário CRM",
        "description": "Cadastro de cliente com dados pessoais, endereço e botões de ação.",
        "icon":        "bi-person-lines-fill",
        "category":    "Formulário",
        "canvas_bg":   "#ffffff",
        "canvas_w":    1280,
        "canvas_h":    900,
        "components": [
            # Título
            {"type":"heading", "name":"lblTitulo", "x":30, "y":20, "width":600, "height":48,
             "z_index":1, "properties":{"text":"Cadastro de Cliente","tag":"h2","font_size":24,
             "text_color":"#012970","bold":True}},
            {"type":"separator", "name":"sep1", "x":30, "y":75, "width":1200, "height":2,
             "z_index":1, "properties":{"color":"#e0e6f0","thickness":1}},
            # Dados pessoais
            {"type":"heading", "name":"lblDados", "x":30, "y":95, "width":300, "height":30,
             "z_index":1, "properties":{"text":"Dados Pessoais","tag":"h5","font_size":14,
             "text_color":"#4154f1","bold":True}},
            {"type":"textbox", "name":"txtNome", "x":30, "y":135, "width":380, "height":40,
             "z_index":1, "properties":{"label":"Nome Completo *","placeholder":"Ex: João Silva","font_size":14},
             "rules":[{"type":"obrigatorio","params":{"message":"Nome é obrigatório"}}]},
            {"type":"textbox", "name":"txtEmail", "x":440, "y":135, "width":380, "height":40,
             "z_index":1, "properties":{"label":"E-mail *","placeholder":"email@dominio.com",
             "input_type":"email","font_size":14},
             "rules":[{"type":"email","params":{"message":"E-mail inválido"}}]},
            {"type":"textbox", "name":"txtCpf", "x":850, "y":135, "width":380, "height":40,
             "z_index":1, "properties":{"label":"CPF *","placeholder":"000.000.000-00","font_size":14},
             "rules":[{"type":"cpf","params":{"message":"CPF inválido"}}]},
            {"type":"textbox", "name":"txtTel", "x":30, "y":205, "width":380, "height":40,
             "z_index":1, "properties":{"label":"Telefone","placeholder":"(11) 99999-9999","font_size":14}},
            {"type":"datepicker", "name":"dtNasc", "x":440, "y":205, "width":380, "height":40,
             "z_index":1, "properties":{"label":"Data de Nascimento","font_size":14}},
            {"type":"combobox", "name":"cmbStatus", "x":850, "y":205, "width":380, "height":40,
             "z_index":1, "properties":{"label":"Status","items":["Ativo","Inativo","Prospecto","VIP"],
             "placeholder":"Selecione...","font_size":14}},
            # Endereço
            {"type":"separator", "name":"sep2", "x":30, "y":270, "width":1200, "height":2,
             "z_index":1, "properties":{"color":"#e0e6f0","thickness":1}},
            {"type":"heading", "name":"lblEnd", "x":30, "y":285, "width":300, "height":30,
             "z_index":1, "properties":{"text":"Endereço","tag":"h5","font_size":14,
             "text_color":"#4154f1","bold":True}},
            {"type":"textbox", "name":"txtCep", "x":30, "y":325, "width":200, "height":40,
             "z_index":1, "properties":{"label":"CEP","placeholder":"00000-000","font_size":14}},
            {"type":"textbox", "name":"txtRua", "x":260, "y":325, "width":560, "height":40,
             "z_index":1, "properties":{"label":"Logradouro","placeholder":"Rua / Av.","font_size":14}},
            {"type":"numberbox", "name":"txtNum", "x":850, "y":325, "width":180, "height":40,
             "z_index":1, "properties":{"label":"Número","placeholder":"Nº","font_size":14}},
            {"type":"textbox", "name":"txtBairro", "x":30, "y":395, "width":380, "height":40,
             "z_index":1, "properties":{"label":"Bairro","placeholder":"Bairro","font_size":14}},
            {"type":"textbox", "name":"txtCidade", "x":440, "y":395, "width":380, "height":40,
             "z_index":1, "properties":{"label":"Cidade","placeholder":"Cidade","font_size":14}},
            {"type":"combobox", "name":"cmbEstado", "x":850, "y":395, "width":180, "height":40,
             "z_index":1, "properties":{"label":"UF","items":["AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"],"placeholder":"UF","font_size":14}},
            # Observações
            {"type":"textarea", "name":"txtObs", "x":30, "y":460, "width":1200, "height":80,
             "z_index":1, "properties":{"label":"Observações","placeholder":"Informações adicionais...","rows":3,"font_size":14}},
            # Botões
            {"type":"button", "name":"btnSalvar", "x":30, "y":565, "width":200, "height":44,
             "z_index":1, "properties":{"text":"Salvar","variant":"primary","icon":"bi-floppy","font_size":14,
             "bg_color":"#4154f1","text_color":"#fff","border_radius":6},
             "events":{"onClick":"DSB.validateAll() && DSB.toast('Cliente salvo com sucesso!','success');"}},
            {"type":"button", "name":"btnLimpar", "x":250, "y":565, "width":200, "height":44,
             "z_index":1, "properties":{"text":"Limpar","variant":"outline-secondary","icon":"bi-eraser","font_size":14,
             "border_radius":6}},
            {"type":"button", "name":"btnCancelar", "x":470, "y":565, "width":200, "height":44,
             "z_index":1, "properties":{"text":"Cancelar","variant":"outline-danger","icon":"bi-x-circle","font_size":14,
             "border_radius":6},
             "events":{"onClick":"window.history.back();"}},
            # StatusBar
            {"type":"statusbar", "name":"stStatus", "x":30, "y":630, "width":1200, "height":32,
             "z_index":1, "properties":{"text":"Pronto para cadastro","icon":"bi-info-circle",
             "bg_color":"#fff3cd","text_color":"#856404"}},
        ]
    },

    # ── Template 4: Landing Page ───────────────────────────────────────────────
    {
        "id":          "landing_page",
        "name":        "Landing Page",
        "description": "Página de apresentação com navbar, hero section, benefícios e CTA.",
        "icon":        "bi-rocket-takeoff",
        "category":    "Marketing",
        "canvas_bg":   "#ffffff",
        "canvas_w":    1280,
        "canvas_h":    900,
        "components": [
            # Navbar
            {"type":"navbar", "name":"navTop", "x":0, "y":0, "width":1280, "height":60,
             "z_index":1, "properties":{"brand":"MinhaMarca","links":["Home","Produto","Preços","Contato"],
             "variant":"dark","bg":"primary","expand":"lg"}},
            # Hero
            {"type":"heading", "name":"heroTitle", "x":120, "y":110, "width":700, "height":70,
             "z_index":1, "properties":{"text":"Solução Inteligente para o seu Negócio","tag":"h1",
             "font_size":40,"text_color":"#012970","bold":True}},
            {"type":"label", "name":"heroSubtitle", "x":120, "y":195, "width":600, "height":60,
             "z_index":1, "properties":{"text":"Automatize processos, aumente produtividade e escale com segurança. Junte-se a mais de 10.000 empresas.",
             "font_size":16,"text_color":"#666","line_height":1.6}},
            {"type":"button", "name":"btnCTA", "x":120, "y":280, "width":220, "height":52,
             "z_index":1, "properties":{"text":"Começar Grátis","variant":"primary","font_size":16,
             "bg_color":"#4154f1","text_color":"#fff","border_radius":8},
             "events":{"onClick":"DSB.toast('Redirecionando para cadastro...','info');"}},
            {"type":"button", "name":"btnDemo", "x":360, "y":280, "width":200, "height":52,
             "z_index":1, "properties":{"text":"Ver Demo","variant":"outline-primary","font_size":16,"border_radius":8}},
            # Imagem hero placeholder
            {"type":"image", "name":"imgHero", "x":800, "y":80, "width":400, "height":300,
             "z_index":1, "properties":{"src":"https://placehold.co/400x300/e8edff/4154f1?text=Produto",
             "alt":"Produto","object_fit":"cover","border_radius":12}},
            # Separador
            {"type":"separator", "name":"sep1", "x":120, "y":380, "width":1040, "height":2,
             "z_index":1, "properties":{"color":"#e0e6f0","thickness":1}},
            # Benefícios
            {"type":"heading", "name":"lblBeneficios", "x":120, "y":405, "width":1040, "height":40,
             "z_index":1, "properties":{"text":"Por que escolher nossa plataforma?","tag":"h2",
             "font_size":24,"text_color":"#012970","bold":True,"text_align":"center"}},
            # Cards benefícios
            {"type":"card", "name":"beneficio1", "x":120, "y":465, "width":300, "height":150,
             "z_index":1, "properties":{"title":"⚡ Rápido","body":"Configure em minutos. Sem necessidade de conhecimento técnico.",
             "shadow":True,"border_radius":10,"header_bg":"#4154f1","header_color":"#fff"}},
            {"type":"card", "name":"beneficio2", "x":460, "y":465, "width":300, "height":150,
             "z_index":1, "properties":{"title":"🔒 Seguro","body":"Dados protegidos com criptografia de ponta a ponta.",
             "shadow":True,"border_radius":10,"header_bg":"#2eca6a","header_color":"#fff"}},
            {"type":"card", "name":"beneficio3", "x":800, "y":465, "width":300, "height":150,
             "z_index":1, "properties":{"title":"📊 Analítico","body":"Relatórios em tempo real para decisões mais inteligentes.",
             "shadow":True,"border_radius":10,"header_bg":"#ff771d","header_color":"#fff"}},
            # CTA final
            {"type":"alert", "name":"alertCTA", "x":120, "y":640, "width":1040, "height":60,
             "z_index":1, "properties":{"text":"🎉 Experimente por 30 dias grátis — sem cartão de crédito!",
             "variant":"primary","font_size":15,"dismissible":False}},
        ]
    },

    # ── Template 5: Relatório / Kanban ────────────────────────────────────────
    {
        "id":          "relatorio_status",
        "name":        "Relatório de Status",
        "description": "Painel de acompanhamento com progresso de projetos, stepper e timeline.",
        "icon":        "bi-clipboard-data",
        "category":    "Relatório",
        "canvas_bg":   "#f6f9ff",
        "canvas_w":    1280,
        "canvas_h":    900,
        "components": [
            {"type":"heading", "name":"lblTitulo", "x":30, "y":20, "width":700, "height":48,
             "z_index":1, "properties":{"text":"Acompanhamento de Projetos","tag":"h2",
             "font_size":24,"text_color":"#012970","bold":True}},
            # Stepper de fases
            {"type":"stepper", "name":"fases", "x":30, "y":90, "width":1200, "height":70,
             "z_index":1, "properties":{"steps":["Planejamento","Desenvolvimento","Testes","Homologação","Produção"],
             "current":3,"variant":"primary"}},
            # Progresso por área
            {"type":"heading", "name":"lblProg", "x":30, "y":185, "width":400, "height":30,
             "z_index":1, "properties":{"text":"Progresso por Área","tag":"h5","font_size":14,
             "text_color":"#4154f1","bold":True}},
            {"type":"label", "name":"lblBack", "x":30, "y":225, "width":120, "height":20,
             "z_index":1, "properties":{"text":"Backend","font_size":12,"text_color":"#555","bold":True}},
            {"type":"progressbar", "name":"pbBack", "x":160, "y":225, "width":440, "height":20,
             "z_index":1, "properties":{"value":85,"variant":"success","show_text":True,"height":20}},
            {"type":"label", "name":"lblFront", "x":30, "y":260, "width":120, "height":20,
             "z_index":1, "properties":{"text":"Frontend","font_size":12,"text_color":"#555","bold":True}},
            {"type":"progressbar", "name":"pbFront", "x":160, "y":260, "width":440, "height":20,
             "z_index":1, "properties":{"value":68,"variant":"primary","show_text":True,"height":20}},
            {"type":"label", "name":"lblTestes", "x":30, "y":295, "width":120, "height":20,
             "z_index":1, "properties":{"text":"Testes","font_size":12,"text_color":"#555","bold":True}},
            {"type":"progressbar", "name":"pbTestes", "x":160, "y":295, "width":440, "height":20,
             "z_index":1, "properties":{"value":42,"variant":"warning","show_text":True,"height":20}},
            {"type":"label", "name":"lblDocs", "x":30, "y":330, "width":120, "height":20,
             "z_index":1, "properties":{"text":"Documentação","font_size":12,"text_color":"#555","bold":True}},
            {"type":"progressbar", "name":"pbDocs", "x":160, "y":330, "width":440, "height":20,
             "z_index":1, "properties":{"value":25,"variant":"danger","show_text":True,"height":20}},
            # Tabela de tarefas
            {"type":"datagrid", "name":"tblTarefas", "x":640, "y":185, "width":600, "height":280,
             "z_index":1, "properties":{
                "columns":["Tarefa","Responsável","Prazo","Status"],
                "rows":[["API de autenticação","Carlos M.","15/05","✅ Concluído"],
                        ["Tela de dashboard","Ana P.","20/05","🔄 Em andamento"],
                        ["Testes unitários","João R.","25/05","⏳ Pendente"],
                        ["Deploy staging","Maria S.","28/05","⏳ Pendente"]],
                "striped":True,"hover":True,"small":True}},
            # Alertas e status
            {"type":"alert", "name":"alrtAtencao", "x":30, "y":380, "width":580, "height":52,
             "z_index":1, "properties":{"text":"⚠️ Prazo do módulo de relatórios expira em 3 dias!",
             "variant":"warning","font_size":13}},
            {"type":"alert", "name":"alrtSucesso", "x":30, "y":445, "width":580, "height":52,
             "z_index":1, "properties":{"text":"✅ Ambiente de staging atualizado com sucesso.",
             "variant":"success","font_size":13}},
            # Timer de atualização
            {"type":"timer", "name":"tmrRefresh", "x":30, "y":515, "width":220, "height":40,
             "z_index":1, "properties":{"interval_ms":30000,"label":"Auto-refresh","enabled":False}},
            {"type":"statusbar", "name":"stConexao", "x":30, "y":570, "width":580, "height":32,
             "z_index":1, "properties":{"text":"Conectado — dados atualizados às 14:30",
             "icon":"bi-wifi","bg_color":"#d1e7dd","text_color":"#0a3622"}},
            # Tabs de visão
            {"type":"tabs", "name":"tabVisao", "x":640, "y":480, "width":600, "height":180,
             "z_index":1, "properties":{"tabs":["Por Sprint","Por Área","Por Responsável"],"variant":"tabs"}},
        ]
    },
]


@bp.route("/api/templates")
def list_templates():
    """Retorna catálogo completo de templates disponíveis."""
    # Retorna sem os components para listagem (economiza dados)
    summary = [
        {
            "id":          t["id"],
            "name":        t["name"],
            "description": t["description"],
            "icon":        t["icon"],
            "category":    t["category"],
            "comp_count":  len(t["components"]),
        }
        for t in TEMPLATE_CATALOG
    ]
    return jsonify({"ok": True, "templates": summary})


@bp.route("/api/templates/<string:template_id>/aplicar/<int:pgid>", methods=["POST"])
def apply_template(template_id: str, pgid: int):
    """
    Aplica um template a uma página existente.
    Substitui TODOS os componentes da página pelos do template.
    Aceita JSON body: {keep_existing: bool}
    """
    import datetime

    page = Page.query.get_or_404(pgid)
    data = request.get_json(force=True) or {}
    keep_existing = data.get("keep_existing", False)

    # Encontra o template pelo ID
    tmpl = next((t for t in TEMPLATE_CATALOG if t["id"] == template_id), None)
    if not tmpl:
        return jsonify({"ok": False, "error": f"Template '{template_id}' não encontrado."}), 404

    # Remove componentes existentes (se não mantiver)
    if not keep_existing:
        for comp in list(page.components):
            db.session.delete(comp)

    # Atualiza canvas da página
    page.canvas_bg = tmpl.get("canvas_bg", "#ffffff")
    page.canvas_w  = tmpl.get("canvas_w", 1280)
    page.canvas_h  = tmpl.get("canvas_h", 900)
    page.updated_at = datetime.datetime.utcnow()

    # Cria componentes do template
    for comp_data in tmpl["components"]:
        comp = Component(
            page_id    = page.id,
            type       = comp_data.get("type", "label"),
            name       = comp_data.get("name", "comp"),
            x          = comp_data.get("x", 0),
            y          = comp_data.get("y", 0),
            width      = comp_data.get("width", 150),
            height     = comp_data.get("height", 40),
            z_index    = comp_data.get("z_index", 1),
            properties = comp_data.get("properties", {}),
            events     = comp_data.get("events", {}),
            rules      = comp_data.get("rules", []),
        )
        db.session.add(comp)

    db.session.commit()

    return jsonify({
        "ok":          True,
        "template_id": template_id,
        "comp_added":  len(tmpl["components"]),
        "canvas_bg":   page.canvas_bg,
        "canvas_w":    page.canvas_w,
        "canvas_h":    page.canvas_h,
    })


@bp.route("/api/templates/<string:template_id>")
def get_template(template_id: str):
    """Retorna um template específico com todos os componentes."""
    tmpl = next((t for t in TEMPLATE_CATALOG if t["id"] == template_id), None)
    if not tmpl:
        return jsonify({"ok": False, "error": "Template não encontrado."}), 404
    return jsonify({"ok": True, "template": tmpl})
