# DevStation Builder v3.0 — Documentação Técnica

**Stack:** Python / Flask / SQLAlchemy / Bootstrap Icons / Vanilla JS  
**Versão:** 3.0.4  
**Testes:** 58 passed  
**GitHub:** https://github.com/ChristopherNicolasSMM/DEVStationFlask

---

## Documentação Disponível

| Arquivo | Público | Conteúdo |
|---------|---------|----------|
| [`MANUAL_USUARIO.md`](./MANUAL_USUARIO.md) | Usuários / Devs | Manual completo de uso do DS_DESIGNER e todas as transações |
| [`GUIA_RAPIDO.md`](./GUIA_RAPIDO.md) | Devs novos | Início em 5 minutos, atalhos, exemplos rápidos |
| [`REFERENCIA_API.md`](./REFERENCIA_API.md) | Devs / Integradores | Todos os endpoints REST com exemplos JSON |
| [`CHANGELOG.md`](./CHANGELOG.md) | Todos | Histórico completo de versões e correções |
| [`ARCHITECTURE.mermaid`](./ARCHITECTURE.mermaid) | Arquitetos | Diagramas C4, ER e fluxo de dados |
| **Este arquivo** | Devs | Arquitetura técnica, estrutura, setup |

---

## Instalação

```bash
pip install -r requirements.txt
python app.py
# http://localhost:5000
```

**requirements.txt:**
```
flask>=3.0.0
flask-sqlalchemy>=3.1.1
s2modatapy>=0.1.0
pytest>=8.0.0
pytest-flask>=1.3.0
deepdiff>=7.0.0
```

---

## Estrutura de Pastas

