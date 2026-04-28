# 📋 DevStation Builder — Atualizações e Próximos Passos

> **Versão atual:** v2.1 MVC  
> **Repositório:** https://github.com/ChristopherNicolasSMM/DEVStationFlask  
> **Stack:** Flask + SQLAlchemy (SQLite) · Bootstrap 5 · interact.js · JavaScript Puro

---

## ✅ Histórico de Versões

### v1.0 — MVP Inicial
- Drag & drop básico com posicionamento absoluto no canvas
- 12 tipos de componentes (button, label, input, textarea, image, card, divider, alert, badge, icon, container)
- Salvar/carregar no SQLite
- Preview em nova aba
- Export ZIP (index.html + style.css)
- Undo/Redo (50 estados)
- Zoom (Ctrl+Scroll + botões)
- Auto-save a cada 30s
- Context menu (botão direito)
- Renomear projeto inline

---

### v2.0 — Arquitetura MVC Completa
**Entregável:** `devstation_builder_v2.0_mvc.zip`

#### Reestruturação da Arquitetura
```
dsb_v2/
├── app.py                      # Application Factory (create_app)
├── config.py                   # Configurações centralizadas
├── models/                     # Model layer (SQLAlchemy)
│   ├── project.py              # Project (id, name, canvas_w/h/bg, pages, menus)
│   ├── page.py                 # Page (multi-página por projeto)
│   ├── component.py            # Component (type, position, properties JSON, events JSON, rules JSON)
│   ├── menu.py                 # Menu (configuração JSON do menu principal e sidebar)
│   └── menu_defaults.py        # Configurações padrão dos menus
├── controllers/                # Controller layer (Flask Blueprints)
│   ├── project_controller.py   # CRUD projetos + dashboard
│   ├── page_controller.py      # CRUD páginas + designer
│   ├── component_controller.py # Catálogo + operações em componentes
│   ├── event_controller.py     # Tipos de eventos + ações disponíveis
│   ├── rule_controller.py      # Tipos de regras de negócio
│   ├── export_controller.py    # Preview HTML + Export ZIP
│   └── menu_controller.py      # Gerenciamento de menus
├── views/                      # View layer (Jinja2 templates)
│   ├── base.html               # Layout autossuficiente (sem dependência NiceAdmin)
│   ├── dashboard.html          # Grid de projetos
│   └── designer.html           # IDE visual completo
├── components/                 # Registro e definição de componentes
│   ├── base_component.py       # Classe abstrata BaseComponent
│   ├── definitions.py          # 36 componentes implementados
│   └── __init__.py             # ComponentRegistry (singleton)
├── events/                     # Sistema de eventos
│   ├── event_types.py          # 11 categorias, ~50 tipos de eventos
│   └── event_actions.py        # 23 ações pré-definidas (navegar, UI, API, timer...)
├── rules/                      # Sistema de regras de negócio
│   └── rule_types.py           # 18 tipos (validação, visibilidade, cálculo, status)
└── generators/                 # Geradores de código
    ├── html_generator.py       # HTML completo com runtime DSB embutido
    ├── css_generator.py        # CSS consolidado para export
    └── js_generator.py         # JS de eventos e regras para export
```

#### 36 Componentes Implementados
| Grupo | Componentes |
|-------|-------------|
| **Entrada** | button, textbox, textarea, numberbox, checkbox, radiobutton, combobox, switch, slider, datepicker, rating, fileupload |
| **Visualização** | label, heading, image, icon, badge, progressbar, statusbar, separator, spinner |
| **Container** | panel, card, groupbox, tabs, accordion |
| **Dados** | datagrid, chart, pagination |
| **Feedback** | alert, modal |
| **Navegação** | navbar, breadcrumb, stepper |
| **Tempo** | timer, countdown |

#### Sistema de Eventos
- `onClick`, `onDoubleClick`, `onMouseEnter`, `onMouseLeave`, `onFocus`, `onBlur`
- `onChange`, `onKeyUp`, `onKeyDown`, `onEnterPress`, `onInput`
- `onTick` (Timer), `onComplete` (Countdown/ProgressBar)
- `onRowClick`, `onCellEdit`, `onSort` (DataGrid)
- `onTabChange`, `onSectionChange` (Tabs/Accordion)
- `onOpen`, `onClose`, `onConfirm`, `onCancel` (Modal)

