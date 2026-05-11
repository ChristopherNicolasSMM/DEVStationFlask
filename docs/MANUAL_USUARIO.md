# 📖 Manual do Usuário — DevStation Builder v3.0

**Versão:** 3.0.4  
**Plataforma:** DevStation Platform  
**Transação principal:** `DS_DESIGNER`

---

## Índice

1. [Visão Geral](#1-visão-geral)
2. [DS_HOME — Launchpad](#2-ds_home--launchpad)
3. [Navegação por Transações](#3-navegação-por-transações)
4. [DS_DESIGNER — Editor Visual](#4-ds_designer--editor-visual)
   - 4.1 [Estrutura do Designer](#41-estrutura-do-designer)
   - 4.2 [Paleta de Componentes](#42-paleta-de-componentes)
   - 4.3 [Canvas — Área de Trabalho](#43-canvas--área-de-trabalho)
   - 4.4 [Painel de Propriedades](#44-painel-de-propriedades)
   - 4.5 [Painel OData](#45-painel-odata)
   - 4.6 [Painel de Histórico](#46-painel-de-histórico)
   - 4.7 [Aba Dados — Binding OData](#47-aba-dados--binding-odata)
   - 4.8 [Preview e Exportação](#48-preview-e-exportação)
   - 4.9 [Atalhos de Teclado](#49-atalhos-de-teclado)
5. [DS_VERSIONS — Histórico de Versões](#5-ds_versions--histórico-de-versões)
6. [DS_PLUGINS — Gerenciador de Plugins](#6-ds_plugins--gerenciador-de-plugins)
7. [DS_ADDONS — Gerenciador de Addons](#7-ds_addons--gerenciador-de-addons)
8. [DS_BUILD — Build e Deploy](#8-ds_build--build-e-deploy)
9. [DS_MENU — Editor de Menu](#9-ds_menu--editor-de-menu)
10. [DS_ODATA — Gerenciador OData](#10-ds_odata--gerenciador-odata)
11. [Referência de Componentes](#11-referência-de-componentes)
12. [Boas Práticas](#12-boas-práticas)
13. [Solução de Problemas](#13-solução-de-problemas)

---

## 1. Visão Geral

O **DevStation Builder** é uma plataforma RAD (Rapid Application Development) visual que permite criar páginas e formulários completos por meio de drag & drop, com integração nativa a servidores OData V4, versionamento automático e pipeline de build integrado.

### Perfis de Acesso

| Perfil | Acesso |
|--------|--------|
| `USER` | Visualiza e executa transações |
| `PUSER` | Power User — exporta dados |
| `BANALYST` | Analista — cria workflows |
| `DEVELOPER` | Cria projetos, páginas, usa OData |
| `CORE_DEV` | Modifica transações DS_*, publica |
| `DEV_ALL` | Acesso completo de desenvolvimento |
| `ADMIN` | Administração total da plataforma |

> A maioria das funcionalidades do DS_DESIGNER requer perfil mínimo **DEVELOPER**.

---

## 2. DS_HOME — Launchpad

O DS_HOME é a tela inicial da plataforma. Acesse em: **`http://localhost:5000/`**

### Abas do Launchpad

| Aba | Descrição |
|-----|-----------|
| **Transações** | Grade de cards com todas as transações DS_* disponíveis |
| **Projetos** | Lista de projetos criados no Builder |
| **Plugins** | Plugins NDS_* ativos na plataforma |
| **Addons** | Extensões de componentes instaladas |
| **Build** | Status do último pipeline de testes |

### Criar um Novo Projeto

1. Acesse **DS_HOME** ou clique em **Novo Projeto** na barra superior
2. Informe o **nome** do projeto (ex: "Portal de Clientes")
3. Informe uma **descrição** opcional
4. Clique em **Criar Projeto**
5. O Designer abre automaticamente na nova página inicial

---

## 3. Navegação por Transações

### Campo de Transação Rápida

O campo de transação está presente em **todas as telas** do sistema, no canto superior esquerdo do header.

```
┌──────────────────────────────────────┐
│  [Transação... (Ctrl+F5)]  ›         │
└──────────────────────────────────────┘
```

**Como usar:**

1. Clique no campo ou pressione **`Ctrl+F5`** em qualquer tela
2. Digite o código da transação (ex: `DS_DESIGNER`) ou parte do nome
3. O dropdown de autocomplete exibe sugestões em tempo real
4. Pressione **`Enter`** ou clique na sugestão para navegar
5. Use **`↑ ↓`** para navegar no dropdown
6. **`Esc`** limpa o campo

**Histórico:** Os últimos 10 códigos usados aparecem ao focar o campo vazio.

### Catálogo de Transações DS_*

| Código | Descrição | Perfil |
|--------|-----------|--------|
| `DS_HOME` | Launchpad — tela inicial | USER |
| `DS_DESIGNER` | Editor visual drag & drop | DEVELOPER |
| `DS_ODATA` | Gerenciador de conexões OData | DEVELOPER |
| `DS_VERSIONS` | Histórico e restauração de versões | DEVELOPER |
| `DS_BUILD` | Pipeline de testes e build | CORE_DEV |
| `DS_PLUGINS` | Gerenciador de plugins NDS_* | DEVELOPER |
| `DS_ADDONS` | Gerenciador de addons | DEVELOPER |
| `DS_MENU` | Editor visual da barra de menus | DEVELOPER |
| `DS_AUDIT` | Console de auditoria | ADMIN |
| `DS_USERS` | Gestão de usuários e perfis | ADMIN |

---

## 4. DS_DESIGNER — Editor Visual

### Como Acessar

- No DS_HOME → clique em **Editar** num projeto existente
- Digite `DS_DESIGNER` no campo de transação
- URL direta: `/designer/{id_projeto}`

---

### 4.1 Estrutura do Designer

```
┌─────────────────────────────────────────────────────────────────────┐
│  TOOLBAR: [←] [DS_DESIGNER] [NomeProjeto] [↩][↪] [⊞][🧲] [W][H][🎨]  │
│                                    [Preview] [ZIP] [💾 Salvar]      │
├──────────────────┬─────────────────────────────────┬────────────────┤
│                  │                                 │                │
│  PAINEL ESQUERDO │         CANVAS                  │ PAINEL DIREITO │
│                  │      (Área de trabalho)         │                │
│  Abas:           │  ┌─────────────────────────┐   │ Abas:          │
│  ⊞ Componentes   │  │                         │   │ ☰ Propriedades │
│  📄 Páginas      │  │  Arraste componentes    │   │ ⚡ Eventos      │
│  ≡ Outline       │  │  para cá                │   │ ≡ Regras       │
│  ☁ OData         │  │                         │   │ 🗄 Dados OData  │
│  🕐 Histórico    │  └─────────────────────────┘   │                │
│                  │                                 │                │
└──────────────────┴─────────────────────────────────┴────────────────┘
                        [– 100% +  ⊞] (Zoom HUD)
```

---

### 4.2 Paleta de Componentes

A paleta fica na aba **⊞ Componentes** do painel esquerdo.

**Para adicionar ao canvas:** arraste o componente desejado para a área de trabalho.

#### Grupos de Componentes

**Entrada**
| Componente | Descrição |
|------------|-----------|
| Botão | Ação primária, secundária ou perigo |
| Campo Texto | Input de texto simples ou tipado |
| Área de Texto | Textarea multilinha |
| Campo Número | Input numérico com min/max/step |
| ComboBox | Select com lista de opções |
| CheckBox | Opção marcável |
| Switch/Toggle | Alternância ligado/desligado |
| Data | Date picker |
| Slider | Controle deslizante |
| Rating | Avaliação por estrelas |
| Upload Arquivo | Input de arquivo |

**Visualização**
| Componente | Descrição |
|------------|-----------|
| Texto / Label | Parágrafo ou span de texto |
| Título | H1 a H6 estilizados |
| Imagem | Tag `<img>` com object-fit |
| Ícone | Bootstrap Icons |
| Badge | Etiqueta colorida |
| Progress Bar | Barra de progresso |
| Status Bar | Barra de status com ícone |
| Divisor | Linha separadora `<hr>` |
| Spinner | Indicador de carregamento |

**Container**
| Componente | Descrição |
|------------|-----------|
| Painel | Div container livre |
| Card | Card Bootstrap com header/body/footer |
| GroupBox | Fieldset com legenda |
| Abas (Tabs) | Navegação por abas |
| Accordion | Seções expansíveis |

**Dados**
| Componente | Descrição |
|------------|-----------|
| DataGrid | Tabela com ordenação e filtro |
| Gráfico | Chart.js (bar, line, pie, doughnut) |
| Paginação | Navegação entre páginas de dados |

**Feedback**
| Componente | Descrição |
|------------|-----------|
| Alert | Mensagem de alerta Bootstrap |
| Dialog/Modal | Popup de confirmação ou formulário |

**Navegação**
| Componente | Descrição |
|------------|-----------|
| Navbar | Barra de navegação superior |
| Breadcrumb | Trilha de navegação |
| Stepper | Assistente passo a passo |

**Tempo**
| Componente | Descrição |
|------------|-----------|
| Timer | Dispara evento em intervalo |
| Countdown | Contagem regressiva |

#### Busca na Paleta

Use o campo **"Buscar componente…"** no topo da paleta para filtrar por nome.

---

### 4.3 Canvas — Área de Trabalho

#### Arrastar da Paleta para o Canvas

1. Clique e segure no componente na paleta
2. Arraste para o canvas
3. Solte na posição desejada
4. O componente é criado com tamanho padrão e Snap ao grid de 8px

#### Mover Componentes

- **Clique e arraste** sobre o componente
- Use as **teclas de seta** (move 2px) ou **Shift + seta** (move 10px)
- O componente selecionado fica com borda colorida e alça de redimensionamento

> ⚠️ **Importante:** Os elementos internos do componente (botão, input, etc.) têm `pointer-events:none` no canvas — isso é intencional para que o drag funcione corretamente. Na exportação/preview, os elementos voltam a ser interativos.

#### Redimensionar Componentes

- Clique no componente para selecionar
- Arraste a **alça no canto inferior direito** (triângulo diagonal)
- Tamanho mínimo: 40×24px

#### Selecionar Componente

- **Clique** em qualquer parte do componente
- O painel direito atualiza com as propriedades do componente selecionado
- O nome do componente aparece em uma etiqueta acima

#### Deselecionar

- Clique em qualquer área vazia do canvas
- Pressione **`Esc`**

#### Zoom

| Ação | Como fazer |
|------|-----------|
| Zoom in | Botão `+` no HUD inferior ou `Ctrl+Scroll ↑` |
| Zoom out | Botão `–` no HUD inferior ou `Ctrl+Scroll ↓` |
| Reset 100% | Botão `⊞` no HUD |

#### Grade e Snap

| Botão na Toolbar | Função |
|-----------------|--------|
| **⊞ Grade** | Ativa/desativa grade visual de 8px (fundo pontilhado) |
| **🧲 Snap** | Ativa/desativa alinhamento automático ao grid de 8px |

Quando ativos, os botões ficam com fundo azul.

---

### 4.4 Painel de Propriedades

O painel direito tem 4 abas: **Propriedades**, **Eventos**, **Regras** e **Dados**.

#### Aba Propriedades (☰)

Disponível após selecionar um componente.

**Seção Layout**

| Campo | Descrição |
|-------|-----------|
| X | Posição horizontal em pixels desde a borda esquerda |
| Y | Posição vertical em pixels desde o topo |
| Largura | Largura em pixels |
| Altura | Altura mínima em pixels |
| Z-Index | Camada — número maior fica à frente |
| ↑ / ↓ | Aumenta ou diminui Z-Index em 1 |

> **Dica:** Edite X, Y, W, H diretamente nos campos numéricos para posicionamento preciso.

**Seção Propriedades (dinâmicas)**

Cada tipo de componente exibe seus próprios campos:

- **Botão:** texto, variante (primary/secondary/danger...), ícone
- **Campo Texto:** placeholder, label, tipo (text/email/password), maxlength
- **Título:** texto, tag (h1-h6), tamanho da fonte, cor
- **Imagem:** URL/src, alt, object-fit
- **DataGrid:** colunas, dados de exemplo, striped, hover
- **Card:** título, corpo, header_bg, border_radius

Para cores, aparece um **color picker** nativo do browser.

**Ações**

| Botão | Atalho | Função |
|-------|--------|--------|
| **Duplicar** | `Ctrl+D` | Cria cópia com offset de 16px |
| **Deletar** | `Del` | Remove o componente selecionado |

#### Aba Eventos (⚡)

Permite associar código JavaScript a eventos do componente.

**Eventos disponíveis variam por tipo:**
- `onClick`, `onDoubleClick`, `onMouseEnter`, `onMouseLeave` — todos os componentes
- `onChange`, `onKeyUp`, `onEnterPress` — inputs
- `onRowClick`, `onSort` — DataGrid
- `onTick`, `onComplete` — Timer, Countdown

**Como adicionar um evento:**
1. Selecione o componente
2. Vá para a aba **Eventos**
3. Clique em **+ Adicionar Evento**
4. Selecione o tipo de evento
5. Escolha uma **ação pré-definida** ou escreva código JS livre
6. Clique em **Salvar Evento**

**Ações pré-definidas disponíveis:**

| Ação | O que faz |
|------|-----------|
| Navegar para URL | `window.location.href = '...'` |
| Mostrar Mensagem | `DSB.toast('msg', 'tipo')` |
| Abrir Modal | Abre um componente Modal pelo ID |
| Mostrar/Ocultar | Alterna visibilidade de um componente |
| Definir Valor | `DSB.setValue('id', valor)` |
| Iniciar Timer | `DSB.startTimer('id', ms)` |
| Chamar API | `DSB.callApi(url, método, destino)` |
| Exportar CSV | Exporta DataGrid para CSV |
| Validar Formulário | `DSB.validateAll()` |

#### Aba Regras (≡)

Define validações e comportamentos dinâmicos sem código.

**Grupos de Regras**

| Grupo | Regras Disponíveis |
|-------|-------------------|
| Validação | Campo obrigatório, tamanho mín/máx, e-mail, CPF, CNPJ, apenas números, valor mín/máx, data válida |
| Visibilidade | Visível se, Oculto se, Habilitado se |
| Cálculo | Calcular expressão, Somar campos, Controlar ProgressBar, Mapear status, Formatar valor |

**Como adicionar uma regra:**
1. Selecione o componente (campo de entrada)
2. Vá para a aba **Regras**
3. Clique em **+ Adicionar Regra**
4. Selecione o tipo de regra
5. Configure os parâmetros (mensagem de erro, campos de referência, etc.)
6. Clique em **Salvar Regra**

**Exemplo — Campo obrigatório:**
- Tipo: `Campo Obrigatório`
- Mensagem: `"O nome é obrigatório."`
- Resultado: no runtime, se o campo estiver vazio ao submeter, exibe a mensagem em vermelho

**Exemplo — Visível se:**
- Campo origem: `selTipo` (ComboBox)
- Operador: `==`
- Valor: `"PJ"`
- Resultado: este componente só aparece quando o ComboBox selTipo tiver "PJ"

---

### 4.5 Painel OData

A aba **☁ OData** no painel esquerdo gerencia conexões a servidores OData V4.

#### Adicionar uma Conexão

1. Clique no botão **+** ao lado de "Conexões OData"
2. Preencha o formulário:

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| **Nome** | Identificação da conexão | "Servidor de Clientes" |
| **URL Base** | Endpoint raiz do OData | `http://localhost:8000/odata/` |
| **Autenticação** | Tipo: Nenhuma / Bearer / Basic | Nenhuma |
| **Token** | Token Bearer ou user:pass | (vazio para sem auth) |

3. Clique em **Salvar**

#### Testar a Conexão

Clique no ícone **📶** ao lado da conexão para verificar se o servidor responde e quantas entidades estão disponíveis.

**Resultado esperado:**
```
✅ 3 entidade(s) encontrada(s) (formato: json)
```

#### Descoberta de Metadados ($metadata)

O sistema tenta descobrir o `$metadata` automaticamente na seguinte ordem:

1. Extrai `@odata.context` da resposta do servidor → usa essa URL base
2. Tenta `{base}/$metadata.json` (formato JSON, prioritário)
3. Tenta `{base}/%24metadata.json`
4. Tenta `{base}/metadata.json`
5. Tenta variantes XML: `$metadata`, `%24metadata`, `metadata`

Retorna erro apenas se **nenhuma** variante funcionar.

#### Gerar Telas Automaticamente

Após a conexão estar testada, a lista de entidades aparece abaixo.

Para cada entidade, você tem dois botões:

| Botão | O que gera |
|-------|-----------|
| **Gerar Lista** | Nova página com: Heading, botão Novo, campo de busca, DataGrid com colunas da entidade, Paginação |
| **Gerar Form** | Nova página com: Heading, GroupBoxes por grupo de campos, campos no tipo correto (textbox/numberbox/switch/datepicker), botões Salvar/Cancelar |

**Fluxo de geração:**
1. Clique em **Gerar Lista** ou **Gerar Form**
2. Confirme (ou edite) o nome da página
3. A geração é processada no servidor
4. Uma caixa de confirmação pergunta se deseja abrir a página gerada
5. Clique **OK** para navegar diretamente para a nova página

**O que é gerado automaticamente:**
- Tipo de campo correto por tipo OData (`TEXT`→textbox, `NUMBER`→numberbox, `DATE`→datepicker, `BOOLEAN`→switch, `DROPDOWN`→combobox)
- Regras `obrigatorio` em campos `required: true`
- Regra `max_length` em campos com `max_length` definido
- Binding OData configurado em cada campo (visível na aba Dados)
- Colunas da DataGrid baseadas na anotação `ui.list_view.columns`
- GroupBoxes baseados na anotação `ui.form.groups`

---

### 4.6 Painel de Histórico

A aba **🕐 Histórico** no painel esquerdo exibe a timeline de versões da página atual.

#### Tipos de Versão

| Ícone | Tipo | Quando é criado |
|-------|------|-----------------|
| 🔄 (cinza) | **Automático** | A cada `Ctrl+S` (salvar) |
| 🏷 (azul) | **Manual** | Ao clicar em "+ Versão" |
| `odata-gen` | **OData** | Ao gerar tela via OData |
| `pre-restore` | **Pré-restauração** | Antes de restaurar qualquer versão |

> **Regra de ouro:** Versões automáticas **nunca são apagadas automaticamente**. O sistema sugere quais podem ser purgadas (quando ultrapassam 10 por página), mas a decisão é sempre do usuário.

#### Criar Versão Nomeada

1. Clique em **+ Versão** no topo do painel
2. Informe um **label** (ex: `v1.0`, `pré-odata`, `sprint-3-entrega`)
3. Informe uma **descrição** opcional
4. Adicione **tags** separadas por vírgula (ex: `stable, sprint-3`)
5. Clique em **Salvar**

> **Boa prática:** Crie versões nomeadas antes de grandes mudanças, antes de integrar OData e ao final de cada sprint.

#### Restaurar Versão

1. Localize a versão desejada na timeline
2. Clique no botão **↩** (restaurar)
3. Confirme o diálogo (um snapshot `pre-restore` é criado automaticamente)
4. O canvas recarrega com os componentes daquela versão

#### Deletar Versão (com Backup .dsk)

1. Clique no botão **🗑** ao lado da versão
2. Um diálogo explica que um backup `.dsk` será gerado antes da exclusão
3. Confirme para prosseguir
4. O arquivo `.dsk` fica registrado e disponível para download em **DS_VERSIONS**

> **O formato `.dsk` (DevStation Backup)** é um arquivo ZIP renomeado contendo o JSON completo da versão. Pode ser restaurado via DS_VERSIONS → Importar Backup.

#### Sugestões de Purga

Quando uma página acumula mais de 10 snapshots automáticos, o painel exibe um badge laranja **"N sugerida(s) p/ purga"**.

1. Clique no badge para ver a lista de versões sugeridas
2. Revise cada uma
3. Clique **Deletar c/ .dsk** nas que deseja remover
4. Cada exclusão gera backup antes de deletar

---

### 4.7 Aba Dados — Binding OData

A aba **🗄 Dados** no painel direito aparece ao selecionar um componente compatível: `datagrid`, `combobox`, `textbox`, `numberbox`, `datepicker`, `switch`, `label`, `heading`.

#### Status do Binding

**Sem binding configurado:**
```
⚠️ Sem binding. Configure abaixo para carregar dados OData.
```

**Com binding ativo:**
```
⚡ Binding Ativo
Entidade: Customers
Campo: CompanyName      ← apenas para campos individuais
```

#### Configurar Binding (DataGrid ou ComboBox)

1. Selecione um **DataGrid** ou **ComboBox** no canvas
2. Abra a aba **Dados** no painel direito
3. Selecione a **Conexão OData** (dropdown)
4. Selecione a **Entidade** (dropdown — carrega automaticamente)
5. Configure os filtros opcionais:

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| **$filter** | Filtra registros no servidor | `Country eq 'Brazil'` |
| **$orderby** | Ordena os resultados | `CompanyName asc` |
| **$select** | Limita os campos retornados | `CustomerID,CompanyName,Country` |
| **Registros/pág** | Número máximo de registros | `20` |

6. Clique em **💾 Salvar Binding**

**No preview e na exportação, o DataGrid carregará os dados automaticamente do servidor OData.**

#### Configurar Binding (Campo Individual)

Para `textbox`, `numberbox`, `switch`, `datepicker`:

1. Selecione o campo no canvas
2. Aba **Dados** → selecione Conexão e Entidade
3. No dropdown **Campo individual**, selecione o campo da entidade a vincular
4. Clique em **💾 Salvar Binding**

**No formulário gerado via OData**, os campos já vêm com binding configurado automaticamente.

#### Remover Binding

Clique no botão **✕** (aparece quando já existe binding).

---

### 4.8 Preview e Exportação

#### Preview (Visualização ao Vivo)

Clique no botão **Preview** na toolbar ou pressione **`F5`**.

O preview abre em uma **nova aba** do browser com:
- Barra azul superior com nome do projeto e página
- Canvas renderizado com Bootstrap e Bootstrap Icons
- Dados OData carregados em tempo real (se conexão disponível)
- Badges **⚡ OData** indicam componentes com binding ativo
- Botão **Editar** volta ao Designer
- Botão **Fechar** fecha a aba

> O preview usa o **estilo do sistema** (Bootstrap 5.3 + Bootstrap Icons). Para ver como ficará na página exportada standalone, use Export → HTML.

#### Export ZIP

Clique no botão **ZIP** na toolbar.

O arquivo baixado contém:
- Um arquivo `.html` por página do projeto
- Bootstrap e Bootstrap Icons via CDN
- Runtime `DSB.odata` embutido (se houver binding)
- `window.DSB_ODATA_CONFIG` configurável para apontar para o servidor de produção

**Configurar URL do servidor OData no ZIP exportado:**

Adicione antes do `</body>` do HTML exportado:

```html
<script>
  window.DSB_ODATA_CONFIG = {
    baseUrl: "https://meu-servidor-producao.com/odata/"
  };
</script>
```

#### Export HTML Individual

Via API: `GET /api/paginas/{id}/exportar-html`

Baixa apenas a página atual como `.html` standalone.

---

### 4.9 Atalhos de Teclado

#### Globais (qualquer tela)

| Atalho | Ação |
|--------|------|
| `Ctrl+F5` | Foca o campo de transação rápida |
| `Enter` (no campo de transação) | Navega para a transação digitada |

#### No DS_DESIGNER

| Atalho | Ação |
|--------|------|
| `Ctrl+S` | Salvar página (cria auto-snapshot) |
| `F5` | Abrir Preview em nova aba |
| `Ctrl+Z` | Desfazer última ação |
| `Ctrl+Y` | Refazer |
| `Ctrl+D` | Duplicar componente selecionado |
| `Del` ou `Backspace` | Deletar componente selecionado |
| `Esc` | Deselecionar |
| `↑ ↓ ← →` | Mover componente 2px |
| `Shift + ↑ ↓ ← →` | Mover componente 10px |
| `Ctrl+Scroll` | Zoom no canvas |

---

## 5. DS_VERSIONS — Histórico de Versões

Acesse via: `DS_VERSIONS` no campo de transação ou menu Ferramentas.

### O que você vê

- Lista das **50 versões mais recentes** de todos os projetos
- Tipo (manual/auto), data, projeto, página, número de componentes
- Botão **Abrir** para navegar ao projeto correspondente

### Backups .dsk

Cada versão deletada gera um backup `.dsk`.

**Para baixar um backup:**

Via API: `GET /api/versoes/backups/{project_id}/download`

Os backups ficam em: `dist/backups/version_page{N}_{label}_{timestamp}.dsk`

**Estrutura interna do .dsk (abra com qualquer descompressor ZIP):**
```
version_page5_sprint-1_20260508_143022.dsk
├── version.json    ← JSON completo da versão (componentes + metadados)
└── README.txt      ← Instruções de restauração
```

### Reset de Projeto

Restaura múltiplas páginas simultaneamente via API:

```json
POST /api/projetos/{pid}/reset
{
  "triggered_by": "usuario",
  "pages": [
    {"page_id": 1, "version_id": 15},
    {"page_id": 2, "version_id": 22}
  ]
}
```

Um snapshot `pre-reset` é criado em cada página antes da restauração.

---

## 6. DS_PLUGINS — Gerenciador de Plugins

Acesse via: `DS_PLUGINS` no campo de transação.

### Como Funcionam os Plugins

Plugins são pastas na pasta `plugins/` que registram transações `NDS_*` (Non-Standard). Eles são descobertos automaticamente na inicialização, mas **nunca são ativados automaticamente** — requerem ativação explícita.

### Estrutura de um Plugin

```
plugins/
└── meu_plugin/
    ├── plugin.json       ← Manifesto obrigatório
    └── transactions.py   ← Módulo Python com as transações NDS_*
```

**plugin.json:**
```json
{
  "code":        "meu_plugin",
  "name":        "Meu Módulo Customizado",
  "version":     "1.0.0",
  "author":      "dev@empresa.com",
  "description": "Gerenciamento de membros",
  "entry_point": "meu_plugin.transactions",
  "transactions": ["NDS_MEMBROS_MANTER"]
}
```

**transactions.py:**
```python
TRANSACTIONS = [
    {
        "code":        "NDS_MEMBROS_MANTER",
        "label":       "Manutenção de Membros",
        "group":       "Meu Módulo",
        "description": "CRUD completo de membros",
        "icon":        "bi-people",
        "route":       "/nds/membros",
        "min_profile": "DEVELOPER",
    }
]
```

### Ativar um Plugin

1. Coloque a pasta do plugin em `plugins/`
2. Acesse **DS_PLUGINS**
3. Clique em **Re-escanear** para descobrir novos plugins
4. O plugin aparece com status **Inativo**
5. Clique em **Ativar**
6. Confirme o diálogo (campo `confirmed: true` obrigatório)
7. As transações `NDS_*` do plugin ficam disponíveis no launchpad

### Desativar um Plugin

1. Acesse **DS_PLUGINS**
2. Clique em **Desativar** ao lado do plugin
3. As transações NDS_* do plugin são marcadas como inativas

---

## 7. DS_ADDONS — Gerenciador de Addons

Acesse via: `DS_ADDONS` no campo de transação.

Addons são extensões que adicionam novos tipos de componentes, integrações ou temas ao Builder.

### Instalar um Addon

> **Regra fundamental:** Nenhuma instalação ocorre automaticamente. Cada etapa requer confirmação explícita do usuário.

**Passo a passo:**

1. Acesse **DS_ADDONS**
2. Clique em **Instalar Addon** (botão de upload)
3. Selecione o arquivo `.zip` do addon
4. O sistema valida o `addon.json` interno — verifique o resultado
5. O addon aparece com status **available**
6. Revise as informações (nome, versão, tipo, autor)
7. Clique em **Instalar**
8. Confirme o diálogo — todos os passos são logados
9. Após instalação (status `installed`), clique em **Ativar**
10. Confirme novamente

**Estrutura do addon.json:**
```json
{
  "code":        "ds-charts-pro",
  "name":        "Charts Pro",
  "version":     "2.0.0",
  "author":      "DevStation Labs",
  "type":        "component",
  "description": "Gráficos avançados com Plotly"
}
```

### Log de Instalação

Cada ação de addon é registrada permanentemente. Clique em **📋 Log** ao lado de qualquer addon para ver o histórico completo:

| Ação | Descrição |
|------|-----------|
| `upload_package` | Pacote ZIP recebido |
| `validate_manifest` | addon.json validado |
| `extract_files` | Arquivos extraídos |
| `confirm_install` | Instalação confirmada |
| `activate` | Addon ativado |
| `deactivate` | Addon desativado |
| `uninstall` | Addon removido |
| `error` | Erro em qualquer etapa |

---

## 8. DS_BUILD — Build e Deploy

Acesse via: `DS_BUILD` no campo de transação ou menu Ferramentas.

### Executar Testes

1. Clique em **▶ Executar Testes**
2. O pipeline inicia em background (não bloqueia a tela)
3. A saída do pytest aparece em tempo real no painel preto
4. O resultado final aparece com badge verde (passed) ou vermelho (failed)

**Resultado esperado:**
```
58 passed in 0.75s
```

### Gerar ZIP de Distribuição

1. Certifique-se que o último build está com status **passed**
2. Clique em **⬇ Gerar ZIP**
3. O arquivo é criado em `dist/devstation_builder_v{versão}_{timestamp}.zip`
4. Clique em **⬇ (ícone download)** na linha do build para baixar

> Se o build estiver com status `failed`, o ZIP não é gerado. Use `force: true` via API para forçar (não recomendado para produção).

### Histórico de Builds

A tabela na parte inferior lista os últimos 20 builds com:
- Status, testes passados/falhados, duração, data
- Download do ZIP quando disponível

---

## 9. DS_MENU — Editor de Menu

Acesse via: `DS_MENU` no campo de transação ou **Ferramentas → Editor de Menu** dentro do Designer.

### Como Usar

1. Selecione o **projeto** no dropdown superior
2. No painel esquerdo, clique em um **grupo de menu** (Arquivo, Editar, etc.)
3. Os itens do grupo aparecem à direita
4. Visualize os itens: label, atalho, ação
5. Clique em **💾 Salvar Menu** para persistir as alterações

> Na v3.0, o editor permite visualizar e salvar a configuração JSON do menu. A edição completa drag & drop de itens está prevista para v3.1.

---

## 10. DS_ODATA — Gerenciador OData

Acesse via: `DS_ODATA` no campo de transação.

Esta tela é um ponto central de documentação e acesso rápido às conexões OData por projeto. Para configurar conexões efetivamente, use a **aba OData dentro do DS_DESIGNER** (aba ☁ no painel esquerdo).

**Tipos de campo OData suportados:**

| Tipo OData | Tipo DSB | Componente gerado |
|-----------|----------|-------------------|
| `Edm.String` | TEXT | textbox |
| `Edm.Int32`, `Edm.Decimal` | NUMBER | numberbox |
| `Edm.Date`, `Edm.DateTime` | DATE | datepicker |
| `Edm.Boolean` | BOOLEAN | switch |
| DROPDOWN (anotação) | DROPDOWN | combobox |

---

## 11. Referência de Componentes

### Propriedades Comuns a Todos os Componentes

| Propriedade | Tipo | Descrição |
|-------------|------|-----------|
| `text` | string | Texto principal exibido |
| `font_size` | número | Tamanho da fonte em pixels |
| `text_color` | cor `#hex` | Cor do texto |
| `bg_color` | cor `#hex` | Cor de fundo |
| `border_radius` | número | Raio dos cantos em pixels |

### Propriedades Especiais por Componente

**Botão**
```
text          → "Salvar"
variant       → primary | secondary | success | danger | warning | info | outline-primary
icon          → bi-save (Bootstrap Icon)
icon_pos      → left | right
disabled      → true | false
full_width    → true | false
```

**DataGrid**
```
columns       → ["ID", "Nome", "Valor"]
rows          → [["1","Item A","R$ 10"]]
striped       → true | false
hover         → true | false
sortable      → true | false
odata         → {connection_id, entity, filter, orderby, select, page_size}
```

**Card**
```
title         → "Título do Card"
subtitle      → "Subtítulo"
body          → "Conteúdo do card"
footer        → "Rodapé"
header_bg     → "#4154f1"
header_color  → "#ffffff"
shadow        → true | false
border_radius → 8
```

**Gráfico**
```
chart_type    → bar | line | pie | doughnut
labels        → ["Jan","Fev","Mar"]
data          → [10, 20, 15]
label         → "Vendas"
color         → "#4154f1"
```

**Timer**
```
interval_ms   → 1000
label         → "Timer1"
enabled       → false
repeat        → true
```

**Countdown**
```
seconds       → 60
font_size     → 32
color         → "#4154f1"
auto_start    → false
```

---

## 12. Boas Práticas

### Nomenclatura de Componentes

Use nomes descritivos com prefixo do tipo:

| Tipo | Prefixo | Exemplo |
|------|---------|---------|
| Botão | `btn` | `btnSalvar`, `btnCancelar` |
| Campo texto | `txb` | `txbNome`, `txbEmail` |
| ComboBox | `cbo` | `cboStatus`, `cboPais` |
| CheckBox | `chk` | `chkAtivo`, `chkAceite` |
| DataGrid | `grd` | `grdClientes`, `grdPedidos` |
| Label | `lbl` | `lblTitulo`, `lblInfo` |
| Painel | `pnl` | `pnlCabecalho`, `pnlFiltros` |

### Organização de Páginas

- Crie uma página por funcionalidade (listagem, formulário, relatório)
- Nomeie as páginas com padrão: `[Entidade] — [Função]` (ex: "Clientes — Lista")
- Defina sempre uma página como **Home** (marcada com 🏠)
- Use slugs descritivos (gerados automaticamente do nome)

### Versionamento

- Crie **versão nomeada** antes de cada integração OData
- Crie **versão nomeada** ao final de cada sprint (ex: `sprint-3`, `v1.2-stable`)
- Use tags para organizar: `stable`, `wip`, `odata-gen`, `cliente-aprovado`
- **Nunca ignore** as sugestões de purga — revise periodicamente

### Uso do OData

- Teste a conexão antes de gerar telas
- Prefira usar `$select` para limitar campos e melhorar performance
- Use `$filter` para pré-filtrar dados específicos de um contexto
- Configure `window.DSB_ODATA_CONFIG.baseUrl` no ZIP exportado para produção

### Build e Deploy

- Execute os testes (`DS_BUILD`) antes de qualquer entrega
- Só gere o ZIP de distribuição com build **passed**
- Documente os addons e plugins instalados antes do deploy

---

## 13. Solução de Problemas

### Canvas não responde ao drag

**Causa:** O browser pode estar com zoom diferente de 100%.  
**Solução:** Defina o zoom do browser para 100% (`Ctrl+0`) e reinicie o Designer.

---

### Conexão OData retorna "Não foi possível encontrar o $metadata"

**Causa:** O servidor não expõe o metadata no caminho esperado.  
**Verificação:**
1. Confirme que o servidor está rodando: `curl http://localhost:8000/odata/`
2. Verifique se a URL base está correta (deve terminar com `/odata/`)
3. Tente acessar `http://localhost:8000/odata/$metadata` no browser
4. O servidor deve retornar JSON com `@odata.context` ou um XML EDMX

---

### Campos do formulário OData não aparecem no canvas

**Causa:** A página foi gerada mas o Designer ainda está mostrando a página anterior.  
**Solução:**
1. Após gerar a tela, confirme navegar para a nova página no diálogo
2. Ou use a **aba Páginas** no painel esquerdo para selecionar a nova página

---

### Preview tenta fazer download em vez de abrir

**Causa:** Versão antiga (v3.0.0–v3.0.3).  
**Solução:** Atualize para v3.0.4+ que introduz o template `preview.html` com rota dedicada.

---

### Versão não aparece na timeline após salvar

**Causa:** O auto-snapshot é criado no servidor mas o painel de histórico não recarregou.  
**Solução:** Clique fora da aba Histórico e volte para ela — isso dispara o reload automático.

---

### Plugin não aparece após adicionar na pasta

**Causa:** O sistema escaneia plugins na inicialização e ao clicar em Re-escanear.  
**Solução:** Acesse `DS_PLUGINS` → clique em **Re-escanear**. O plugin aparecerá como **Inativo**.

---

### Addon com status "error" após tentativa de instalação

**Causa:** Erro na extração de arquivos ou manifesto inválido.  
**Como verificar:** Clique em **📋 Log** ao lado do addon para ver a etapa exata que falhou.  
**Solução:** Corrija o problema apontado no log e tente reinstalar (remova o addon primeiro com **Remover**).

---

*Documentação DevStation Builder v3.0.4 — 2026*  
*Gerado automaticamente — para atualizar, edite `docs/MANUAL_USUARIO.md` e execute `DS_BUILD`.*
