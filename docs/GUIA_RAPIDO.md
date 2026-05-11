# ⚡ Guia Rápido — DevStation Builder v3.0

**Para desenvolvedores que querem começar em 5 minutos.**

---

## 1. Instalar e Executar

```bash
# Clone e entre na pasta
cd devstation_builder_v3/

# Instale as dependências
pip install -r requirements.txt

# Execute
python app.py

# Acesse
http://localhost:5000
```

**requirements.txt:**
```
flask>=3.0.0
flask-sqlalchemy>=3.1.1
s2modatapy>=0.1.0
pytest>=8.0.0
pytest-flask>=1.3.0
deepdiff>=7.0.0
```

---

## 2. Criar seu Primeiro Projeto

1. Acesse `http://localhost:5000`
2. Clique em **Novo Projeto**
3. Digite um nome (ex: "Portal de Clientes")
4. O **DS_DESIGNER** abre automaticamente

---

## 3. Usar o DS_DESIGNER

```
TOOLBAR
┌──────────────────────────────────────────────────────────┐
│ ← DS_DESIGNER | NomeProjeto | ↩↪ | ⊞🧲 | W H 🎨 | F5 ZIP 💾 │
└──────────────────────────────────────────────────────────┘

PAINEL ESQUERDO     CANVAS              PAINEL DIREITO
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ ⊞ Componentes│    │              │    │ ☰ Props       │
│ 📄 Páginas   │    │  Arraste     │    │ ⚡ Eventos    │
│ ≡ Outline    │    │  aqui        │    │ ≡ Regras      │
│ ☁ OData      │    │              │    │ 🗄 Dados OData│
│ 🕐 Histórico │    └──────────────┘    └──────────────┘
└──────────────┘
```

**Adicionar componentes:** Arraste da paleta para o canvas.  
**Mover:** Clique e arraste o componente.  
**Redimensionar:** Arraste o triângulo no canto inferior direito.  
**Selecionar:** Clique no componente → painel direito mostra propriedades.  
**Salvar:** `Ctrl+S` (cria snapshot automático).  
**Preview:** `F5` (abre em nova aba com estilo do sistema).

---

## 4. Atalhos Essenciais

| Atalho | Ação |
|--------|------|
| `Ctrl+S` | Salvar + auto-snapshot |
| `F5` | Preview em nova aba |
| `Ctrl+Z / Y` | Desfazer / Refazer |
| `Ctrl+D` | Duplicar componente |
| `Del` | Deletar componente selecionado |
| `Ctrl+F5` | Campo de transação rápida (qualquer tela) |
| `Setas` | Mover 2px |
| `Shift+Setas` | Mover 10px |

---

## 5. Conectar Servidor OData

```
No Designer → aba ☁ OData → botão + → preencha:
  Nome:     "Meu Servidor"
  URL Base: "http://localhost:8000/odata/"
  Auth:     Nenhuma
→ Salvar → 📶 Testar
```

**Gerar tela automaticamente:**
```
Aba OData → lista de entidades → Gerar Lista ou Gerar Form
→ Confirme o nome → OK para abrir a página gerada
```

---

## 6. Navegar por Transações

```
Qualquer tela → campo no header (ou Ctrl+F5) → digitar código:

DS_HOME      → Launchpad (projetos + transações)
DS_DESIGNER  → Abrir designer de um projeto
DS_VERSIONS  → Histórico de versões
DS_BUILD     → Pipeline de testes
DS_PLUGINS   → Gerenciar plugins NDS_*
DS_ADDONS    → Gerenciar addons
DS_ODATA     → Visão geral de conexões OData
```

---

## 7. Versionar seu Trabalho

```bash
# No Designer → aba 🕐 Histórico → "+ Versão"
# Label: "sprint-1", Tags: "stable"

# Para restaurar versão anterior:
# Clique ↩ na versão → confirme
# (snapshot pré-restauração criado automaticamente)

# Para deletar versão (gera .dsk antes):
# Clique 🗑 na versão → confirme
```

---

## 8. Executar Testes

```bash
# Via terminal
python -m pytest tests/ -v

# Via browser: DS_BUILD → "▶ Executar Testes"
```

**Resultado esperado:** `58 passed`

---

## 9. Exportar Projeto

```bash
# ZIP completo (todas as páginas)
GET /api/projetos/{id}/exportar-zip

# HTML de uma página
GET /api/paginas/{id}/exportar-html

# No Designer → botão ZIP na toolbar
```

---

## 10. Adicionar Plugin NDS_*

```bash
# 1. Crie a pasta
mkdir plugins/meu_modulo

# 2. Crie o manifesto
cat > plugins/meu_modulo/plugin.json << 'EOF'
{
  "code": "meu_modulo",
  "name": "Meu Módulo",
  "version": "1.0.0",
  "entry_point": "meu_modulo.transactions",
  "transactions": ["NDS_MEU_MODULO"]
}
EOF

# 3. Crie as transações
cat > plugins/meu_modulo/__init__.py << 'EOF'
EOF
cat > plugins/meu_modulo/transactions.py << 'EOF'
TRANSACTIONS = [{
    "code": "NDS_MEU_MODULO",
    "label": "Meu Módulo",
    "group": "Custom",
    "icon": "bi-puzzle",
    "route": "/nds/meu-modulo",
    "min_profile": "DEVELOPER"
}]
EOF

# 4. Ativar: DS_PLUGINS → Re-escanear → Ativar
```

---

## Próximos Passos

| Quero... | Vá para... |
|----------|-----------|
| Criar formulário com dados reais | [Seção 4.5 — OData](#45-painel-odata) no Manual |
| Versionar e fazer backup | [Seção 4.6 — Histórico](#46-painel-de-histórico) no Manual |
| Entender o binding de dados | [Seção 4.7 — Binding](#47-aba-dados--binding-odata) no Manual |
| Deploy em produção | [Seção 4.8 — Exportação](#48-preview-e-exportação) no Manual |
| Referenciar a API REST | [REFERENCIA_API.md](./REFERENCIA_API.md) |
| Ver arquitetura técnica | [README.md](./README.md) |