```
devstation_builder/
│
├── app.py                        # Application Factory (create_app)
├── config.py                     # Configurações centralizadas
├── requirements.txt
├── build.py                      # Pipeline CLI: pytest + ZIP
│
├── models/                       # SQLAlchemy Models
│   ├── __init__.py               # Expõe db + todos os models
│   ├── project.py                # Projeto (raiz da hierarquia)
│   ├── page.py                   # Página dentro de projeto
│   ├── component.py              # Componente posicionado no canvas
│   ├── menu.py                   # Menu/sidebar (JSON)
│   ├── menu_defaults.py          # Configuração padrão de menus
│   ├── odata_connection.py       # Conexão OData V4 com cache
│   ├── page_version.py           # Snapshot de página com soft-delete
│   ├── version_backup.py         # Registro imutável de .dsk gerados
│   ├── transaction.py            # Catálogo de transações DS_*/NDS_*
│   ├── plugin.py                 # Plugin descoberto em plugins/
│   ├── addon.py                  # Addon de extensão
│   ├── addon_log.py              # Log imutável de ações de addon
│   └── build_log.py              # Log de builds pytest
│
├── controllers/                  # Blueprints Flask (MVC Controller)
│   ├── __init__.py               # Registra todos os blueprints
│   ├── project_controller.py     # CRUD de projetos + rota /designer
│   ├── page_controller.py        # CRUD de páginas + save/load canvas
│   ├── component_controller.py   # CRUD de componentes individuais
│   ├── event_controller.py       # Eventos de componente
│   ├── rule_controller.py        # Regras de componente
│   ├── export_controller.py      # Preview inline + export HTML/ZIP
│   ├── menu_controller.py        # CRUD de menus
│   ├── odata_controller.py       # OData: conexões, entidades, geração
│   ├── version_controller.py     # Versões: CRUD, diff, restore, .dsk
│   ├── build_controller.py       # Pipeline: pytest + ZIP
│   ├── nav_controller.py         # DS_HOME + navegação /transacoes/<code>
│   ├── plugin_controller.py      # Ativar/desativar plugins
│   └── addon_controller.py       # Instalar/ativar/log addons
│
├── odata/                        # Módulo de integração OData V4
│   ├── __init__.py
│   ├── connection_manager.py     # Descoberta de $metadata + HTTP client
│   └── screen_generator.py      # Gera Page+Components a partir de UIAnnotations
│
├── versioning/                   # Motor de versionamento
│   ├── __init__.py
│   ├── snapshot.py               # Criar/restaurar snapshots + gerar .dsk
│   └── diff_engine.py            # Comparação entre dois snapshots
│
├── transactions/                 # Catálogo DS_* e descoberta de plugins
│   ├── __init__.py
│   ├── catalog.py                # Lista de transações DS_* nativas
│   └── registry.py               # Seed no banco + scan de plugins/
│
├── components/                   # ComponentRegistry (legado v2.2)
│   ├── __init__.py               # Singleton ComponentRegistry
│   ├── base_component.py         # Classe abstrata BaseComponent
│   └── definitions.py            # 36 tipos de componente
│
├── events/                       # Catálogo de eventos e ações (legado v2.2)
│   ├── __init__.py
│   ├── event_types.py
│   └── event_actions.py
│
├── rules/                        # Catálogo de regras (legado v2.2)
│   ├── __init__.py
│   └── rule_types.py
│
├── tests/                        # Suite pytest
│   ├── conftest.py               # App em memória, fixtures, seed de dados
│   ├── test_smoke.py             # Todas as rotas HTTP (project/page/component/menu/nav)
│   ├── test_odata.py             # Conexões OData com mock de servidor
│   ├── test_versioning.py        # Criar/restaurar/diff/deletar versões + .dsk
│   └── test_transactions.py      # Catálogo DS_*, busca, navegação
│
├── plugins/                      # Pasta de plugins NDS_* (scan automático)
│   └── .gitkeep
│
├── addons/                       # Pasta de addons extraídos
│   └── .gitkeep
│
├── views/                        # Templates Jinja2
│   ├── base.html                 # Base com header, campo tx global, toast
│   ├── dashboard.html            # DS_HOME: launchpad multi-aba
│   ├── designer.html             # DS_DESIGNER: canvas + painéis
│   ├── preview.html              # Preview inline com estilo do sistema
│   ├── ds_versions.html          # DS_VERSIONS: histórico de versões
│   ├── ds_plugins.html           # DS_PLUGINS: gerenciador de plugins
│   ├── ds_addons.html            # DS_ADDONS: gerenciador de addons
│   ├── ds_build.html             # DS_BUILD: pipeline de testes
│   ├── ds_menu_editor.html       # DS_MENU: editor visual de menu
│   ├── ds_odata.html             # DS_ODATA: overview de conexões
│   ├── ds_audit_stub.html        # DS_AUDIT: stub (v4.0)
│   ├── ds_users_stub.html        # DS_USERS: stub (v4.0)
│   └── 404_tx.html               # Transação não encontrada
│
├── static/
│   └── js/
│       ├── designer.js           # Engine canvas: drag/resize/select/undo/zoom
│       ├── odata_panel.js        # Painel OData: conexões, entidades, binding
│       ├── version_panel.js      # Painel histórico: timeline, criar, restaurar
│       └── transaction_nav.js    # Campo tx global, autocomplete, launchpad
│
├── dist/                         # ZIPs de distribuição (gerado por DS_BUILD)
│   └── backups/                  # Backups .dsk de versões deletadas
│
├── instance/                     # Banco SQLite (gitignored)
│   └── devstation.db
│
└── docs/
    ├── README.md                 # Este arquivo
    ├── MANUAL_USUARIO.md         # Manual completo do usuário
    ├── GUIA_RAPIDO.md            # Quick start
    ├── REFERENCIA_API.md         # Referência de todos os endpoints
    ├── CHANGELOG.md              # Histórico de versões
    └── ARCHITECTURE.mermaid      # Diagramas C4 + ER
```

---

## Arquitetura

### Application Factory

```python
# app.py
def create_app(test_config=None) -> Flask:
    app = Flask(__name__, template_folder="views")
    app.config.from_object(Config)
    db.init_app(app)
    with app.app_context():
        db.create_all()
    register_blueprints(app)       # 13 blueprints
    seed_transactions(app)         # DS_* no banco
    discover_plugins(app)          # scan plugins/
    return app
```

