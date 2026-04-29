# 09 · Fluxos de Uso

> 📍 [Início](./README.md) › Fluxos de Uso

---

## 🔄 Fluxo 1 — Criar Projeto e Primeira Página

```mermaid
sequenceDiagram
    actor Dev as Developer
    participant Browser
    participant Flask
    participant DB as SQLite

    Dev->>Browser: Acessa http://localhost:5000
    Browser->>Flask: GET /
    Flask->>DB: Project.query.order_by(updated_at.desc())
    DB-->>Flask: []  (nenhum projeto)
    Flask-->>Browser: dashboard.html (empty state)

    Dev->>Browser: Clica "Criar Primeiro Projeto"
    Browser->>Browser: Abre modal #modalNovoProjeto
    Dev->>Browser: Digita "CRM Clientes" + Enter
    Browser->>Flask: POST /projetos/novo {name: "CRM Clientes"}
    Flask->>DB: INSERT Project
    Flask->>DB: INSERT Page (home, is_home=True)
    Flask->>DB: INSERT Menu (main + sidebar padrão)
    DB-->>Flask: IDs gerados
    Flask-->>Browser: {id: 1, name: "CRM Clientes"}
    Browser->>Browser: window.location.href = '/designer/1'
    Browser->>Flask: GET /designer/1
    Flask-->>Browser: 302 → /designer/1/1
    Browser->>Flask: GET /designer/1/1
    Flask-->>Browser: designer.html com canvas vazio
```

---

## 🔄 Fluxo 2 — Aplicar Template e Personalizar

```mermaid
sequenceDiagram
    actor Dev as Developer
    participant UI as Designer UI
    participant JS as designer.js
    participant Flask
    participant DB as SQLite

    Dev->>UI: Clica botão "Templates"
    UI->>JS: TemplateGallery.open()
    JS->>Flask: GET /api/templates
    Flask-->>JS: [{id, name, description, comp_count}...]
    JS->>UI: Renderiza galeria com 5 cards

    Dev->>UI: Clica "Aplicar" no card "Dashboard KPI"
    UI->>JS: btn-apply-tpl click
    JS->>Flask: POST /api/templates/dashboard_kpi/aplicar/1
    Flask->>DB: DELETE components (página 1)
    Flask->>DB: INSERT 10 componentes do template
    Flask->>DB: UPDATE page (canvas_bg, canvas_w, canvas_h)
    DB-->>Flask: OK
    Flask-->>JS: {ok:true, comp_added:10, canvas_bg:"#f6f9ff"...}
    JS->>Flask: GET /api/paginas/1  (recarrega)
    Flask-->>JS: {components:[...10 comps...]}
    JS->>JS: DesignerState.load(data)
    JS->>UI: CanvasManager.renderAll() — exibe dashboard no canvas
    UI-->>Dev: Template aplicado

    Dev->>UI: Clica no componente "kpiReceita"
    JS->>JS: DesignerCtrl.select('kpiReceita_uid')
    JS->>UI: PropsPanel.load(comp) — exibe propriedades
    Dev->>UI: Altera "title" para "Faturamento Total"
    JS->>JS: comp.properties.title = "Faturamento Total"
    JS->>UI: CanvasManager.renderOne(comp) — atualiza visual
    Dev->>UI: Ctrl+S
    JS->>Flask: POST /api/paginas/1/salvar {components:[...]}
    Flask->>DB: upsert componentes
    Flask-->>JS: {ok:true, saved_at:"14:30:00"}
    JS->>UI: "✓ Salvo 14:30:00"
```

---

## 🔄 Fluxo 3 — Adicionar Regra de Validação

```mermaid
sequenceDiagram
    actor Dev as Developer
    participant UI as Designer UI
    participant JS as designer.js
    participant Flask

    Dev->>UI: Seleciona componente txtEmail
    JS->>UI: Atualiza todos os painéis
    Dev->>UI: Clica aba ⚙ Regras no painel direito
    Dev->>UI: Clica "+ Adicionar Regra"
    JS->>Flask: GET /api/regras/tipos  (se ainda não carregado)
    Flask-->>JS: [{group:"Validação", rules:[...]}]
    JS->>UI: Abre modal #modalAddRule com select populado

    Dev->>UI: Seleciona "Formato E-mail" no dropdown
    JS->>UI: _buildRuleParams() — renderiza campo "Mensagem"
    Dev->>UI: Preenche "Por favor, insira um e-mail válido."
    Dev->>UI: Clica "Salvar Regra"
    JS->>JS: comp.rules.push({type:"email", params:{message:"..."}})
    JS->>UI: _renderList(comp) — exibe regra na lista
    JS->>JS: DesignerState.dirty = true

    Dev->>UI: Ctrl+S
    JS->>Flask: POST /api/paginas/1/salvar
    Flask-->>JS: {ok:true}
    Note over Dev,Flask: No HTML exportado, DSB.rules.email(el, msg)\né chamado no onBlur do campo
```

---

## 🔄 Fluxo 4 — Multi-Seleção e Alinhamento

