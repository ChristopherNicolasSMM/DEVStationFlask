# CHANGELOG — DevStation Builder

## [3.0.4] — 2026-05-08

### Corrigido
- **Preview**: Botão Preview abria download `.html`; agora abre `preview.html` inline em nova aba com estilo do sistema (barra azul, Bootstrap, indicadores OData)
- **Rotas duplicadas**: `export_html` e `export_zip` estavam duplicados no `export_controller.py`, causando `AssertionError` no Flask durante os testes de versioning
- **OData — formulário sem campos**: `grp_h` calculava altura com base no total de campos; corrigido para usar número de **linhas** (`ceil(fields/cols)`), gerando groupboxes com tamanho proporcional correto
- **OData — largura proporcional**: Colunas de campo tinham largura fixa de 260px; agora calculadas proporcionalmente ao `canvas_w` do projeto (~610px por coluna em canvas 1280px)
- **Drag de componentes existentes**: Elementos filhos (`<button>`, `<input>`) consumiam `mousedown` antes do container. Adicionado overlay transparente com `z-index:5` sobre cada componente; conteúdo interno com `pointer-events:none`
- **Toolbar não funcional**: `btnUndo`, `btnRedo`, `btnGrid`, `btnSnap` não tinham listeners em `_bindToolbar()`; todos vinculados e funcionais agora
- **OData modal no Designer**: `ODataPanel.openNewConnModal()` chamava `new bootstrap.Modal()` mas Bootstrap Bundle não está carregado no Designer; substituído por `modal.style.display = 'flex'`
- **Dashboard modal sempre aberto**: `style="display:none;...display:flex"` no mesmo atributo — CSS usa último valor; removido o `display:flex` do markup

### Adicionado
- **Rota `/designer/<pid>/preview/<pgid>`**: Preview inline com template `preview.html` usando Bootstrap 5.3, indicadores visuais de OData binding e botão de volta ao Designer
- **OData Binding UI melhorado**: Painel Dados com status visual (verde/laranja), texto explicativo, campo de seleção de campo individual, botão ✕ para remover binding
- **OData Screen Generator**: Lista gerada inclui heading + botão Novo + campo de busca + DataGrid + paginação. Formulário inclui botões Salvar/Cancelar
- **`generateScreen` interativo**: Solicita nome da página via prompt, oferece navegar para a nova página após geração
- **`_loadEntitiesForSelect` melhorado**: Carrega campos da entidade para seleção de `field_binding`; exibe tipo de cada campo (TEXT, NUMBER, etc.)
- **`clearBinding()`**: Botão ✕ para remover binding OData de um componente
- Documentação completa: `MANUAL_USUARIO.md`, `GUIA_RAPIDO.md`, `REFERENCIA_API.md`

---

## [3.0.3] — 2026-05-08

### Corrigido — OData
- Descoberta de `$metadata` reescrita com cadeia de fallback inteligente
- Fase 1: extrai `@odata.context` da resposta do servidor e tenta `{ctx_base}.json`
- Fase 2: tenta `$metadata.json`, `%24metadata.json`, `metadata.json`
- Fase 3: variantes XML sem `.json`
- Parser automático: detecta se resposta é JSON ou XML antes de processar
- Parse de XML EDMX via `xml.etree.ElementTree` com suporte a namespaces
- Mapeamento completo `Edm.*` → tipo DSB (`TEXT`, `NUMBER`, `DATE`, `BOOLEAN`)

### Corrigido — Designer
- Adicionado overlay transparente sobre componentes (fix drag principal)
- Toolbar completa: undo/redo/grid/snap com feedback visual (fundo azul quando ativo)
- `designer.js` criado do zero com engine de canvas completa

---

## [3.0.2] — 2026-05-07

### Corrigido
- `ODataPanel.openNewConnModal()`: substituído `bootstrap.Modal` por JS puro
- `VersionPanel.openCreateModal()` e `showPurgeSuggestions()`: mesma correção
- `dashboard.html`: `style="display:none;...display:flex"` no mesmo atributo causava abertura automática do modal
- Adicionado `var _modalOpen = false` que estava faltando após o `str_replace`

### Adicionado
- `static/js/designer.js`: engine completa de canvas com drag, resize, seleção, preview por tipo, outline, zoom, undo/redo, atalhos de teclado
- Rota `/designer/<pid>/<pgid>` para navegação entre páginas

---

## [3.0.1] — 2026-05-07

### Corrigido
- Rotas de navegação entre páginas no Designer

---

## [3.0.0] — 2026-05-05

### Adicionado — Eixo A (OData)
- Model `ODataConnection` com cache de `$metadata.json` (TTL 5 min)
- `ODataConnectionManager` — HTTP client com suporte a none/basic/bearer
- `ODataScreenGenerator` — gera páginas a partir de UIAnnotations
- Aba OData no painel esquerdo do Designer
- Aba Dados (4ª aba direita) para binding de componentes
- Runtime `DSB.odata` injetado no HTML exportado

### Adicionado — Eixo B (Versionamento)
- Model `PageVersion` com soft-delete e sugestão de purga
- Model `VersionBackup` — log imutável de cada `.dsk` gerado
- Auto-snapshot a cada `save_page`
- Snapshots: `odata-gen`, `pre-restore`, `pre-reset` com tags automáticas
- Purga NUNCA automática — apenas sugestão ao usuário
- Backup `.dsk` obrigatório antes de qualquer exclusão
- Aba Histórico no painel esquerdo do Designer

### Adicionado — Eixo C (Build)
- `BuildLog` model com output pytest e metadados do ZIP
- Pipeline assíncrono via thread + polling
- `DS_BUILD` — tela com histórico, output e download de ZIPs

### Adicionado — Eixo D (Navegação)
- 11 transações `DS_*` seedadas no banco
- Campo de transação global em todas as telas (`Ctrl+F5`)
- `DS_HOME` substitui dashboard: launchpad com abas
- `DS_PLUGINS` com descoberta automática + ativação manual
- `DS_ADDONS` com pipeline de instalação confirmada e log imutável
- `transaction_nav.js` — autocomplete, histórico localStorage, launchpad

---

## [2.2.0] — 2025 (baseline v2.2)

- Designer visual drag & drop completo
- 36 componentes em 7 grupos via `ComponentRegistry`
- Layers Panel, multi-select, rubber-band selection
- Template gallery (5 templates), responsive preview
- Event editor e rules editor
- Code export generators (HTML/CSS/JS standalone)
- `base.html` totalmente self-contained (sem dependência NiceAdmin)
- Suite de 16 documentos Mermaid em `docs/`