#### Sistema de Regras
- **Validação:** obrigatorio, min_length, max_length, email, cpf, cnpj, numero, min_valor, max_valor, data_valida
- **Visibilidade:** visivel_se, oculto_se, habilitado_se
- **Cálculo:** calcular, somar, progresso, status_map, formatar

#### Designer JS (MVC Frontend)
- `DesignerState` — Model (componentes, undo/redo, zoom, dirty flag)
- `CanvasManager` — View (renderização, interact.js drag+resize)
- `DesignerCtrl` — Controller (orquestra tudo)
- `PropsPanel`, `EventsPanel`, `RulesPanel` — painéis laterais
- `OutlinePanel`, `PagesPanel`, `MenuBar`, `KeyBindings` — módulos auxiliares
- `ContextMenu`, `PaletteDrag`, `CanvasDrop` — interações de canvas

---

### v2.1 — Features Avançadas
**Entregável:** `devstation_builder_v2.1_mvc_features.zip`

#### 🐛 Correções
- **Dashboard quebrado:** `base.html` reescrito como layout autossuficiente — nunca mais depende do NiceAdmin estar presente para funcionar. O NiceAdmin agora é um enhancement opcional.
- **Vendors locais:** `base.html` e `designer.html` agora apontam para `/static/assets/vendor/bootstrap/` e `/static/assets/vendor/bootstrap-icons/` (presentes no repo), em vez de CDN externo.

#### 🆕 Novas Funcionalidades

**1. Upload de Imagens** (`controllers/upload_controller.py`)
- Endpoint `POST /upload/imagem` — upload multipart com validação de tipo e tamanho (max 5MB)
- Endpoint `GET /upload/listar` — lista imagens disponíveis
- Endpoint `DELETE /upload/imagem/<filename>` — remove imagem
- Armazenamento em `static/uploads/` com nomes únicos (timestamp + UUID)

**2. Galeria de Templates** (`controllers/template_controller.py`)
- 5 templates prontos com componentes pré-configurados:
  - 🔐 **Formulário de Login** — campos e-mail/senha, checkbox "lembrar"
  - 📊 **Dashboard KPI** — 4 KPI cards, gráfico, progressbar, datagrid
  - 👤 **Formulário CRM** — cadastro completo com validações CPF/e-mail
  - 🚀 **Landing Page** — navbar, hero section, 3 benefícios, CTA
  - 📋 **Relatório de Status** — stepper, progress por área, tabela de tarefas
- Endpoint `GET /api/templates` — lista templates
- Endpoint `POST /api/templates/<id>/aplicar/<pgid>` — aplica na página
- Opção de manter componentes existentes

**3. Preview Responsivo** (modal fullscreen)
- Toggle de viewport: **Desktop** (1280px) · **Tablet** (768px) · **Mobile** (375px)
- Renderização via iframe com auto-save antes de exibir
- Atalho: `F5`

**4. Interface de Upload no Designer**
- Modal de gerenciamento de imagens com drag & drop
- Galeria visual com miniaturas
- Seletor integrado ao painel de propriedades do componente `image`

---

## 🗺️ Roadmap — Próximos Passos

### Sprint 3 (Prioridade Alta)

#### 1. Multi-seleção no Canvas
```
Comportamento esperado:
- Shift+Click → adiciona/remove da seleção
- Ctrl+A      → seleciona todos
- Arrastar no canvas (sem componente) → rubber band selection
- Mover, deletar, duplicar em grupo
- Propriedades em comum editáveis em lote
```

#### 2. Layers Panel
```
Interface:
- Lista todos os componentes da página atual
- Ícone do tipo, nome editável inline
- Drag para reordenar z-index
- Clique → seleciona no canvas
- Ícone de visibilidade (ocultar/mostrar temporariamente)
- Ícone de lock (impede edição acidental)
```

#### 3. Duplicate Page / Page Templates
```
Funcionalidade:
- Botão "Duplicar" na lista de páginas
- Clona todos os componentes e propriedades
- Nomeia como "Cópia de [nome]"
- Controller: POST /paginas/<pgid>/duplicar
```

