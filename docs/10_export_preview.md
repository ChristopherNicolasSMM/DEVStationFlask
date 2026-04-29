# 10 · Export & Preview — Pipeline de Geração de Código

> 📍 [Início](./README.md) › Export & Preview

---

## 🎯 Visão Geral

O pipeline de geração de código converte os dados persistidos no banco de dados em HTML, CSS e JavaScript funcionais, exportáveis como ZIP independente do builder.

```mermaid
graph LR
    DB[(SQLite\nComponents JSON)] --> HG[HtmlGenerator]
    DB --> CG[CssGenerator]
    DB --> JG[JsGenerator]
    DB --> CR[ComponentRegistry]

    CR --> HG
    CR --> CG
    CR --> JG

    HG --> PV[Preview\nInline tudo]
    HG --> ZP[ZIP Export\nlinks externos]
    CG --> ZP
    JG --> ZP

    PV --> BR[Navegador\nPreview]
    ZP --> DL[Download\n.zip]

    style PV fill:#2d3250,color:#fff
    style ZP fill:#2d3250,color:#fff
    style BR fill:#198754,color:#fff
    style DL fill:#4154f1,color:#fff
```

---

## 🏗️ Class Diagram — Generators

```mermaid
classDiagram
    class HtmlGenerator {
        -project: Project
        -page: Page
        -CDN_CSS: list
        -CDN_JS: list
        +render(inline_css, inline_js) str
        -_build_page_css(bg, w, h) str
        -_build_page_js() str
        -_dsb_runtime() str
    }

    class CssGenerator {
        -project: Project
        +render_all() str
        -_base_css() str
    }

    class JsGenerator {
        -project: Project
        +render_all() str
    }

    class ComponentRegistry {
        <<singleton>>
        +render_component(comp_model) str
        +render_css(comp_model) str
        +render_js(comp_model) str
    }

    class ExportController {
        +preview(pid, pgid) Response
        +export_zip(pid) Response
    }

    ExportController --> HtmlGenerator : instancia
    ExportController --> CssGenerator  : instancia (ZIP)
    ExportController --> JsGenerator   : instancia (ZIP)
    HtmlGenerator    --> ComponentRegistry : render_component()
    CssGenerator     --> ComponentRegistry : render_css()
    JsGenerator      --> ComponentRegistry : render_js()
```

---

## 🔄 Sequence Diagram — Preview Geração

```mermaid
sequenceDiagram
    participant B as Navegador
    participant EC as ExportController
    participant HG as HtmlGenerator
    participant CR as ComponentRegistry
    participant DB as SQLite

    B->>EC: GET /projetos/1/preview/1
    EC->>DB: Project.query.get(1)
    EC->>DB: Page.query.get(1)  ← inclui components
    DB-->>EC: Project + Page + Components
    EC->>HG: HtmlGenerator(project, page).render(inline_css=True, inline_js=True)

    HG->>HG: Resolve canvas_w, canvas_h, canvas_bg\n(page ou fallback project)
    HG->>HG: Ordena components por z_index

    loop Para cada Component
        HG->>CR: render_component(comp)
        CR->>CR: _REGISTRY.get(comp.type) → instância BaseComponent
        CR->>CR: instance.render_html(comp_id, name, props, x, y, w, h, z)
        CR-->>HG: HTML string do componente
    end

    HG->>HG: _build_page_css(bg, w, h)\n→ CSS base + CSS de cada comp
    HG->>HG: _build_page_js()\n→ JS de eventos e regras
    HG->>HG: _dsb_runtime()\n→ objeto DSB completo embutido
    HG->>HG: Monta documento HTML completo

    HG-->>EC: HTML string (15–50 KB)
    EC-->>B: text/html; charset=utf-8
```

---

## 🔄 Sequence Diagram — Export ZIP

```mermaid
sequenceDiagram
    participant B as Navegador
    participant EC as ExportController
    participant CG as CssGenerator
    participant JG as JsGenerator
    participant HG as HtmlGenerator
    participant ZF as ZipFile (memory)

    B->>EC: GET /projetos/1/exportar
    EC->>EC: buf = io.BytesIO()
    EC->>ZF: zipfile.ZipFile(buf, 'w', ZIP_DEFLATED)

    EC->>CG: CssGenerator(project).render_all()
    CG->>CG: _base_css() → CSS responsivo base
    loop Para cada página e componente
        CG->>CG: ComponentRegistry.render_css(comp)
    end
    CG-->>EC: style.css content
    EC->>ZF: zf.writestr("style.css", css)

    EC->>JG: JsGenerator(project).render_all()
    loop Para cada componente com eventos/regras
        JG->>JG: ComponentRegistry.render_js(comp)
    end
    JG-->>EC: app.js content
    EC->>ZF: zf.writestr("app.js", js)

    loop Para cada página do projeto
        EC->>HG: HtmlGenerator(project, page).render(inline_css=False, inline_js=False)
        Note over HG: inline=False → usa <link> e <script src>
        HG-->>EC: index.html / sobre.html / etc.
        EC->>ZF: zf.writestr(page.slug + ".html", html)
    end

    EC->>ZF: zf.writestr("README.txt", info)
    EC->>ZF: zf.close()
    EC->>B: send_file(buf, download_name="projeto.zip", mimetype="application/zip")
```

