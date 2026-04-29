# 02 · Arquitetura do Sistema

> 📍 [Início](./README.md) › Arquitetura

---

## 🏗️ Stack Técnica

| Camada | Tecnologia | Versão | Finalidade |
|--------|-----------|--------|-----------|
| **Backend** | Flask | 3.x | Framework web, roteamento, Application Factory |
| **ORM** | SQLAlchemy + Flask-SQLAlchemy | 3.x | Persistência, relacionamentos, migrations |
| **Banco** | SQLite (dev) / PostgreSQL (prod) | — | Armazenamento de projetos e componentes |
| **Templates** | Jinja2 | 3.x | Renderização server-side das views |
| **Frontend** | JavaScript Puro (ES6+) | — | Toda lógica de designer sem frameworks pesados |
| **UI Framework** | Bootstrap 5 (local) | 5.3.3 | Layout responsivo e componentes Bootstrap |
| **Ícones** | Bootstrap Icons (local) | 1.11.3 | Ícones SVG via classes CSS |
| **Drag & Drop** | interact.js | 1.10.27 | Drag, resize e snap no canvas |
| **Gráficos (export)** | Chart.js | 4.4 | Gráficos no HTML exportado |

---

## 📐 C4 — Containers (Nível 2)

```mermaid
C4Container
    title DevStation Builder — Diagrama de Containers (C4 Level 2)

    Person(dev, "Developer / Analista")

    System_Boundary(builder, "DevStation Builder") {
        Container(web_app, "Flask Web App", "Python / Flask", "Application Factory, Blueprints, Jinja2 templates, geração de código HTML/CSS/JS")
        Container(static, "Static Assets", "HTML/CSS/JS/Vendors", "designer.js, designer.css, Bootstrap local, Bootstrap Icons, interact.js, uploads/")
        ContainerDb(db, "SQLite Database", "SQLite / SQLAlchemy", "Projetos, Páginas, Componentes, Menus, Versões")
        Container(uploads, "Upload Storage", "Filesystem /static/uploads/", "Imagens enviadas pelos usuários para uso nos componentes")
    }

    System_Ext(browser, "Navegador Web")
    System_Ext(ext_api, "APIs Externas REST")

    Rel(dev, browser, "Usa")
    Rel(browser, web_app, "HTTP GET/POST/DELETE", "JSON + HTML")
    Rel(browser, static, "GET static files")
    Rel(web_app, db, "SQLAlchemy ORM", "SQL")
    Rel(web_app, uploads, "os.path read/write")
    Rel(browser, ext_api, "fetch() no runtime exportado")
```

---

## 🧩 C4 — Componentes da Web App (Nível 3)

```mermaid
C4Component
    title Flask Web App — Diagrama de Componentes (C4 Level 3)

    Container_Boundary(web_app, "Flask Web App") {
        Component(app_factory, "Application Factory", "app.py / create_app()", "Inicializa Flask, registra Blueprints, cria tabelas")

        Component(proj_ctrl, "ProjectController", "Blueprint /projetos/*", "CRUD de projetos")
        Component(page_ctrl, "PageController", "Blueprint /designer/* /paginas/*", "CRUD de páginas, serve designer, save/load canvas")
        Component(comp_ctrl, "ComponentController", "Blueprint /api/componentes/*", "Catálogo de tipos, save events/rules")
        Component(event_ctrl, "EventController", "Blueprint /api/eventos/*", "Tipos de eventos e ações disponíveis")
        Component(rule_ctrl, "RuleController", "Blueprint /api/regras/*", "Catálogo de regras de negócio")
        Component(export_ctrl, "ExportController", "Blueprint /projetos/*/exportar", "Preview HTML + Export ZIP")
        Component(upload_ctrl, "UploadController", "Blueprint /upload/*", "Upload, listagem, deleção de imagens")
        Component(tmpl_ctrl, "TemplateController", "Blueprint /api/templates/*", "Galeria de templates, aplicação em páginas")

        Component(comp_reg, "ComponentRegistry", "components/__init__.py", "Singleton, catálogo dos 36 tipos, render_html/css/js")
        Component(generators, "Generators", "generators/", "HtmlGenerator, CssGenerator, JsGenerator")
        Component(models, "Models", "models/", "Project, Page, Component, Menu + SQLAlchemy")
    }

    ContainerDb(db, "Database")

    Rel(proj_ctrl, models, "usa")
    Rel(page_ctrl, models, "usa")
    Rel(page_ctrl, comp_reg, "catálogo")
    Rel(export_ctrl, generators, "gera HTML/CSS/JS")
    Rel(generators, comp_reg, "render_component()")
    Rel(models, db, "ORM")
    Rel(comp_ctrl, comp_reg, "get_catalog()")
    Rel(tmpl_ctrl, models, "cria componentes")
```

