# DevStation Builder v3.0 — Documentação

**Stack:** Python / Flask / SQLAlchemy / Bootstrap Icons / Vanilla JS  
**Versão:** 3.0.0  
**Status:** ✅ 58 testes passando

---

## Sumário

1. [Visão Geral](#1-visão-geral)
2. [Instalação](#2-instalação)
3. [Arquitetura](#3-arquitetura)
4. [Eixo A — Integração OData](#4-eixo-a--integração-odata)
5. [Eixo B — Versionamento](#5-eixo-b--versionamento)
6. [Eixo C — Build Pipeline](#6-eixo-c--build-pipeline)
7. [Eixo D — Navegação por Transações](#7-eixo-d--navegação-por-transações)
8. [Plugins e Addons](#8-plugins-e-addons)
9. [Referência de Rotas API](#9-referência-de-rotas-api)
10. [Testes](#10-testes)

---

## 1. Visão Geral

O **DevStation Builder v3.0** é a plataforma RAD visual construída sobre Flask + SQLAlchemy.  
Esta versão adiciona quatro novos eixos ao builder v2.2:

| Eixo | Código | Descrição |
|------|--------|-----------|
| A | OData | Conexão a servidores OData V4 com geração automática de telas |
| B | Version | Versionamento com snapshots, restauração e backup `.dsk` |
| C | Build | Pipeline pytest + geração de ZIP versionado (`DS_BUILD`) |
| D | Nav | Navegação por transações `DS_*` com launchpad e busca global |

---

## 2. Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/ChristopherNicolasSMM/DEVStationFlask

# 2. Instale dependências
pip install -r requirements.txt

# 3. Execute
python app.py

# 4. Acesse
http://localhost:5000
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

## 3. Arquitetura

```
dsb_v3/
├── app.py                     # Application Factory
├── config.py                  # Configurações centralizadas
├── models/                    # SQLAlchemy Models
│   ├── project.py             # Projeto (raiz)
│   ├── page.py                # Página dentro de um projeto
│   ├── component.py           # Componente posicionado na página
│   ├── menu.py                # Configuração de menu (JSON)
│   ├── odata_connection.py    # Conexão OData (Eixo A)
│   ├── page_version.py        # Versão/snapshot de página (Eixo B)
│   ├── version_backup.py      # Registro de backups .dsk (Eixo B)
│   ├── transaction.py         # Catálogo de transações DS_* (Eixo D)
│   ├── plugin.py              # Plugin NDS_* descoberto (Eixo D)
│   ├── addon.py               # Addon de extensão (Eixo D)
│   ├── addon_log.py           # Log imutável de ações de addon (Eixo D)
│   └── build_log.py           # Log de builds pytest (Eixo C)
├── controllers/               # Blueprints Flask (MVC)
├── odata/                     # Módulo OData V4 (Eixo A)
├── versioning/                # Snapshots e backups (Eixo B)
├── transactions/              # Registry e catálogo DS_* (Eixo D)
├── tests/                     # Suite pytest (Eixo C)
├── views/                     # Templates Jinja2
└── static/js/                 # JavaScript modular
    ├── transaction_nav.js     # Campo de transação + launchpad
    ├── odata_panel.js         # Painel OData no Designer
    └── version_panel.js       # Painel de versões no Designer
```

---

## 4. Eixo A — Integração OData

### Fluxo

```
1. Criar conexão  →  POST /api/projetos/<pid>/odata-connections
2. Testar         →  POST /api/odata-connections/<cid>/testar
3. Listar ent.    →  GET  /api/odata-connections/<cid>/entidades
4. Gerar tela     →  POST /api/odata-connections/<cid>/gerar-tela
```

### Geração automática de telas

```json
POST /api/odata-connections/1/gerar-tela
{
  "entity":    "Customers",
  "mode":      "both",
  "page_name": "Clientes"
}
```

Modos disponíveis: `list` | `form` | `both`

Resposta:
```json
{
  "ok": true,
  "pages": [
    { "id": 5, "name": "Clientes — Lista", ... },
    { "id": 6, "name": "Clientes — Formulário", ... }
  ]
}
```

### Mapeamento de tipos

| `FieldType` (S2MOdataPy) | Componente DSB |
|--------------------------|----------------|
| `TEXT` | `textbox` |
| `NUMBER` | `numberbox` |
| `DATE` | `datepicker` |
| `BOOLEAN` | `switch` |
| `DROPDOWN` | `combobox` |

### Binding no HTML exportado

Quando um componente tem `properties.odata` configurado, o `HtmlGenerator`
injeta automaticamente o runtime `DSB.odata` e o código de inicialização:

```javascript
DSB.odata.bind('comp_42', 'http://localhost:8000/odata', 'Customers', {
  filter: "Country eq 'Brazil'",
  orderby: 'CompanyName asc',
  top: 20
});
```

A URL base é configurável via `window.DSB_ODATA_CONFIG.baseUrl` sem necessidade de regerar o ZIP.

---

## 5. Eixo B — Versionamento

### Regras fundamentais

- **Nunca há purga automática** — o sistema apenas *sugere* versões antigas para purga.
- **Ao deletar qualquer versão**, um backup `.dsk` é gerado automaticamente antes.
- O arquivo `.dsk` é um ZIP renomeado contendo o JSON completo da versão.
- Todos os backups ficam registrados em `VersionBackup` para rastreabilidade total.
- Um snapshot pré-restauração é sempre criado antes de qualquer `restore`.

### Gatilhos de snapshot automático

| Evento | Tag | Retenção |
|--------|-----|----------|
| `save_page` (Ctrl+S) | `auto` | Permanente (sugestão de purga após 10) |
| Geração OData | `odata-gen` | Permanente |
| Pré-restauração | `pre-restore` | Permanente |
| Pré-reset de projeto | `pre-reset` | Permanente |

### Backup .dsk

```
Extensão:  .dsk  (DevStation Backup)
Conteúdo:  ZIP com version.json + README.txt
Local:     dist/backups/version_page{N}_{label}_{ts}.dsk
Registro:  tabela version_backups
```

### API de versões

```
GET  /api/paginas/<pgid>/versoes              → lista versões
POST /api/paginas/<pgid>/versoes              → criar versão nomeada
GET  /api/versoes/<vid>?snapshot=1            → detalhe + snapshot
POST /api/versoes/<vid>/restaurar             → restaurar
DELETE /api/versoes/<vid>                     → deletar (gera .dsk)
GET  /api/versoes/diff?a=<vid>&b=<vid>        → diff entre versões
GET  /api/paginas/<pgid>/versoes/sugestoes-purga → sugeridas para purga
GET  /api/versoes/backups/<pid>               → lista backups .dsk
GET  /api/versoes/backups/<bid>/download      → baixar .dsk
```

---

## 6. Eixo C — Build Pipeline

### Executar via CLI

```bash
python -m pytest tests/ -v
```

### Via API (`DS_BUILD`)

```
POST /api/build/run-tests     → inicia pytest em thread assíncrona
GET  /api/build/status        → status do último build
POST /api/build/create-zip    → gera ZIP de distribuição
GET  /api/build/logs          → histórico de builds
GET  /api/build/zip/<id>/download → baixar ZIP
```

O endpoint `run-tests` retorna imediatamente com `build_id`.
Use polling em `GET /api/build/logs/<build_id>` para acompanhar o resultado.

### Artefato gerado

```
dist/devstation_builder_v{version}_{timestamp}.zip
```

---

## 7. Eixo D — Navegação por Transações

### Campo de transação global

Presente em todas as telas via `base.html`.

- **Atalho:** `Ctrl+F5` foca o campo de qualquer tela
- **Autocomplete:** busca em código + label na API `/api/transacoes`
- **Histórico:** últimos 10 códigos usados (localStorage)
- **Enter:** navega para `/transacoes/<CODE>`

### Catálogo DS_*

| Código | Grupo | Perfil Mínimo |
|--------|-------|---------------|
| `DS_HOME` | Core | USER |
| `DS_PROJECTS` | Core | USER |
| `DS_DESIGNER` | Design | DEVELOPER |
| `DS_MENU` | Design | DEVELOPER |
| `DS_ODATA` | Integration | DEVELOPER |
| `DS_VERSIONS` | DevOps | DEVELOPER |
| `DS_BUILD` | DevOps | CORE_DEV |
| `DS_PLUGINS` | Platform | DEVELOPER |
| `DS_ADDONS` | Platform | DEVELOPER |
| `DS_AUDIT` | Admin | ADMIN |
| `DS_USERS` | Admin | ADMIN |

---

## 8. Plugins e Addons

### Plugins (NDS_*)

1. Criar pasta `plugins/<nome>/` com `plugin.json`
2. Acessar `DS_PLUGINS` → clicar **Re-escanear**
3. Plugin aparece como **inativo** — ativar manualmente

```json
// plugins/meu_plugin/plugin.json
{
  "code": "meu_plugin",
  "name": "Meu Plugin",
  "version": "1.0.0",
  "entry_point": "meu_plugin.transactions",
  "transactions": ["NDS_MEU_MODULO"]
}
```

### Addons

1. Empacotar como ZIP com `addon.json` na raiz
2. `DS_ADDONS` → **Instalar Addon** → upload do ZIP
3. Revisar o log de validação
4. Clicar **Instalar** (requer `confirmed: true`)
5. Após instalação, clicar **Ativar**

Todas as etapas são registradas em `AddonLog` — **nenhuma ação ocorre automaticamente**.

---

## 9. Referência de Rotas API

### Projetos
```
GET  /projetos                    → lista
POST /api/projetos                → criar
PUT  /api/projetos/<pid>          → atualizar
DEL  /api/projetos/<pid>          → deletar
GET  /api/projetos/<pid>/exportar-zip
```

### Páginas
```
GET  /api/projetos/<pid>/paginas
POST /api/projetos/<pid>/paginas
GET  /api/paginas/<pgid>?snapshot=1
PUT  /api/paginas/<pgid>
DEL  /api/paginas/<pgid>
POST /api/paginas/<pgid>/salvar
POST /api/paginas/<pgid>/duplicar
GET  /api/paginas/<pgid>/exportar-html
```

### Componentes
```
POST /api/paginas/<pgid>/componentes
PUT  /api/componentes/<cid>
DEL  /api/componentes/<cid>
PUT  /api/componentes/<cid>/eventos
PUT  /api/componentes/<cid>/regras
```

### OData
```
GET  /api/projetos/<pid>/odata-connections
POST /api/projetos/<pid>/odata-connections
DEL  /api/odata-connections/<cid>
POST /api/odata-connections/<cid>/testar
GET  /api/odata-connections/<cid>/entidades
POST /api/odata-connections/<cid>/gerar-tela
```

### Versões
```
GET  /api/paginas/<pgid>/versoes
POST /api/paginas/<pgid>/versoes
GET  /api/versoes/<vid>
POST /api/versoes/<vid>/restaurar
DEL  /api/versoes/<vid>
GET  /api/versoes/diff?a=<vid>&b=<vid>
GET  /api/paginas/<pgid>/versoes/sugestoes-purga
POST /api/projetos/<pid>/reset
GET  /api/versoes/backups/<pid>
GET  /api/versoes/backups/<bid>/download
```

### Plugins e Addons
```
GET  /api/plugins
GET  /api/plugins/<code>
POST /api/plugins/<code>/ativar
POST /api/plugins/<code>/desativar
POST /api/plugins/redescobrir

GET  /api/addons
POST /api/addons/upload
POST /api/addons/<code>/instalar
POST /api/addons/<code>/ativar
POST /api/addons/<code>/desativar
DEL  /api/addons/<code>
GET  /api/addons/<code>/logs
```

### Build
```
POST /api/build/run-tests
GET  /api/build/status
POST /api/build/create-zip
GET  /api/build/logs
GET  /api/build/logs/<bid>
GET  /api/build/zip/<bid>/download
```

### Transações
```
GET  /api/transacoes?q=<busca>
GET  /api/transacoes/<code>
GET  /transacoes/<CODE>            → navega para a tela
```

---

## 10. Testes

```bash
# Suite completa
python -m pytest tests/ -v

# Por módulo
python -m pytest tests/test_smoke.py       -v   # Rotas core
python -m pytest tests/test_odata.py       -v   # Integração OData
python -m pytest tests/test_versioning.py  -v   # Versionamento
python -m pytest tests/test_transactions.py -v  # Navegação
```

**Resultado esperado: 58 passed**

Fixtures disponíveis em `tests/conftest.py`:
- `app` — aplicação Flask com SQLite em memória
- `client` — test client HTTP
- `project_id` — ID do projeto de teste
- `page_id` — ID da página de teste
- `odata_conn_id` — ID da conexão OData de teste (se existir)