---

## 📦 Estrutura do ZIP Exportado

```
meu-projeto.zip
├── index.html          ← Página home (is_home=True)
├── sobre.html          ← Demais páginas (slug como filename)
├── contato.html
├── style.css           ← CSS consolidado de todas as páginas
├── app.js              ← JS de eventos e regras de todas as páginas
└── README.txt          ← Metadados do projeto
```

---

## 📄 Estrutura do HTML Exportado

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Nome da Página</title>

  <!-- CDNs Bootstrap e Bootstrap Icons -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/...">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/...">

  <!-- Preview: CSS inline | Export: link externo -->
  <style>/* CSS gerado */</style>
  <!-- OU -->
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <!-- Canvas com posicionamento absoluto -->
  <div id="dsb-canvas" class="dsb-canvas" style="background:#ffffff;">
    <!-- Componentes renderizados -->
    <div style="position:absolute;left:100px;top:50px;width:150px;min-height:40px;z-index:1;">
      <button id="comp_1" class="btn btn-primary" data-dsb="btnSalvar">Salvar</button>
    </div>
    <!-- ... mais componentes ... -->
  </div>

  <!-- CDNs JS -->
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/.../bootstrap.bundle.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/..."></script>

  <!-- Runtime DSB (objeto completo embutido) -->
  <script>
    const DSB = {
      toast(msg, type, duration) { ... },
      val(id) { ... },
      setValue(id, v) { ... },
      // ... todos os métodos DSB
      rules: {
        required(el, msg) { ... },
        email(el, msg) { ... },
        // ...
      },
      initAll() { ... }
    };
  </script>

  <!-- Preview: JS inline | Export: script externo -->
  <script>
    document.addEventListener('DOMContentLoaded', () => {
      // eventos e regras dos componentes
      document.getElementById("comp_1").addEventListener("click", function(e) {
        DSB.toast('Salvo!', 'success');
      });
      DSB.initAll();
    });
  </script>
  <!-- OU -->
  <script src="app.js"></script>
</body>
</html>
```

---

## 📱 CSS Responsivo Gerado

O CSS gerado inclui automaticamente media queries para adaptar o layout absoluto ao mobile:

```css
/* Canvas com tamanho fixo no desktop */
.dsb-canvas {
  position: relative;
  width: 1280px;
  min-height: 900px;
  background: #ffffff;
  margin: 0 auto;
  box-shadow: 0 2px 20px rgba(0,0,0,.1);
  overflow: hidden;
}

/* Responsividade automática: abaixo da largura do canvas, 
   converte posicionamento absoluto em fluxo normal */
@media (max-width: 1280px) {
  .dsb-canvas {
    width: 100%;
    min-height: auto;
  }
  [style*="position:absolute"] {
    position: relative !important;
    left: auto !important;
    top: auto !important;
    width: 100% !important;
    margin-bottom: 8px;
  }
}
```

> **Nota:** A responsividade automática garante que o site funcione em mobile mesmo que a página tenha sido projetada em 1280px. O layout muda de **absoluto** para **fluxo normal** abaixo do breakpoint.

---

## 🔄 State Diagram — Modos de Exportação

```mermaid
stateDiagram-v2
    [*] --> Componentes

    Componentes --> PreviewInline : GET /preview/<pgid>
    PreviewInline --> HTMLCompleto : inline_css=True\ninline_js=True
    HTMLCompleto --> Navegador : text/html

    Componentes --> ExportZIP : GET /exportar
    ExportZIP --> CSSFile : CssGenerator.render_all()
    ExportZIP --> JSFile  : JsGenerator.render_all()
    ExportZIP --> HTMLPages : HtmlGenerator.render(inline=False) × N páginas
    CSSFile  --> ZIPBuffer
    JSFile   --> ZIPBuffer
    HTMLPages --> ZIPBuffer
    ZIPBuffer --> Download : send_file() application/zip

    Navegador --> [*]
    Download --> [*]
```

---

## 🔗 Navegação

| Anterior | Próximo |
|----------|---------|
| [← Fluxos de Uso](./09_fluxos_usuario.md) | [Templates →](./11_templates.md) |