---

## 📁 Estrutura de Diretórios

```
dsb_v2/
│
├── app.py                     ← Application Factory (create_app)
├── config.py                  ← Configurações centralizadas por ambiente
├── requirements.txt
│
├── models/                    ── MODEL LAYER ──────────────────────────────
│   ├── __init__.py            ← db = SQLAlchemy() + exports
│   ├── project.py             ← Project (id, name, canvas_w/h/bg, pages, menus)
│   ├── page.py                ← Page (multi-página, canvas override)
│   ├── component.py           ← Component (type, pos, properties/events/rules JSON)
│   ├── menu.py                ← Menu (main + sidebar como JSON configurável)
│   └── menu_defaults.py       ← Configurações JSON padrão dos menus
│
├── controllers/               ── CONTROLLER LAYER ─────────────────────────
│   ├── __init__.py            ← register_blueprints()
│   ├── project_controller.py  ← CRUD /projetos/*
│   ├── page_controller.py     ← Designer + CRUD páginas + save/load + dup
│   ├── component_controller.py← Catálogo + eventos/regras por componente
│   ├── event_controller.py    ← /api/eventos/tipos + /api/eventos/acoes
│   ├── rule_controller.py     ← /api/regras/tipos
│   ├── export_controller.py   ← Preview HTML + Export ZIP
│   ├── menu_controller.py     ← /api/projetos/*/menus
│   ├── upload_controller.py   ← /upload/imagem (POST/GET/DELETE)
│   └── template_controller.py ← /api/templates (catálogo + aplicar)
│
├── views/                     ── VIEW LAYER ───────────────────────────────
│   ├── base.html              ← Layout NiceAdmin autossuficiente
│   ├── dashboard.html         ← Grid de projetos
│   └── designer.html          ← IDE visual completo
│
├── components/                ── COMPONENT REGISTRY ──────────────────────
│   ├── __init__.py            ← ComponentRegistry singleton
│   ├── base_component.py      ← BaseComponent (ABC)
│   └── definitions.py         ← 36 componentes implementados
│
├── events/                    ── EVENT SYSTEM ────────────────────────────
│   ├── __init__.py
│   ├── event_types.py         ← 11 categorias, ~50 tipos (onClick, onTick...)
│   └── event_actions.py       ← 23 ações pré-definidas (navegar, toast, API...)
│
├── rules/                     ── RULES SYSTEM ────────────────────────────
│   ├── __init__.py
│   └── rule_types.py          ← 18 tipos (validação, visibilidade, cálculo)
│
├── generators/                ── CODE GENERATION ─────────────────────────
│   ├── __init__.py
│   ├── html_generator.py      ← HTML completo + DSB runtime JS
│   ├── css_generator.py       ← CSS consolidado para export
│   └── js_generator.py        ← JS de eventos e regras para export
│
└── static/
    ├── css/designer.css        ← IDE dark theme CSS (504 linhas)
    ├── js/designer.js          ← Engine frontend (2.479 linhas, 14 módulos)
    ├── uploads/               ← Imagens enviadas pelos usuários
    └── assets/
        ├── css/style.css       ← NiceAdmin CSS
        ├── js/main.js          ← NiceAdmin JS
        └── vendor/            ← Bootstrap, Bootstrap Icons, Chart.js, ApexCharts,
                                   TinyMCE, Quill, interact.js...
```

---

## 🔄 Padrão MVC — Fluxo de Requisição

```mermaid
sequenceDiagram
    participant B as Navegador
    participant F as Flask Router
    participant C as Controller (Blueprint)
    participant M as Model (SQLAlchemy)
    participant DB as SQLite
    participant V as View (Jinja2)

    B->>F: GET /designer/1/1
    F->>C: page_controller.designer(pid=1, pgid=1)
    C->>M: Project.query.get(1)
    M->>DB: SELECT * FROM projects WHERE id=1
    DB-->>M: Project row
    M-->>C: Project object
    C->>M: ComponentRegistry.get_catalog()
    M-->>C: [{group, items}...]
    C->>V: render_template("designer.html", project=..., registry=...)
    V-->>B: HTML completo renderizado
```

---

## ⚙️ Application Factory

```python
# app.py — padrão Application Factory
def create_app(config_class=Config) -> Flask:
    app = Flask(__name__, template_folder="views", static_folder="static")
    app.config.from_object(config_class)
    db.init_app(app)              # inicializa SQLAlchemy
    register_blueprints(app)      # registra os 9 controllers
    with app.app_context():
        db.create_all()           # cria tabelas se não existirem
    return app
```

---

## 🔗 Navegação

| Anterior | Próximo |
|----------|---------|
| [← Visão Geral](./01_visao_geral.md) | [Modelos de Dados →](./03_modelos_dados.md) |
