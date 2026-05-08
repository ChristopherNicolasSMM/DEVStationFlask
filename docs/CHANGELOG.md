# CHANGELOG — DevStation Builder

## [3.0.0] — 2026-05-05

### Adicionado — Eixo A (OData)
- Model `ODataConnection` com cache de `$metadata.json` (TTL 5 min)
- `ODataConnectionManager` — HTTP client OData com suporte a none/basic/bearer
- `ODataScreenGenerator` — gera páginas (listagem + formulário) a partir de UIAnnotations
- Aba **OData** no painel esquerdo do Designer com lista de conexões e entidades
- Aba **Dados** (4ª aba direita) para binding de componentes a endpoints OData
- Runtime `DSB.odata` injetado no HTML exportado quando binding está configurado
- `window.DSB_ODATA_CONFIG.baseUrl` configurável no ZIP exportado
- 5 novos endpoints REST `/api/odata-connections/...`

### Adicionado — Eixo B (Versionamento)
- Model `PageVersion` — snapshot completo de página com suporte a soft-delete
- Model `VersionBackup` — registro imutável de cada arquivo `.dsk` gerado
- `versioning/snapshot.py` — criação de snapshots automáticos e nomeados
- `versioning/diff_engine.py` — comparação entre dois snapshots
- Snapshot automático a cada `save_page` (Ctrl+S no Designer)
- Snapshot marcado com tag `odata-gen` ao gerar tela via OData
- Sugestão de purga quando acumulam mais de 10 auto-snapshots por página — **nunca automático**
- Ao deletar versão: gera `.dsk` obrigatoriamente antes, registra em `VersionBackup`
- Snapshot `pre-restore` criado automaticamente antes de qualquer restauração
- Snapshot `pre-reset` criado antes de reset de projeto
- Aba **Histórico** (`bi-clock-history`) no painel esquerdo do Designer
- API completa: criar, listar, diff, restaurar, deletar, download `.dsk`

### Adicionado — Eixo C (Build)
- `BuildLog` model com resultado de pytest e metadados do ZIP
- `POST /api/build/run-tests` — execução assíncrona do pytest via thread
- `POST /api/build/create-zip` — ZIP de distribuição (requer build verde)
- `DS_BUILD` — tela de pipeline com histórico de builds e download de ZIPs
- Suite de 58 testes cobrindo todos os módulos

### Adicionado — Eixo D (Navegação)
- Model `Transaction` com catálogo seed de 11 transações `DS_*`
- `transactions/registry.py` — seed automático + descoberta de plugins
- Campo de transação no header de todas as telas com autocomplete
- Atalho global `Ctrl+F5` para focar o campo de transação
- `DS_HOME` — substitui dashboard: launchpad com abas Transações/Projetos/Plugins/Addons
- `transaction_nav.js` — autocomplete, histórico localStorage, renderização do launchpad
- `DS_PLUGINS` — lista plugins descobertos, ativa/desativa com confirmação
- `DS_ADDONS` — upload, instalação passo a passo, ativação, log imutável
- Plugins escaneados de `plugins/` registrados no banco (inativos por padrão)
- Addons nunca instalados automaticamente — cada passo requer `confirmed: true`
- Rota `GET /transacoes/<CODE>` com handlers para cada transação nativa

### Alterado
- `save_page` agora gera auto-snapshot após cada salvamento
- `dashboard.html` substituído por `DS_HOME` com launchpad multi-aba
- `base.html` agora inclui campo de transação global e transaction_nav.js
- `DEFAULT_MAIN_MENU` atualizado com entradas para DS_MENU e DS_BUILD
- `DEFAULT_SIDEBAR` atualizado com abas OData e Histórico

---

## [2.2.0] — 2025 (baseline)

- Designer visual drag & drop completo
- 36 componentes em 7 grupos
- Layers Panel, multi-select, rubber-band
- Template gallery, responsive preview
- Event editor, rules editor
- Code export generators (HTML/CSS/JS)
- `base.html` totalmente self-contained (sem dependência NiceAdmin)
- Suite de documentação Mermaid em `docs/`
