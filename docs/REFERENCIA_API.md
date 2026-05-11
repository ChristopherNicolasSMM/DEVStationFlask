# 📡 Referência da API REST — DevStation Builder v3.0

**Base URL:** `http://localhost:5000`  
**Formato:** JSON (Content-Type: application/json)  
**Autenticação:** não implementada na v3.0 (planejada para v4.0)

---

## Índice

- [Projetos](#projetos)
- [Páginas](#páginas)
- [Componentes](#componentes)
- [Menus](#menus)
- [OData](#odata)
- [Versões e Backups](#versões-e-backups)
- [Transações](#transações)
- [Plugins](#plugins)
- [Addons](#addons)
- [Build](#build)
- [Preview e Export](#preview-e-export)

---

## Projetos

### Listar projetos
```
GET /projetos
```
```json
[
  {
    "id": 1,
    "name": "Portal de Clientes",
    "canvas_w": 1280,
    "canvas_h": 900,
    "canvas_bg": "#ffffff",
    "page_count": 3,
    "created_at": "08/05/2026 14:30",
    "updated_at": "08/05/2026 16:45"
  }
]
```

### Criar projeto
```
POST /api/projetos
```
**Body:**
```json
{
  "name":        "Portal de Clientes",
  "description": "Sistema de gestão de clientes",
  "canvas_w":    1280,
  "canvas_h":    900,
  "canvas_bg":   "#ffffff"
}
```
**Retorno:** `201 Created` com o projeto criado.

### Atualizar projeto
```
PUT /api/projetos/{pid}
```
**Body:** qualquer subconjunto dos campos acima.

### Deletar projeto
```
DELETE /api/projetos/{pid}
```
```json
{"ok": true}
```

### Abrir Designer
```
GET /designer/{pid}
GET /designer/{pid}/{pgid}
```
Renderiza a interface HTML do DS_DESIGNER.

---

## Páginas

### Listar páginas de um projeto
```
GET /api/projetos/{pid}/paginas
```
```json
[
  {
    "id": 1, "project_id": 1, "name": "Início",
    "slug": "index", "is_home": true, "order": 0,
    "canvas_w": 1280, "canvas_h": 900, "canvas_bg": "#ffffff"
  }
]
```

### Criar página
```
POST /api/projetos/{pid}/paginas
```
**Body:**
```json
{
  "name":    "Lista de Clientes",
  "slug":    "clientes-lista",
  "is_home": false
}
```

### Obter página com componentes
```
GET /api/paginas/{pgid}
```
Adicione `?snapshot=1` para incluir apenas metadados sem componentes.

```json
{
  "id": 2, "name": "Lista de Clientes",
  "components": [
    {
      "id": 10, "type": "heading", "name": "hdgLista",
      "x": 24, "y": 20, "width": 1232, "height": 52, "z_index": 1,
      "properties": {"text": "Lista de Clientes", "font_size": 26},
      "events": {},
      "rules": []
    }
  ]
}
```

### Atualizar metadados da página
```
PUT /api/paginas/{pgid}
```
**Body:** `name`, `title`, `slug`, `is_home`, `canvas_w`, `canvas_h`, `canvas_bg`

### Salvar componentes da página
```
POST /api/paginas/{pgid}/salvar
```
**Body:**
```json
{
  "author": "usuario",
  "canvas_w": 1280,
  "canvas_h": 900,
  "canvas_bg": "#ffffff",
  "components": [
    {
      "id": 10,
      "type": "heading",
      "name": "hdgPrincipal",
      "x": 24, "y": 20, "width": 500, "height": 52,
      "z_index": 1,
      "properties": {"text": "Meu Título"},
      "events": {},
      "rules": []
    }
  ]
}
```
**Retorno:**
```json
{"ok": true, "page": {...}}
```
> Também cria um **auto-snapshot** da versão anterior ao salvar.

### Duplicar página
```
POST /api/paginas/{pgid}/duplicar
```
Cria cópia completa da página (com todos os componentes) com nome `{original} (cópia)`.

### Deletar página
```
DELETE /api/paginas/{pgid}
```
> Não é possível deletar a página marcada como `is_home`.

---

## Componentes

### Adicionar componente
```
POST /api/paginas/{pgid}/componentes
```
**Body:**
```json
{
  "type":       "button",
  "name":       "btnSalvar",
  "x": 24, "y": 500, "width": 140, "height": 40,
  "properties": {"text": "Salvar", "variant": "primary"},
  "events":     {},
  "rules":      []
}
```

### Atualizar componente
```
PUT /api/componentes/{cid}
```
**Body:** qualquer subconjunto dos campos: `type`, `name`, `x`, `y`, `width`, `height`, `z_index`, `properties`, `events`, `rules`

### Salvar eventos
```
PUT /api/componentes/{cid}/eventos
```
**Body:**
```json
{
  "onClick": "DSB.toast('Clicado!', 'success');",
  "onDoubleClick": "window.location.href = '/clientes';"
}
```

### Salvar regras
```
PUT /api/componentes/{cid}/regras
```
**Body:**
```json
[
  {
    "id": "obrigatorio",
    "params": {"message": "Campo obrigatório."}
  },
  {
    "id": "email",
    "params": {"message": "E-mail inválido."}
  }
]
```

### Deletar componente
```
DELETE /api/componentes/{cid}
```

---

## Menus

### Listar menus do projeto
```
GET /api/projetos/{pid}/menus
```
```json
[
  {"id": 1, "project_id": 1, "type": "main",    "config": {...}},
  {"id": 2, "project_id": 1, "type": "sidebar", "config": {...}}
]
```

### Atualizar menu
```
PUT /api/menus/{mid}
```
**Body:**
```json
{
  "config": {
    "arquivo": {
      "label": "Arquivo", "ordem": 1,
      "items": [
        {"label": "Salvar", "shortcut": "Ctrl+S", "action": "save"}
      ]
    }
  }
}
```

---

## OData

### Listar conexões do projeto
```
GET /api/projetos/{pid}/odata-connections
```
```json
[
  {
    "id": 1,
    "project_id": 1,
    "name": "Servidor de Clientes",
    "base_url": "http://localhost:8000/odata/",
    "auth_type": "none",
    "has_metadata_cache": true,
    "metadata_cached_at": "08/05/2026 15:00:00"
  }
]
```

### Criar conexão
```
POST /api/projetos/{pid}/odata-connections
```
**Body:**
```json
{
  "name":       "Servidor de Clientes",
  "base_url":   "http://localhost:8000/odata/",
  "auth_type":  "none",
  "auth_value": null
}
```
Valores para `auth_type`: `none` | `bearer` | `basic`  
Para `basic`: `auth_value` = `"usuario:senha"`  
Para `bearer`: `auth_value` = `"meu-token-aqui"`

### Testar conexão
```
POST /api/odata-connections/{cid}/testar
```
**Retorno sucesso:**
```json
{
  "ok": true,
  "entities_count": 3,
  "source_format": "json",
  "message": "3 entidade(s) encontrada(s) (formato: json)"
}
```
**Retorno falha:**
```json
{
  "ok": false,
  "error": "Não foi possível encontrar o $metadata..."
}
```

### Listar entidades disponíveis
```
GET /api/odata-connections/{cid}/entidades
```
```json
[
  {
    "name":   "Customers",
    "label":  "Clientes",
    "fields": [
      {"name": "CustomerID",  "label": "ID",     "type": "TEXT",   "required": true},
      {"name": "CompanyName", "label": "Empresa", "type": "TEXT",   "required": true, "max_length": 100},
      {"name": "Country",     "label": "País",   "type": "TEXT"},
      {"name": "IsActive",    "label": "Ativo",  "type": "BOOLEAN"}
    ],
    "ui": {
      "list_view": {
        "columns": [{"field": "CustomerID", "label": "ID"}, ...],
        "default_sort": "CompanyName asc"
      },
      "form": {
        "groups": [
          {"label": "Identificação", "fields": [...]}
        ]
      }
    }
  }
]
```

### Gerar tela automaticamente
```
POST /api/odata-connections/{cid}/gerar-tela
```
**Body:**
```json
{
  "entity":    "Customers",
  "mode":      "both",
  "page_name": "Clientes"
}
```
`mode`: `list` | `form` | `both`

**Retorno:**
```json
{
  "ok": true,
  "pages": [
    {"id": 5, "name": "Clientes — Lista",       "slug": "clientes-lista"},
    {"id": 6, "name": "Clientes — Formulário",  "slug": "clientes-formulario"}
  ]
}
```

### Deletar conexão
```
DELETE /api/odata-connections/{cid}
```

---

## Versões e Backups

### Listar versões de uma página
```
GET /api/paginas/{pgid}/versoes
GET /api/paginas/{pgid}/versoes?deleted=1    ← inclui deletadas
```
```json
[
  {
    "id": 12,
    "page_id": 2,
    "version_label": "sprint-3",
    "description": "Entrega do sprint 3",
    "author": "usuario",
    "is_auto": false,
    "tags": ["sprint-3", "stable"],
    "purge_suggested": false,
    "deleted": false,
    "backup_path": null,
    "component_count": 8,
    "created_at": "08/05/2026 14:30:00"
  }
]
```

### Criar versão nomeada
```
POST /api/paginas/{pgid}/versoes
```
**Body:**
```json
{
  "label":       "v1.0-release",
  "description": "Versão aprovada pelo cliente",
  "author":      "dev@empresa.com",
  "tags":        ["stable", "v1.0"]
}
```
**Retorno:** `201 Created`

### Obter detalhe de versão
```
GET /api/versoes/{vid}
GET /api/versoes/{vid}?snapshot=1    ← inclui snapshot completo dos componentes
```

### Comparar duas versões
```
GET /api/versoes/diff?a={vid_a}&b={vid_b}
```
```json
{
  "added":          ["btnNovo", "grdLista"],
  "removed":        ["lblAntigo"],
  "changed":        ["hdgTitulo"],
  "canvas_changed": false,
  "total_changes":  4,
  "version_a": {...},
  "version_b": {...}
}
```

### Restaurar versão
```
POST /api/versoes/{vid}/restaurar
```
**Body:**
```json
{"triggered_by": "usuario"}
```
**Retorno:**
```json
{
  "ok": true,
  "pre_restore_version_id": 45
}
```

### Deletar versão (gera .dsk obrigatório)
```
DELETE /api/versoes/{vid}
```
**Body:**
```json
{"triggered_by": "usuario"}
```
**Retorno:**
```json
{
  "ok": true,
  "backup_name": "version_page2_sprint-3_20260508_143022.dsk",
  "backup_path": "/home/.../dist/backups/version_page2_sprint-3_20260508_143022.dsk",
  "size_bytes": 4096
}
```

### Versões sugeridas para purga
```
GET /api/paginas/{pgid}/versoes/sugestoes-purga
```
Retorna versões automáticas antigas marcadas com `purge_suggested: true`.

### Reset de projeto
```
POST /api/projetos/{pid}/reset
```
**Body:**
```json
{
  "triggered_by": "usuario",
  "pages": [
    {"page_id": 1, "version_id": 12},
    {"page_id": 2, "version_id": 18}
  ]
}
```
**Retorno:**
```json
{
  "ok": true,
  "results": [
    {"page_id": 1, "version_id": 12, "ok": true, "pre_restore_version_id": 51},
    {"page_id": 2, "version_id": 18, "ok": true, "pre_restore_version_id": 52}
  ]
}
```

### Listar backups .dsk
```
GET /api/versoes/backups/{project_id}
```

### Baixar backup .dsk
```
GET /api/versoes/backups/{bid}/download
```
Retorna o arquivo `.dsk` como download.

---

## Transações

### Listar transações ativas
```
GET /api/transacoes
GET /api/transacoes?q=designer          ← busca por código ou label
GET /api/transacoes?active=0            ← inclui inativas
```
```json
[
  {
    "id": 1,
    "code": "DS_DESIGNER",
    "label": "Visual Designer",
    "group": "Design",
    "description": "Editor visual drag & drop",
    "icon": "bi-layout-wtf",
    "route": "/designer/{pid}",
    "min_profile": "DEVELOPER",
    "is_active": true,
    "is_standard": true,
    "plugin_code": null
  }
]
```

### Detalhe de uma transação
```
GET /api/transacoes/{code}
```

### Navegar para transação (HTML)
```
GET /transacoes/{code}
```
Renderiza a tela correspondente ou retorna 404 com template `404_tx.html`.

---

## Plugins

### Listar plugins
```
GET /api/plugins
```
```json
[
  {
    "id": 1,
    "code": "fraterlink",
    "name": "FraterLink",
    "version": "1.0.0",
    "is_active": false,
    "is_installed": true,
    "transaction_codes": ["NDS_FRATER_MEMBRO"],
    "discovered_at": "08/05/2026 14:00"
  }
]
```

### Ativar plugin
```
POST /api/plugins/{code}/ativar
```
**Body:**
```json
{
  "confirmed":    true,
  "triggered_by": "usuario"
}
```
> `confirmed: true` é **obrigatório** — plugin nunca é ativado automaticamente.

### Desativar plugin
```
POST /api/plugins/{code}/desativar
```
**Body:** `{"triggered_by": "usuario"}`

### Re-escanear pasta plugins/
```
POST /api/plugins/redescobrir
```
Escaneia `plugins/` e registra novos plugins como inativos.

---

## Addons

### Listar addons
```
GET /api/addons
```

### Detalhe com log
```
GET /api/addons/{code}
```
Inclui campo `logs` com histórico completo de ações.

### Upload de pacote
```
POST /api/addons/upload
Content-Type: multipart/form-data

file:          arquivo.zip
triggered_by:  usuario
```
**Retorno:** `201 Created` com addon em status `available`.

### Instalar addon
```
POST /api/addons/{code}/instalar
```
**Body:**
```json
{
  "confirmed":    true,
  "triggered_by": "usuario"
}
```
> `confirmed: true` obrigatório. Executa: validate → extract → register.

### Ativar addon instalado
```
POST /api/addons/{code}/ativar
```
**Body:** `{"confirmed": true, "triggered_by": "usuario"}`

### Desativar addon
```
POST /api/addons/{code}/desativar
```

### Remover addon
```
DELETE /api/addons/{code}
```
**Body:** `{"confirmed": true, "triggered_by": "usuario"}`

### Log de ações
```
GET /api/addons/{code}/logs
```
```json
[
  {
    "id": 1,
    "addon_code": "ds-charts-pro",
    "action": "upload_package",
    "status": "success",
    "detail": "Pacote arquivo.zip recebido.",
    "triggered_by": "usuario",
    "created_at": "08/05/2026 14:30:00"
  }
]
```

---

## Build

### Executar testes (assíncrono)
```
POST /api/build/run-tests
```
**Body:** `{"triggered_by": "usuario"}`  
**Retorno imediato:**
```json
{"ok": true, "build_id": 5, "status": "running"}
```
Faça polling em `GET /api/build/logs/{build_id}` para acompanhar.

### Status do último build
```
GET /api/build/status
```
```json
{
  "ok": true,
  "build": {
    "id": 5, "status": "passed",
    "tests_total": 58, "tests_passed": 58, "tests_failed": 0,
    "duration_seconds": 1,
    "zip_name": "devstation_builder_v3.0.4_20260508.zip",
    "started_at": "08/05/2026 15:00:00",
    "finished_at": "08/05/2026 15:00:01"
  }
}
```

### Gerar ZIP de distribuição
```
POST /api/build/create-zip
```
**Body:**
```json
{
  "triggered_by": "usuario",
  "force": false
}
```
`force: true` gera mesmo com build falhado (não recomendado para produção).

**Retorno:**
```json
{
  "ok": true,
  "zip_name": "devstation_builder_v3.0.4_20260508.zip",
  "size_bytes": 118067
}
```

### Histórico de builds
```
GET /api/build/logs
GET /api/build/logs?limit=10
GET /api/build/logs/{bid}        ← com test_output completo
```

### Baixar ZIP de um build
```
GET /api/build/zip/{bid}/download
```

---

## Preview e Export

### Preview inline (nova aba, estilo do sistema)
```
GET /designer/{pid}/preview/{pgid}
```
Renderiza `preview.html` com Bootstrap, barra de preview e dados OData carregados.

### Export HTML individual (download)
```
GET /api/paginas/{pgid}/exportar-html
```
Baixa a página como `.html` standalone com Bootstrap via CDN.

### Export ZIP do projeto
```
GET /api/projetos/{pid}/exportar-zip
```
Baixa todas as páginas do projeto em um único `.zip`.

---

## Códigos de Status HTTP

| Código | Significado |
|--------|-------------|
| `200 OK` | Sucesso |
| `201 Created` | Recurso criado com sucesso |
| `400 Bad Request` | Parâmetros inválidos ou faltando |
| `404 Not Found` | Recurso não encontrado |
| `409 Conflict` | Conflito (ex: addon já registrado) |
| `500 Internal Server Error` | Erro interno (ver logs do servidor) |
| `502 Bad Gateway` | Erro ao acessar servidor OData externo |

---

## Modelos de Dados

### Component.properties — Exemplo completo (Binding OData)

```json
{
  "text":        "Gráfico de Vendas",
  "font_size":   13,
  "text_color":  "#333333",
  "odata": {
    "connection_id": 1,
    "entity":        "SalesOrders",
    "mode":          "list",
    "filter":        "Year eq 2026",
    "orderby":       "TotalAmount desc",
    "select":        "OrderID,Customer,TotalAmount,Date",
    "page_size":     50,
    "field_binding": null,
    "columns":       ["OrderID", "Customer", "TotalAmount", "Date"]
  }
}
```

### PageVersion.snapshot — Estrutura do snapshot

```json
{
  "id": 2,
  "name": "Lista de Clientes",
  "canvas_w": 1280,
  "canvas_h": 900,
  "canvas_bg": "#ffffff",
  "components": [
    {
      "id": 10, "type": "heading", "name": "hdgLista",
      "x": 24, "y": 20, "width": 1232, "height": 52, "z_index": 1,
      "properties": {"text": "Lista de Clientes"},
      "events": {},
      "rules": []
    }
  ]
}
```

---

*API Reference DevStation Builder v3.0.4 — 2026*
