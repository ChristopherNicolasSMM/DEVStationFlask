# DevStation Builder — Site Builder Visual (Drag & Drop)

## Tecnologias
- Backend: Flask + SQLAlchemy (SQLite)
- Frontend: Bootstrap 5 + Bootstrap Icons + interact.js
- Template base: NiceAdmin (você inclui o `assets/` manualmente)

---
 
## Estrutura de Pastas

```
devstation_builder/
├── app.py
├── models.py
├── requirements.txt
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   └── designer.html
└── static/
    ├── css/
    │   └── designer.css
    ├── js/
    │   └── designer.js
    └── assets/           ← COLE AQUI a pasta assets/ do NiceAdmin
        ├── css/style.css
        ├── js/main.js
        ├── img/
        └── vendor/
```

---

## Instalação e Execução

```bash
# 1. Entre na pasta
cd devstation_builder

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Cole a pasta assets/ do NiceAdmin dentro de static/
#    (static/assets/css/style.css, static/assets/js/main.js, etc.)

# 4. Execute
python app.py

# 5. Acesse
http://localhost:5000
```

---

## Funcionalidades do MVP

### Dashboard
- Listar todos os projetos
- Criar novo projeto (modal)
- Deletar projeto
- Acessar designer
- Preview direto
- Exportar ZIP

### Designer (Drag & Drop)
- **Paleta** (esquerda): 12 tipos de componentes
  - Container, Card, Divisor
  - Parágrafo, Título (h1-h6)
  - Botão, Input, Textarea
  - Imagem, Ícone Bootstrap Icons
  - Alert, Badge
- **Canvas** (centro): posicionamento absoluto
  - Drag para mover
  - Resize pelos cantos
  - Snap em grid de 5px
  - Duplo-clique para editar texto inline
  - Zoom (Ctrl+Scroll ou botões)
  - Fundo e dimensão configuráveis
- **Painel de Propriedades** (direita): edição em tempo real
  - X, Y, Largura, Altura
  - Texto/conteúdo dinâmico por tipo
  - Tipografia: tamanho, cor, negrito, itálico, alinhamento
  - Visual: fundo, borda, border-radius
  - Classes Bootstrap extras
  - Z-index / camadas

### Atalhos de Teclado
| Atalho | Ação |
|--------|------|
| Ctrl+S | Salvar |
| Ctrl+Z | Desfazer |
| Ctrl+Y | Refazer |
| Ctrl+D | Duplicar selecionado |
| Del/Backspace | Deletar selecionado |
| Arrows | Mover 2px |
| Shift+Arrows | Mover 10px |
| Escape | Desselecionar |

### Exportação
- **Preview**: nova aba com o HTML gerado
- **Export ZIP**: baixa `index.html` + `style.css`

---

## Componentes Suportados

| Tipo | Classe Bootstrap Gerada |
|------|------------------------|
| button | `btn btn-primary` |
| label | `<p>` |
| heading | `<h1>`—`<h6>` |
| input | `form-control` |
| textarea | `form-control` |
| image | `<img>` |
| card | `card card-body` |
| divider | `<hr>` |
| alert | `alert alert-{variant}` |
| badge | `badge bg-{color}` |
| icon | `<i class="bi ...">` |
| container | `<div>` |

---

## Próximas Evoluções (pós-MVP)

- [ ] Layers panel (lista de componentes)
- [ ] Templates prontos
- [ ] Upload de imagens
- [ ] Grid/flexbox layout
- [ ] Mobile preview mode
- [ ] Export com Bootstrap incluído
- [ ] Integração com DevStationPlatform (DS_DESIGNER)
