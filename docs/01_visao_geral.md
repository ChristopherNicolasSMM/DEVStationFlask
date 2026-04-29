# 01 · Visão Geral do Produto

> 📍 [Início](./README.md) › Visão Geral

---

## 🎯 Propósito

**DevStation Builder** é uma plataforma RAD *(Rapid Application Development)* visual, inspirada no modelo **Delphi / Visual Studio WinForms**, que permite construir interfaces web empresariais através de **drag & drop** sem escrever HTML/CSS/JS.

O sistema gera código limpo, exportável como ZIP, e está projetado para integração futura com a **DevStation Platform** (sistema SAP-like com transações `DS_*`).

---

## 👥 Personas

| Persona | Perfil DS_ | Necessidade Principal |
|---------|-----------|----------------------|
| **Analista de Sistemas** | `BANALYST` | Prototipar telas rapidamente usando templates, configurar regras de negócio sem código |
| **Developer** | `DEVELOPER` | Construir UIs completas, exportar código para integrar em projetos, criar transações `NDS_*` |
| **Core Developer** | `CORE_DEV` | Criar novos tipos de componentes, customizar o sistema, integrar APIs externas |
| **Power User** | `PUSER` | Usar interfaces geradas, preencher formulários, visualizar dashboards |

---

## 💡 Diferenciais Estratégicos

| Característica | Benefício |
|----------------|-----------|
| Drag & drop com snap | Posicionamento preciso sem escrever CSS |
| 36 componentes prontos | Cobre 95% dos casos de uso empresariais |
| Sistema de eventos visual | Associar ações sem JavaScript manual |
| Sistema de regras | Validação, visibilidade, cálculo automático |
| Export limpo | HTML/CSS/JS independente, sem dependência do builder |
| Templates prontos | Login, Dashboard KPI, CRM, Landing Page, Relatório |
| Multi-páginas | Projetos completos com múltiplas telas |
| Vendors locais | Funciona offline com Bootstrap, BI icons locais |

---

## 🗺️ C4 — Contexto do Sistema

```mermaid
C4Context
    title DevStation Builder — Diagrama de Contexto (C4 Level 1)

    Person(dev, "Developer", "Cria e gerencia projetos de interface visual usando drag & drop")
    Person(analyst, "Analista de Sistemas", "Usa templates, configura regras de negócio sem código")
    Person(user, "Usuário Final", "Acessa as páginas geradas pelo builder")

    System_Boundary(builder_sys, "DevStation Builder") {
        System(builder, "Builder App", "Plataforma RAD visual para criação de interfaces web com Flask + SQLAlchemy")
    }

    System_Ext(browser, "Navegador Web", "Chrome, Firefox, Edge, Safari — interface de uso")
    System_Ext(platform, "DevStation Platform", "Sistema SAP-like com transações DS_*, RBAC 7 níveis, Audit Log")
    System_Ext(sqlite, "SQLite / PostgreSQL", "Banco de dados de projetos, páginas e componentes")
    System_Ext(ext_api, "APIs Externas", "DataSources para DataGrid dinâmico (REST/JSON)")
    System_Ext(github, "GitHub", "Controle de versão do código-fonte")

    Rel(dev, browser, "Acessa via")
    Rel(analyst, browser, "Acessa via")
    Rel(user, browser, "Acessa páginas exportadas via")
    Rel(browser, builder, "HTTP/REST + Static Files")
    Rel(builder, sqlite, "SQLAlchemy ORM")
    Rel(builder, platform, "Integração futura — DS_DESIGNER")
    Rel(builder, ext_api, "fetch() no runtime das páginas exportadas")
    Rel(builder, github, "CI/CD + versionamento")
```

---

## 📦 Escopo do Sistema

### Dentro do Escopo (v2.2)
- ✅ Editor visual drag & drop com canvas absoluto
- ✅ 36 componentes (entrada, visualização, container, dados, feedback, navegação, tempo)
- ✅ Sistema de eventos com editor visual
- ✅ Sistema de regras (validação, visibilidade, cálculo)
- ✅ Multi-seleção, rubber-band, alinhamento em grupo
- ✅ Layers Panel com drag de z-index, lock, visibilidade
- ✅ Multi-páginas + duplicar página
- ✅ Galeria de 5 templates prontos
- ✅ Upload de imagens
- ✅ Preview responsivo (desktop/tablet/mobile)
- ✅ Export ZIP (HTML + CSS + JS funcional)

### Fora do Escopo (próximas sprints)
- ⏳ Autenticação de usuários
- ⏳ Colaboração em tempo real
- ⏳ Deploy em produção com PostgreSQL
- ⏳ Integração formal DS_DESIGNER
- ⏳ Componentes TinyMCE e ApexCharts

---

## 🔄 Fluxo Principal de Valor

```mermaid
stateDiagram-v2
    direction LR
    [*] --> CriarProjeto : Usuário acessa /
    CriarProjeto --> DesignerAberto : Nome do projeto
    DesignerAberto --> ComponenteArrastado : Drag da paleta
    ComponenteArrastado --> PropriedadesEditadas : Clique no componente
    PropriedadesEditadas --> EventoAssociado : Aba Eventos
    EventoAssociado --> RegraCriada : Aba Regras
    RegraCriada --> ProjetoSalvo : Ctrl+S / botão Salvar
    ProjetoSalvo --> PreviewGerado : Preview responsivo
    PreviewGerado --> ZIPExportado : Export ZIP
    ZIPExportado --> [*] : Site funcional

    note right of ComponenteArrastado
        36 tipos disponíveis
        na paleta esquerda
    end note

    note right of ZIPExportado
        HTML + CSS + JS
        Funciona sem o builder
    end note
```

---

## 🔗 Navegação

| Anterior | Próximo |
|----------|---------|
| [← Índice](./README.md) | [Arquitetura →](./02_arquitetura.md) |