```mermaid
sequenceDiagram
    actor Dev as Developer
    participant Canvas as Canvas DOM
    participant JS as MultiSelect + DesignerCtrl

    Dev->>Canvas: Clica no botão btnSalvar
    JS->>JS: DesignerCtrl.select('btnSalvar_uid')
    Note over Dev: Quer selecionar mais 2 componentes

    Dev->>Canvas: Shift+Click em txtNome
    JS->>JS: MultiSelect.add('txtNome_uid')
    JS->>JS: DesignerCtrl.deselect()
    JS->>Canvas: Aplica .multi-selected nos 2 itens
    JS->>JS: _refreshBadge() — badge aparece "2 selecionados"

    Dev->>Canvas: Shift+Click em txtEmail
    JS->>JS: MultiSelect.add('txtEmail_uid')
    JS->>Canvas: Aplica .multi-selected nos 3 itens
    JS->>JS: _refreshBadge() — badge "3 selecionados"

    Dev->>Canvas: Clica ⊞ (alinhar centro) no badge
    JS->>JS: MultiSelect.alignSelected('group_center')
    JS->>JS: Para cada comp: c.x = minX + (groupW - c.width)/2
    JS->>Canvas: CanvasManager.renderOne(c) × 3
    Canvas-->>Dev: Componentes centralizados horizontalmente

    Dev->>Canvas: Ctrl+S
    JS->>JS: DesignerCtrl.save()
    Note over JS: Estado persistido com novos x,y
```

---

## 🔄 Fluxo 5 — Preview Responsivo e Export

```mermaid
sequenceDiagram
    actor Dev as Developer
    participant UI as Designer UI
    participant JS as designer.js
    participant Flask
    participant ZipFile as ZIP

    Dev->>UI: Clica "Preview" (ou F5)
    JS->>JS: ResponsivePreview.open()
    JS->>JS: DesignerCtrl.save(silent=true)  — salva antes
    JS->>Flask: POST /api/paginas/1/salvar
    Flask-->>JS: {ok:true}
    JS->>UI: Abre modal fullscreen #modalResponsivePreview
    JS->>UI: Cria <iframe> com src="/projetos/1/preview/1"
    UI->>Flask: GET /projetos/1/preview/1 (no iframe)
    Flask->>Flask: HtmlGenerator.render(inline_css=True, inline_js=True)
    Flask-->>UI: HTML completo da página
    UI-->>Dev: Preview renderizado no iframe

    Dev->>UI: Clica ícone Tablet
    JS->>UI: previewFrame.style.width = "768px"
    UI-->>Dev: Layout em viewport 768px
    Dev->>UI: Clica ícone Mobile
    JS->>UI: previewFrame.style.width = "375px"
    UI-->>Dev: Layout em viewport 375px

    Dev->>UI: Fecha modal e clica "Export ZIP"
    Browser->>Flask: GET /projetos/1/exportar
    Flask->>Flask: CssGenerator.render_all()
    Flask->>Flask: JsGenerator.render_all()
    Flask->>Flask: Para cada página: HtmlGenerator.render(inline=False)
    Flask->>ZipFile: Escreve index.html, style.css, app.js, README.txt
    Flask-->>Browser: application/zip download
    Browser-->>Dev: CRM-Clientes.zip baixado
```

---

## 🔄 Fluxo 6 — Layers Panel: Reordenar Z-Index

```mermaid
sequenceDiagram
    actor Dev as Developer
    participant LayersUI as Aba Layers
    participant JS as LayersPanel
    participant State as DesignerState
    participant Canvas as Canvas DOM

    Dev->>LayersUI: Clica aba ⠿ Layers
    JS->>JS: LayersPanel.render()
    JS->>LayersUI: Exibe lista ordenada por z-index (topo primeiro)
    Note over LayersUI: [card1 z:3][btnSalvar z:2][txtNome z:1]

    Dev->>LayersUI: Arrasta "txtNome" acima de "card1"
    JS->>JS: dragstart → _dragSrcUid = 'txtNome_uid'
    JS->>JS: drop → _reorderLayers('txtNome_uid', 'card1_uid')
    JS->>State: Reordena array + reatribui z-indexes
    Note over JS,State: [txtNome z:3][card1 z:2][btnSalvar z:1]
    JS->>Canvas: CanvasManager.renderOne(c) × 3
    Canvas-->>Dev: Z-indexes atualizados no canvas

    Dev->>LayersUI: Clica 👁 em "card1"
    JS->>JS: meta.hidden = true
    JS->>Canvas: card1.style.opacity = "0.1"
    Canvas-->>Dev: card1 quase invisível (temporário, não persiste)

    Dev->>LayersUI: Duplo clique em "btnSalvar"
    JS->>LayersUI: Substitui span por input editável
    Dev->>LayersUI: Digita "btnPrincipal" + Enter
    JS->>State: comp.name = "btnPrincipal"
    JS->>Canvas: CanvasManager.renderOne(comp)
    JS->>LayersUI: LayersPanel.render()
    Canvas-->>Dev: Nome atualizado no comp-label
```

---

## 🔄 Fluxo 7 — Duplicar Página

```mermaid
sequenceDiagram
    actor Dev as Developer
    participant SidebarUI as Aba Páginas
    participant JS as PageManager
    participant Flask
    participant DB as SQLite

    Dev->>SidebarUI: Clica aba 📄 Páginas no painel esquerdo
    SidebarUI-->>Dev: Lista páginas do projeto atual

    Dev->>SidebarUI: Clica botão ⧉ (duplicar)
    JS->>JS: PageManager.initDuplicate() — btn click handler
    JS->>Flask: POST /paginas/1/duplicar
    Flask->>DB: SELECT componentes da página 1
    Flask->>DB: INSERT Page ("Cópia de Início")
    Flask->>DB: INSERT Component × N (deepcopy de properties/events/rules)
    DB-->>Flask: Nova página criada
    Flask-->>JS: {ok:true, page:{id:2, name:"Cópia de Início"}, redirect_url:"/designer/1/2"}
    JS->>Browser: window.location.href = "/designer/1/2"
    Browser->>Flask: GET /designer/1/2
    Flask-->>Browser: Designer com nova página carregada
    Browser-->>Dev: Cópia da página pronta para edição
```

---

## 🔗 Navegação

| Anterior | Próximo |
|----------|---------|
| [← Frontend Designer](./08_frontend_designer.md) | [Export & Preview →](./10_export_preview.md) |