---

### Sprint 4 (Prioridade Média)

#### 4. Grid/Snap Avançado
```
Melhorias no snap:
- Snap to other components (guides visuais azuis durante drag)
- Distribuição equidistante (align & distribute)
- Lock aspect ratio durante resize
- Snap edges & centers
```

#### 5. Gerador de Código Aprimorado
```
Funcionalidades:
- Modal "Ver Código" com syntax highlight
- Exportar HTML/CSS/JS em abas separadas
- Preview do código gerado em tempo real
- Opção "Bootstrap local" vs "CDN"
- Responsividade automática com breakpoints configuráveis
```

#### 6. Conectar Dados via API
```
Para o componente DataGrid:
- Propriedade "dataSource" com URL de API
- Carregamento dinâmico (fetch ao renderizar)
- Configuração de método HTTP e headers
- Mapeamento de campos da resposta JSON para colunas
```

---

### Sprint 5 (Médio/Longo Prazo)

#### 7. Integração DS_DESIGNER (DevStationPlatform)
```
Registrar o builder como transação da plataforma:
- Código: DS_DESIGNER
- Grupo: Ferramentas
- Perfil mínimo: DEVELOPER
- Integração com sistema de auditoria (DS_AUDIT)
- Salvar projetos associados a módulos NDS_*
```

#### 8. Sistema de Versões de Página
```
Git-like para páginas:
- Snapshot automático a cada save
- Histórico visual com diff de componentes
- Rollback para versão anterior
- Tag de versão (ex: "v1.0 — Aprovada pelo cliente")
```

#### 9. Componentes Avançados
```
Próximos a implementar:
- RichTextEditor (TinyMCE já está nos vendors!)
- DataChart com ApexCharts (vendor disponível no repo)
- Kanban Board
- Calendar Widget
- TreeView
- MaskedInput (CPF, CNPJ, Telefone)
- MapEmbed (iframe Google Maps)
- QRCode Generator
```

#### 10. Colaboração em Tempo Real
```
Nice to have:
- WebSocket para edição simultânea
- Indicador de quem está editando cada componente
- Chat/comentários no canvas
- Histórico de atividades
```

---

## 🔧 Como Rodar

```bash
cd dsb_v2
pip install -r requirements.txt
python app.py
# → http://localhost:5000
```

## 📁 Estrutura de Vendors Locais

O projeto já inclui em `static/assets/vendor/`:
- `bootstrap/` — Bootstrap 5.3 CSS + JS
- `bootstrap-icons/` — Bootstrap Icons (font + CSS)
- `chart.js/` — Chart.js para gráficos
- `apexcharts/` — ApexCharts (avançado)
- `echarts/` — ECharts (alternativo)
- `quill/` — Editor rich text
- `tinymce/` — TinyMCE editor (completo)
- `simple-datatables/` — Tabelas avançadas

---

## 🏗️ Padrões de Desenvolvimento

### Adicionar um novo componente
1. Criar classe em `components/definitions.py` herdando `BaseComponent`
2. Implementar: `type`, `label`, `icon`, `group`, `default_properties`, `default_size`, `render_html()`
3. Registrar em `components/__init__.py` na lista `_COMPONENTS_LIST`
4. Adicionar visual preview em `CanvasManager._buildInner()` no `designer.js`

### Adicionar um novo controller
1. Criar `controllers/meu_controller.py` com `bp = Blueprint(...)`
2. Importar e registrar em `controllers/__init__.py`

### Adicionar um novo template
1. Adicionar entrada ao `TEMPLATE_CATALOG` em `controllers/template_controller.py`
2. Nenhuma outra mudança necessária — o endpoint os serve automaticamente

---

*Documento gerado automaticamente pelo DevStation Builder CI — v2.1 MVC*

---

### v2.2 — Sprint 3: Multi-seleção, Layers Panel, Duplicate Page
**Entregável:** `devstation_builder_v2.2_sprint3.zip`

#### 🆕 Novas Funcionalidades

**1. Multi-Seleção no Canvas** (`MultiSelect` — designer.js)