### Hierarquia de Models

```
Project (1)
  ├── Page (N)
  │     ├── Component (N)          ← properties{odata{...}} para binding
  │     └── PageVersion (N)        ← snapshot completo
  ├── Menu (N)                     ← config JSON (main/sidebar)
  └── ODataConnection (N)          ← cache de $metadata

Transaction (global)               ← catálogo DS_*/NDS_*
Plugin      (global)               ← descobertos em plugins/
Addon       (global)               ← instalados em addons/
  └── AddonLog (N)                 ← log imutável de ações
BuildLog    (global)               ← histórico de builds pytest
VersionBackup (global)             ← registro de .dsk gerados
```

### Fluxo de Versionamento

```
save_page()
    └── create_auto_snapshot()
            └── PageVersion(is_auto=True)
                    └── _suggest_purge_if_needed()  ← SUGERE, nunca purga

delete_version()
    └── delete_version_with_backup()
            ├── gera .dsk (ZIP com version.json)
            ├── registra VersionBackup no banco
            └── soft-delete PageVersion

restore_snapshot()
    ├── create_named_snapshot("pre-restore")   ← ANTES de restaurar
    ├── deleta componentes atuais
    └── recria do snapshot
```

### Cadeia de Descoberta OData ($metadata)

```
fetch_metadata()
    ├── [Cache válido?] → retorna cache
    └── _discover_and_fetch_metadata()
            ├── _extract_context_base()          # GET base_url → @odata.context
            │     └── Tenta {ctx_base}.json
            ├── {base}/$metadata.json            # JSON prioritário
            ├── {base}/%24metadata.json
            ├── {base}/metadata.json
            ├── {base}/$metadata                 # XML fallback
            ├── {base}/%24metadata
            └── {base}/metadata
                    └── _parse_response()        # auto-detecta JSON ou XML
```

### Fluxo de Geração de Tela OData

```
ODataScreenGenerator.generate("Customers", "form")
    ├── mgr.get_entity("Customers")             # do cache de metadata
    ├── _create_page("Clientes — Formulário")
    ├── Heading component (y=20, h=52)
    ├── Para cada grupo em ui.form.groups:
    │     ├── GroupBox (altura = ceil(fields/2) × field_h)
    │     └── Para cada campo:
    │           ├── Tipo: TEXT→textbox, NUMBER→numberbox...
    │           ├── Position: col_w proporcional ao canvas_w
    │           ├── Props: label, placeholder, odata.field_binding
    │           └── Rules: obrigatorio, max_length (se declarado)
    ├── Botões Salvar/Cancelar
    └── create_auto_snapshot(tags=["odata-gen", "auto-form"])
```

---

## Módulos Principais

### `ODataConnectionManager`

```python
mgr = ODataConnectionManager(connection)
mgr.test_connection()          # → {"ok": True, "entities_count": 3}
mgr.fetch_metadata()           # → {"entities": [...]}  (com cache)
mgr.list_entities()            # → [{name, label, fields, ui}]
mgr.get_entity("Customers")   # → {name, label, fields, ui}
mgr.query("Customers", {"$filter": "Country eq 'BR'", "$top": "20"})
mgr.patch("Customers", "1", {"CompanyName": "Novo Nome"})
```

### `ODataScreenGenerator`

```python
gen = ODataScreenGenerator(connection, project)
pages = gen.generate("Customers", "both", "Clientes")
# → [{"id": 5, "name": "Clientes — Lista"}, {"id": 6, "name": "...Formulário"}]
```

### `versioning.snapshot`

```python
from versioning import (
    create_auto_snapshot,    # chamado pelo save_page automaticamente
    create_named_snapshot,   # chamado pelo usuário via API
    restore_snapshot,        # restaura + cria pre-restore
    delete_version_with_backup,  # gera .dsk + soft-delete
    get_purge_suggestions,   # lista versões sugeridas p/ purga
    diff_versions,           # {"added": [...], "removed": [...]}
)
```

