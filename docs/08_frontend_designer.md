# 08 · Frontend — Designer Engine

> 📍 [Início](./README.md) › Frontend Designer

---

## 🏗️ Arquitetura Frontend (MVC)

O `designer.js` (~2.500 linhas) é organizado como **MVC no frontend** usando o padrão **Revealing Module** (IIFEs). Cada módulo é isolado e expõe apenas uma API pública.

```mermaid
graph TB
    subgraph Model["MODEL — DesignerState"]
        DS[DesignerState]
        DS_C[components: Array]
        DS_U[undoStack / redoStack]
        DS_Z[zoom: float]
        DS_D[dirty: bool]
    end

    subgraph View["VIEW — CanvasManager"]
        CM[CanvasManager]
        CM_R[renderAll / renderOne]
        CM_H[highlight / removeEl]
        CM_Z[applyZoom]
        CM_S[applyCanvasSettings]
    end

    subgraph Controller["CONTROLLER — DesignerCtrl"]
        DC[DesignerCtrl]
        DC_I[init — carrega catálogos + canvas]
        DC_S[select / deselect]
        DC_A[addComponent]
        DC_D[deleteSelected / duplicateSelected]
        DC_SA[save → POST /api/paginas/salvar]
        DC_UD[undo / redo]
    end

    subgraph Panels["PAINÉIS"]
        PP[PropsPanel]
        EP[EventsPanel]
        RP[RulesPanel]
        LP[LayersPanel]
        OP[OutlinePanel]
        PS[PagesPanel]
    end

    subgraph Sprint3["SPRINT 3"]
        MS[MultiSelect]
        PM[PageManager]
    end

    subgraph Extras["EXTRAS v2.1"]
        TG[TemplateGallery]
        IM[ImageManager]
        RP2[ResponsivePreview]
    end

    subgraph Input["ENTRADA"]
        PD[PaletteDrag]
        CD[CanvasDrop]
        CTX[ContextMenu]
        KB[KeyBindings]
        MB[MenuBar]
    end

    DC --> DS
    DC --> CM
    DC --> PP
    DC --> EP
    DC --> RP
    DC --> LP
    DC --> OP
    MS --> DS
    MS --> CM
    LP --> DS
    LP --> CM
    LP --> MS
    KB --> DC
    MB --> DC
    PD --> CD
    CD --> DC
    CTX --> DC
```

---

## 📐 Class Diagram — Módulos JS

```mermaid
classDiagram
    class DesignerState {
        -components: Array
        -selectedId: string
        -zoom: float
        -undoStack: Array
        -redoStack: Array
        -dirty: bool
        +add(type, x, y, catalog) Component
        +delete(uid)
        +duplicate(uid) Component
        +getByUid(uid) Component
        +select(uid)
        +deselect()
        +serialize(bg, w, h) dict
        +load(data)
        +pushUndo()
        +undo() bool
        +redo() bool
        +setZoom(z) float
    }

    class CanvasManager {
        -canvas: HTMLElement
        -hint: HTMLElement
        -onSelect: Function
        +init(canvas, hint, callback)
        +renderAll()
        +renderOne(comp)
        +removeEl(uid)
        +highlight(uid)
        +applyZoom(z)
        +applyCanvasSettings(bg, w, h, grid)
        -_buildInner(comp) string
        -_attachEvents(el, comp, uid)
        -_makeInteractable(el, comp, uid)
        -_startInlineEdit(el, comp, uid)
    }

    class DesignerCtrl {
        -cfg: dict
        -catalog: dict
        -eventCatalog: dict
        -actionCatalog: list
        -ruleCatalog: list
        +init() Promise
        +select(uid)
        +deselect()
        +addComponent(type, x, y)
        +deleteSelected()
        +duplicateSelected()
        +undo()
        +redo()
        +save(silent) Promise
        +toggleGrid()
        +applyZoom(z)
        +align(direction)
    }

    class MultiSelect {
        -_sel: Set
        -_rbActive: bool
        -_rbStart: point
        +add(uid)
        +remove(uid)
        +clear()
        +selectAll()
        +deleteSelected()
        +duplicateSelected()
        +alignSelected(dir)
        +moveSelected(dx, dy)
        +isMultiMode() bool
        +getSelectedUids() Set
    }

    class LayersPanel {
        -_meta: Map
        -_dragSrcUid: string
        +init()
        +render()
        +isLocked(uid) bool
        -_attachLayerEvents(container)
        -_reorderLayers(srcUid, targetUid)
    }

    class PropsPanel {
        +init(catalog)
        +load(comp)
        +clear()
        +refreshDynamic(comp)
        +syncPosition(comp)
        +syncSize(comp)
    }

    DesignerCtrl --> DesignerState : usa
    DesignerCtrl --> CanvasManager : usa
    DesignerCtrl --> PropsPanel : atualiza
    MultiSelect --> DesignerState : lê/escreve
    MultiSelect --> CanvasManager : renderiza
    LayersPanel --> DesignerState : lê
    LayersPanel --> CanvasManager : renderiza
    LayersPanel --> MultiSelect : integra
```

---

## 🔄 State Diagram — Ciclo de Vida de um Componente