| Gesto | Ação |
|-------|------|
| `Shift + Click` em componente | Adiciona/remove da seleção múltipla |
| Arrastar no vazio do canvas | Rubber-band (seleciona por área) |
| `Ctrl + A` | Seleciona todos |
| `Esc` | Limpa seleção múltipla |
| `Ctrl + D` (com seleção) | Duplica todos selecionados |
| `Delete` (com seleção) | Remove todos selecionados |
| `Setas` (com seleção) | Move grupo 2px / Shift+Setas 10px |

**Selection Badge** (barra flutuante): aparece automaticamente ao selecionar 2+ componentes com botões de:
- Duplicar grupo
- Alinhar esquerda / centro / direita (relativo ao canvas)
- Alinhar ao grupo (center, edges)
- Distribuição equidistante horizontal e vertical
- Deletar grupo
- Limpar seleção

**2. Layers Panel** (aba ⠿ no painel esquerdo)
- Lista de camadas ordenada por z-index (topo → fundo)
- **Drag & drop para reordenar z-index** dentro do painel
- **Toggle visibilidade** 👁️ — oculta temporariamente no canvas (não persiste)
- **Toggle lock** 🔒 — bloqueia drag/resize no canvas, destaca com borda laranja
- **Rename inline** — duplo clique no nome da camada
- **Highlight** — mostra seleção simples (azul) e múltipla (laranja)
- **Delete** via botão ✕ em cada linha

**3. Duplicate Page** (botão ⧉ na aba Páginas)
- Clona a página atual com todos os componentes
- Endpoint: `POST /paginas/<pgid>/duplicar`
- Nome automático: `"Cópia de <nome original>"`
- Redireciona automaticamente para a nova página após duplicação
- Usa `copy.deepcopy` para isolar propriedades/eventos/regras

#### 📁 Arquivos Modificados
- `views/designer.html` — nova aba tab-layers, rubber-band div, selection-badge, btnDupPage
- `static/js/designer.js` — +700 linhas: módulos MultiSelect, LayersPanel, PageManager
- `static/css/designer.css` — +130 linhas: rubber-band, multi-selected, layers-list, selection-badge
- `controllers/page_controller.py` — endpoint `POST /paginas/<pgid>/duplicar`

---

## 🗺️ Roadmap Atualizado

### Sprint 4 — Dados e Código (próxima)

#### 1. DataGrid com Fonte de API
- Propriedade `dataSource` (URL) no componente DataGrid
- Carregamento dinâmico com `fetch` ao preview/export
- Configuração: método HTTP, headers, mapeamento de campos JSON → colunas
- Atualização automática via componente Timer
- UI no painel de propriedades: campo URL + botão "Testar"

#### 2. Modal "Ver Código Gerado"
- Botão na toolbar: `</>` Código
- Modal com 3 abas: **HTML** · **CSS** · **JavaScript**
- Syntax highlight com `highlight.js` (CDN)
- Botão "Copiar" por aba
- Atualização em tempo real ao editar o canvas

#### 3. Snap to Components (guias inteligentes)
- Linhas guia azuis durante drag (alinha com edges e centros de outros comps)
- Lock aspect ratio durante resize (`Shift` mantido)
- Snap configurável: ativar/desativar no toolbar

### Sprint 5 — Componentes Avançados

#### 4. RichTextEditor
- Componente usando TinyMCE (já nos vendors locais!)
- Edição inline no canvas
- Export HTML com conteúdo serializado

#### 5. ApexChart Avançado
- Componente usando ApexCharts (já nos vendors locais!)
- Mais tipos: área, radial, heatmap, treemap
- Configuração visual no painel de propriedades

#### 6. MaskedInput
- Componente de entrada com máscara
- Máscaras padrão: CPF, CNPJ, Telefone, CEP, Data
- Validação integrada com sistema de regras

### Sprint 6 — Plataforma

#### 7. Integração DS_DESIGNER
- Registrar como `DS_DESIGNER` na DevStationPlatform
- Associar projetos a plugins `NDS_*`
- Auditoria via `DS_AUDIT`
- Perfil mínimo: `DEVELOPER`

#### 8. Sistema de Versões
- Snapshot automático a cada save (últimas 10 versões)
- Histórico visual com diff de componentes
- Rollback com 1 clique