### `transactions.registry`

```python
seed_transactions(app)   # insere DS_* se não existirem
discover_plugins(app)    # scan plugins/ → registra no banco (inativo)
                         # carrega apenas plugins com is_active=True
```

---

## Testes

```bash
# Suite completa
python -m pytest tests/ -v

# Por módulo
python -m pytest tests/test_smoke.py        # rotas HTTP core
python -m pytest tests/test_odata.py        # OData com mock
python -m pytest tests/test_versioning.py   # versioning + .dsk
python -m pytest tests/test_transactions.py # catálogo + navegação
```

**Fixtures (`tests/conftest.py`):**

| Fixture | Escopo | Descrição |
|---------|--------|-----------|
| `app` | session | Flask com SQLite in-memory + seed |
| `client` | function | Test client HTTP |
| `project_id` | function | ID do projeto de teste |
| `page_id` | function | ID da página de teste |
| `odata_conn_id` | function | ID de conexão OData (se existir) |

---

## Build Pipeline

```bash
# Testes + ZIP via terminal
python -m pytest tests/ && python -c "
import zipfile, os
with zipfile.ZipFile('dist/devstation_v3.0.4.zip','w') as z:
    for r,d,f in os.walk('.'):
        d[:] = [x for x in d if x not in {'.git','__pycache__','dist','.venv'}]
        for file in f:
            if not file.endswith('.pyc'):
                z.write(os.path.join(r,file))
"

# Via DS_BUILD (browser)
POST /api/build/run-tests   → aguarda status 'passed'
POST /api/build/create-zip  → gera dist/devstation_builder_v3.0.4_{ts}.zip
GET  /api/build/zip/{id}/download
```

---

## Configurações (`config.py`)

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `SECRET_KEY` | `devstation-builder-secret-v3` | Chave Flask session |
| `SQLALCHEMY_DATABASE_URI` | `sqlite:///instance/devstation.db` | Banco de dados |
| `DEFAULT_CANVAS_W` | `1280` | Largura padrão do canvas |
| `DEFAULT_CANVAS_H` | `900` | Altura padrão do canvas |
| `VERSION_AUTO_SUGGEST_PURGE_AFTER` | `10` | Threshold de sugestão de purga |
| `DSK_EXTENSION` | `.dsk` | Extensão dos backups |
| `ODATA_METADATA_TTL_SECONDS` | `300` | TTL do cache de metadata (5 min) |
| `PLUGINS_DIR` | `./plugins` | Pasta de plugins NDS_* |
| `ADDONS_DIR` | `./addons` | Pasta de addons extraídos |
| `BUILD_DIST_DIR` | `./dist` | Pasta de ZIPs de distribuição |
| `BUILD_VERSION` | `3.0.0` | Versão atual para o ZIP |

---

## Extensão da Plataforma

### Adicionar Novo Componente

1. Em `components/definitions.py`, crie uma classe herdando `BaseComponent`
2. Implemente: `type`, `label`, `icon`, `group`, `default_properties`, `default_size`, `render_html()`
3. Registre em `components/__init__.py` → `_COMPONENTS_LIST`
4. Adicione a prévia em `static/js/designer.js` → objeto `map` em `_buildPreview()`
5. Execute `python -m pytest tests/test_smoke.py` para validar

### Adicionar Nova Transação DS_*

1. Em `transactions/catalog.py`, adicione ao array `DS_TRANSACTIONS`
2. Em `controllers/nav_controller.py`, adicione handler em `_HANDLERS`
3. Crie o template em `views/ds_{codigo_lower}.html`
4. Execute o app — `seed_transactions()` inserirá no banco automaticamente

### Adicionar Plugin NDS_*

Veja seção dedicada em [`MANUAL_USUARIO.md`](./MANUAL_USUARIO.md#6-ds_plugins--gerenciador-de-plugins).

---

*DevStation Builder v3.0.4 — Documentação Técnica*  
*Atualizado em: 2026-05-08*
