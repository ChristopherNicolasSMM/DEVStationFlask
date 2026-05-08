"""
transactions/catalog.py — Catálogo Inicial de Transações DS_*
=============================================================
Seed executado na criação do banco.
Todas as transações NDS_* são adicionadas pela descoberta de plugins.
"""

DS_TRANSACTIONS = [
    # ── Core ───────────────────────────────────────────────────
    {
        "code": "DS_HOME",
        "label": "Início / Launchpad",
        "group": "Core",
        "description": "Tela inicial com launchpad de transações, projetos e favoritos.",
        "icon": "bi-house-fill",
        "route": "/",
        "min_profile": "USER",
        "is_standard": True,
    },
    {
        "code": "DS_PROJECTS",
        "label": "Meus Projetos",
        "group": "Core",
        "description": "Lista e gestão de projetos do DevStation Builder.",
        "icon": "bi-folder2-open",
        "route": "/?tab=projects",
        "min_profile": "USER",
        "is_standard": True,
    },
    # ── Design ─────────────────────────────────────────────────
    {
        "code": "DS_DESIGNER",
        "label": "Visual Designer",
        "group": "Design",
        "description": "Editor visual drag & drop de páginas e componentes.",
        "icon": "bi-layout-wtf",
        "route": "/designer/{pid}",
        "min_profile": "DEVELOPER",
        "is_standard": True,
    },
    {
        "code": "DS_MENU",
        "label": "Editor de Menu",
        "group": "Design",
        "description": "Editor visual da barra de menus do Designer.",
        "icon": "bi-list-ul",
        "route": "/transacoes/DS_MENU",
        "min_profile": "DEVELOPER",
        "is_standard": True,
    },
    # ── Integration ────────────────────────────────────────────
    {
        "code": "DS_ODATA",
        "label": "Gerenciador OData",
        "group": "Integration",
        "description": "Conecta servidores OData V4 e gera telas automaticamente.",
        "icon": "bi-cloud-arrow-down",
        "route": "/transacoes/DS_ODATA",
        "min_profile": "DEVELOPER",
        "is_standard": True,
    },
    # ── DevOps ─────────────────────────────────────────────────
    {
        "code": "DS_VERSIONS",
        "label": "Histórico de Versões",
        "group": "DevOps",
        "description": "Consulta e restauração de versões de páginas e projetos.",
        "icon": "bi-clock-history",
        "route": "/transacoes/DS_VERSIONS",
        "min_profile": "DEVELOPER",
        "is_standard": True,
    },
    {
        "code": "DS_BUILD",
        "label": "Build & Deploy",
        "group": "DevOps",
        "description": "Pipeline de testes automatizados e geração de ZIP de distribuição.",
        "icon": "bi-hammer",
        "route": "/transacoes/DS_BUILD",
        "min_profile": "CORE_DEV",
        "is_standard": True,
    },
    # ── Platform ───────────────────────────────────────────────
    {
        "code": "DS_PLUGINS",
        "label": "Gerenciador de Plugins",
        "group": "Platform",
        "description": "Lista, ativa e desativa plugins NDS_* da plataforma.",
        "icon": "bi-puzzle",
        "route": "/transacoes/DS_PLUGINS",
        "min_profile": "DEVELOPER",
        "is_standard": True,
    },
    {
        "code": "DS_ADDONS",
        "label": "Gerenciador de Addons",
        "group": "Platform",
        "description": "Lista, instala e gerencia extensões de componentes e integrações.",
        "icon": "bi-box-seam",
        "route": "/transacoes/DS_ADDONS",
        "min_profile": "DEVELOPER",
        "is_standard": True,
    },
    # ── Admin ──────────────────────────────────────────────────
    {
        "code": "DS_AUDIT",
        "label": "Console de Auditoria",
        "group": "Admin",
        "description": "Consulta de logs de auditoria e rastreabilidade de ações.",
        "icon": "bi-shield-check",
        "route": "/transacoes/DS_AUDIT",
        "min_profile": "ADMIN",
        "is_standard": True,
    },
    {
        "code": "DS_USERS",
        "label": "Gestão de Usuários",
        "group": "Admin",
        "description": "Cadastro e configuração de perfis de acesso.",
        "icon": "bi-people-fill",
        "route": "/transacoes/DS_USERS",
        "min_profile": "ADMIN",
        "is_standard": True,
    },
]