```mermaid
stateDiagram-v2
    [*] --> Inexistente

    Inexistente --> Criado : Drag da paleta\nou InsertMenu
    Criado --> Posicionado : interact.js drag
    Posicionado --> Selecionado : Click
    Selecionado --> PropriedadesEditadas : Painel Props
    PropriedadesEditadas --> EventoAssociado : Painel Eventos
    EventoAssociado --> RegraCriada : Painel Regras
    Selecionado --> MultiSelecionado : Shift+Click\nou Rubber-band
    MultiSelecionado --> Alinhado : Badge → Alinhar
    MultiSelecionado --> Deletado : Delete / Badge Del
    Selecionado --> Redimensionado : interact.js resize
    Selecionado --> Deletado : Del / btnDelete
    Selecionado --> Duplicado : Ctrl+D
    Duplicado --> Selecionado
    Alinhado --> Selecionado
    RegraCriada --> Salvo : Ctrl+S
    Salvo --> Selecionado
    Salvo --> [*] : Projeto deletado
    Deletado --> [*]
```

---

## 🔄 State Diagram — Canvas Zoom

```mermaid
stateDiagram-v2
    [*] --> Zoom100

    Zoom100 --> ZoomMais : Ctrl+Scroll ↑\nbtnZoomIn
    ZoomMais --> ZoomMais : repete até 300%
    ZoomMais --> Zoom100 : btnZoomReset
    Zoom100 --> ZoomMenos : Ctrl+Scroll ↓\nbtnZoomOut
    ZoomMenos --> ZoomMenos : repete até 20%
    ZoomMenos --> Zoom100 : btnZoomReset

    note right of Zoom100
        Escala padrão: 1.0
        CSS: canvas.style.transform = "scale(1)"
    end note

    note right of ZoomMais
        Max: 3.0 (300%)
        Incremento: 0.1 por clique
    end note
```

---

## 🔄 Sequence Diagram — Inicialização do Designer

```mermaid
sequenceDiagram
    participant Browser
    participant JS as designer.js (DOMContentLoaded)
    participant API as Flask API

    Browser->>JS: DOMContentLoaded
    JS->>JS: DesignerCtrl.init()
    par Carregamento paralelo
        JS->>API: GET /api/componentes/catalogo
        JS->>API: GET /api/eventos/tipos
        JS->>API: GET /api/eventos/acoes
        JS->>API: GET /api/regras/tipos
    end
    API-->>JS: Catálogos retornados (Promise.all)

    JS->>API: GET /api/paginas/<pgid>
    API-->>JS: {components, canvas_bg, canvas_w, canvas_h}
    JS->>JS: DesignerState.load(pageData)
    JS->>JS: CanvasManager.init(canvas, hint, select)
    JS->>JS: CanvasManager.applyCanvasSettings(bg, w, h, grid)
    JS->>JS: CanvasManager.renderAll()

    Note over JS: Inicializa sub-módulos
    JS->>JS: PropsPanel.init(catalog)
    JS->>JS: EventsPanel.init(eventCatalog, actionCatalog)
    JS->>JS: RulesPanel.init(ruleCatalog)
    JS->>JS: PaletteDrag.init(catalog)
    JS->>JS: CanvasDrop.init(canvas, catalog)
    JS->>JS: MenuBar.init(cfg)
    JS->>JS: KeyBindings.init()
    JS->>JS: ContextMenu.init()
    JS->>JS: OutlinePanel.render()

    Note over JS: Sprint 3
    JS->>JS: MultiSelect.init()
    JS->>JS: LayersPanel.init()
    JS->>JS: PageManager.initDuplicate()

    Note over JS: v2.1 Features
    JS->>JS: TemplateGallery.init()
    JS->>JS: ImageManager.init()
    JS->>JS: ResponsivePreview.init()

    JS-->>Browser: Designer pronto para uso
```

---

## 🔄 Sequence Diagram — Drag & Drop de Componente

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant Palette as Paleta (HTML)
    participant JS as designer.js
    participant Canvas as Canvas DOM
    participant State as DesignerState
    participant API as Flask

    Dev->>Palette: dragstart em item "Button"
    Palette->>JS: dataTransfer.setData('comp-type', 'button')
    Dev->>Canvas: drop no canvas
    Canvas->>JS: CanvasDrop drop event
    JS->>JS: type = dataTransfer.getData('comp-type') // 'button'
    JS->>JS: Calcula x,y ajustado ao zoom e snap(grid 5px)
    JS->>State: DesignerState.add('button', x, y, catalog)
    State->>State: Cria comp com defaults + uid temporário
    State-->>JS: comp object
    JS->>Canvas: CanvasManager.renderOne(comp)
    Canvas->>Canvas: Cria div.canvas-comp com inner HTML
    Canvas->>JS: _makeInteractable(el) → interact.draggable + resizable
    JS->>JS: DesignerCtrl.select(comp._uid)
    JS->>JS: PropsPanel.load(comp)
    JS->>JS: OutlinePanel.render()
    JS->>JS: LayersPanel.render()
    JS->>JS: State.dirty = true
    Note over JS,API: Auto-save em 30s ou Ctrl+S manual
```

---

## ⌨️ Atalhos de Teclado

| Atalho | Ação |
|--------|------|
| `Ctrl+S` | Salvar |
| `Ctrl+Z` | Desfazer |
| `Ctrl+Y` / `Ctrl+Shift+Z` | Refazer |
| `Ctrl+D` | Duplicar selecionado(s) |
| `Ctrl+A` | Selecionar todos |
| `Delete` / `Backspace` | Deletar selecionado(s) |
| `Escape` | Desselecionar / Limpar multi-seleção |
| `F5` | Abrir Preview Responsivo |
| `↑ ↓ ← →` | Mover componente 2px |
| `Shift + ↑↓←→` | Mover componente 10px |
| `Shift + Click` | Toggle na multi-seleção |

---

## 🔗 Navegação

| Anterior | Próximo |
|----------|---------|
| [← API & Endpoints](./07_api_endpoints.md) | [Fluxos de Uso →](./09_fluxos_usuario.md) |
