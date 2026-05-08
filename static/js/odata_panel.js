/**
 * odata_panel.js — Painel OData no DS_DESIGNER v3.0
 * ===================================================
 * Gerencia a aba "OData" no painel esquerdo e a aba "Dados"
 * no painel direito de propriedades do componente.
 */

(function () {
  "use strict";

  /* ── Estado ──────────────────────────────────────────────── */
  let _projectId    = null;
  let _connections  = [];
  let _currentConn  = null;
  let _entities     = [];

  /* ── Inicialização ───────────────────────────────────────── */

  window.ODataPanel = {
    init: function (projectId) {
      _projectId = projectId;
      this.load();
    },

    load: function () {
      fetch(`/api/projetos/${_projectId}/odata-connections`)
        .then(r => r.json())
        .then(function (conns) {
          _connections = conns;
          ODataPanel.renderConnectionList();
        })
        .catch(function (e) { console.error("[ODataPanel] load error", e); });
    },

    /* ── Lista de conexões ───────────────────────────────── */

    renderConnectionList: function () {
      const list = document.getElementById("odataConnectionList");
      if (!list) return;

      if (!_connections.length) {
        list.innerHTML = `<div class="text-muted small p-2">Nenhuma conexão configurada.</div>`;
        return;
      }

      list.innerHTML = _connections.map(conn =>
        `<div class="odata-conn-item d-flex align-items-center p-2 border-bottom" data-id="${conn.id}">
          <i class="bi bi-cloud me-2 text-primary"></i>
          <div class="flex-grow-1">
            <div class="fw-semibold small">${conn.name}</div>
            <div class="text-muted" style="font-size:.7rem">${conn.base_url}</div>
          </div>
          <button class="btn btn-sm btn-outline-primary me-1" onclick="ODataPanel.testConn(${conn.id})">
            <i class="bi bi-wifi"></i>
          </button>
          <button class="btn btn-sm btn-outline-danger" onclick="ODataPanel.deleteConn(${conn.id})">
            <i class="bi bi-trash"></i>
          </button>
        </div>`
      ).join("");

      // Clique para expandir entidades
      list.querySelectorAll(".odata-conn-item").forEach(function (item) {
        item.addEventListener("click", function (e) {
          if (e.target.closest("button")) return;
          ODataPanel.loadEntities(parseInt(item.dataset.id));
        });
      });
    },

    /* ── Nova conexão ────────────────────────────────────── */

    openNewConnModal: function () {
      const modal = document.getElementById("modalNovaConexao");
      if (modal) modal.style.display = 'flex';
    },

    saveNewConn: function () {
      const name     = document.getElementById("odataConnName").value.trim();
      const base_url = document.getElementById("odataConnUrl").value.trim();
      const auth     = document.getElementById("odataConnAuth").value;
      const token    = document.getElementById("odataConnToken").value.trim();

      if (!name || !base_url) {
        alert("Nome e URL são obrigatórios.");
        return;
      }

      fetch(`/api/projetos/${_projectId}/odata-connections`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, base_url, auth_type: auth, auth_value: token }),
      })
        .then(r => r.json())
        .then(function (conn) {
          _connections.push(conn);
          ODataPanel.renderConnectionList();
          const modal = document.getElementById("modalNovaConexao");
          if (modal) modal.style.display = 'none';
        });
    },

    /* ── Testar conexão ──────────────────────────────────── */

    testConn: function (connId) {
      const btn = document.querySelector(`.odata-conn-item[data-id="${connId}"] .btn-outline-primary`);
      if (btn) { btn.disabled = true; btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span>'; }

      fetch(`/api/odata-connections/${connId}/testar`, { method: "POST" })
        .then(r => r.json())
        .then(function (result) {
          if (btn) { btn.disabled = false; btn.innerHTML = '<i class="bi bi-wifi"></i>'; }
          if (result.ok) {
            ODataPanel._toast(`✅ ${result.message}`, "success");
            ODataPanel.loadEntities(connId);
          } else {
            ODataPanel._toast(`❌ ${result.error}`, "danger");
          }
        })
        .catch(function () {
          if (btn) { btn.disabled = false; btn.innerHTML = '<i class="bi bi-wifi"></i>'; }
          ODataPanel._toast("Erro ao testar conexão.", "danger");
        });
    },

    deleteConn: function (connId) {
      if (!confirm("Remover esta conexão OData?")) return;
      fetch(`/api/odata-connections/${connId}`, { method: "DELETE" })
        .then(() => {
          _connections = _connections.filter(c => c.id !== connId);
          ODataPanel.renderConnectionList();
          document.getElementById("odataEntityList").innerHTML = "";
        });
    },

    /* ── Entidades ───────────────────────────────────────── */

    loadEntities: function (connId) {
      _currentConn = connId;
      const el = document.getElementById("odataEntityList");
      if (el) el.innerHTML = `<div class="small text-muted p-2"><span class="spinner-border spinner-border-sm me-1"></span>Carregando...</div>`;

      fetch(`/api/odata-connections/${connId}/entidades`)
        .then(r => r.json())
        .then(function (entities) {
          _entities = entities;
          ODataPanel.renderEntityList(entities);
        })
        .catch(function () {
          if (el) el.innerHTML = `<div class="text-danger small p-2">Erro ao carregar entidades.</div>`;
        });
    },

    renderEntityList: function (entities) {
      const el = document.getElementById("odataEntityList");
      if (!el) return;

      if (!entities.length) {
        el.innerHTML = `<div class="text-muted small p-2">Nenhuma entidade disponível.</div>`;
        return;
      }

      el.innerHTML = entities.map(ent =>
        `<div class="odata-entity-item p-2 border-bottom" data-name="${ent.name}">
          <div class="d-flex align-items-center">
            <i class="bi bi-table me-2 text-secondary"></i>
            <div class="flex-grow-1">
              <div class="fw-semibold small">${ent.label}</div>
              <div class="text-muted" style="font-size:.7rem">${ent.name}</div>
            </div>
          </div>
          <div class="mt-1 d-flex gap-1">
            <button class="btn btn-xs btn-outline-primary"
                    onclick="ODataPanel.generateScreen('${ent.name}','list','${ent.label}')">
              <i class="bi bi-list-ul me-1"></i>Gerar Lista
            </button>
            <button class="btn btn-xs btn-outline-success"
                    onclick="ODataPanel.generateScreen('${ent.name}','form','${ent.label}')">
              <i class="bi bi-ui-checks me-1"></i>Gerar Form
            </button>
          </div>
        </div>`
      ).join("");
    },

    /* ── Geração de telas ────────────────────────────────── */

    generateScreen: function (entityName, mode, label) {
      if (!_currentConn) { alert("Selecione uma conexão primeiro."); return; }

      // Pede nome customizado
      var pageName = prompt(
        "Nome para a(s) página(s) gerada(s):",
        label || entityName
      );
      if (pageName === null) return;  // cancelou

      // Bloqueia botão durante geração
      var btn = event && event.target;
      var origHtml = btn ? btn.innerHTML : "";
      if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<span style="display:inline-block;width:10px;height:10px;border:2px solid #fff;border-top-color:transparent;border-radius:50%;animation:spin .6s linear infinite;margin-right:5px;"></span>Gerando...';
      }

      fetch('/api/odata-connections/' + _currentConn + '/gerar-tela', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ entity: entityName, mode: mode, page_name: pageName }),
      })
        .then(function(r) { return r.json(); })
        .then(function (result) {
          if (btn) { btn.disabled = false; btn.innerHTML = origHtml; }
          if (result.ok) {
            var pages = result.pages || [];
            var names = pages.map(function(p) { return p.name; }).join(', ');

            // Mostra resultado com opção de navegar
            var msg  = '✅ ' + pages.length + ' página(s) gerada(s):\n\n' + names + '\n\n';
            msg += 'Deseja abrir a primeira página agora?';
            if (pages.length && confirm(msg)) {
              var pid = window.DSB_DESIGNER_CONFIG && DSB_DESIGNER_CONFIG.projectId;
              window.location.href = '/designer/' + pid + '/' + pages[0].id;
            } else {
              ODataPanel._toast('Página(s) criada(s). Use a aba Páginas para navegar.', 'success');
              // Atualiza lista de páginas no painel
              if (window.DSBDesigner && DSBDesigner.reloadPages) {
                setTimeout(DSBDesigner.reloadPages, 300);
              }
            }
          } else {
            ODataPanel._toast('❌ ' + (result.error || 'Erro ao gerar'), 'danger');
          }
        })
        .catch(function(e) {
          if (btn) { btn.disabled = false; btn.innerHTML = origHtml; }
          ODataPanel._toast('Erro de rede: ' + e.message, 'danger');
        });
    },

    /* ── Aba Dados (painel direito) ──────────────────────── */

    renderBindingPanel: function (componentId, currentProps) {
      var container = document.getElementById("odataBindingContainer");
      if (!container) return;

      var odata      = (currentProps && currentProps.odata) || {};
      var hasBinding = !!(odata.connection_id && odata.entity);

      var statusHtml = hasBinding
        ? '<div style="background:#0d2a1a;border:1px solid #2e7d32;border-radius:5px;padding:8px 10px;margin-bottom:10px;font-size:.75rem;">' +
          '<div style="font-weight:600;color:#66bb6a;margin-bottom:3px;">⚡ Binding Ativo</div>' +
          '<div style="color:#aaa;">Entidade: <b style=\'color:#fff;\'>' + (odata.entity || '') + '</b></div>' +
          (odata.field_binding ? '<div style=\'color:#aaa;\'>Campo: <b style=\'color:#fff;\'>' + odata.field_binding + '</b></div>' : '') +
          '</div>'
        : '<div style="background:#1a1205;border:1px solid #7c4e00;border-radius:5px;padding:7px 10px;margin-bottom:10px;font-size:.73rem;color:#ffa726;">' +
          '⚠️ Sem binding. Configure abaixo para carregar dados OData.' +
          '</div>';

      var helpHtml = '<div style="font-size:.7rem;color:#556;line-height:1.5;margin-bottom:8px;border-bottom:1px solid #1e2340;padding-bottom:6px;">' +
        '<b style=\'color:#8aadff;\'>Como usar:</b><br>' +
        '• <b>DataGrid / ComboBox:</b> carrega lista de registros<br>' +
        '• <b>Campos de formulário:</b> vincula a um campo específico<br>' +
        '• $filter, $orderby, $select são opcionais' +
        '</div>';

      var connOptions = '<option value="">— Sem conexão —</option>' +
        _connections.map(function(c) {
          return '<option value="' + c.id + '"' + (odata.connection_id == c.id ? ' selected' : '') + '>' + c.name + '</option>';
        }).join('');

      var _s = 'width:100%;background:#0d1020;border:1px solid #2a2f4a;color:#ccc;' +
               'padding:5px 7px;border-radius:3px;font-size:.78rem;margin-bottom:6px;';

      container.innerHTML = statusHtml + helpHtml +
        '<label style="font-size:.7rem;color:#889;display:block;margin-bottom:2px;">Conexão</label>' +
        '<select id="odataBindConn" style="' + _s + '">' + connOptions + '</select>' +
        '<div id="odataEntitySection" style="' + (odata.connection_id ? '' : 'display:none;') + '">' +
        '  <label style="font-size:.7rem;color:#889;display:block;margin-bottom:2px;">Entidade</label>' +
        '  <select id="odataBindEntity" style="' + _s + '"><option value="">Carregando...</option></select>' +
        '</div>' +
        '<div id="odataQuerySection" style="' + (odata.entity ? '' : 'display:none;') + '">' +
        '  <label style="font-size:.7rem;color:#889;display:block;margin-bottom:2px;">$filter <span style=\'color:#445;\'>opcional</span></label>' +
        '  <input id="odataBindFilter" style="' + _s + '" placeholder="Country eq \'Brazil\'" value="' + (odata.filter || '') + '">' +
        '  <label style="font-size:.7rem;color:#889;display:block;margin-bottom:2px;">$orderby <span style=\'color:#445;\'>opcional</span></label>' +
        '  <input id="odataBindOrderby" style="' + _s + '" placeholder="Name asc" value="' + (odata.orderby || '') + '">' +
        '  <label style="font-size:.7rem;color:#889;display:block;margin-bottom:2px;">$select <span style=\'color:#445;\'>campos</span></label>' +
        '  <input id="odataBindSelect" style="' + _s + '" placeholder="ID,Name,Country" value="' + (odata.select || '') + '">' +
        '  <label style="font-size:.7rem;color:#889;display:block;margin-bottom:2px;">Registros/pág</label>' +
        '  <input id="odataBindPageSize" type="number" style="' + _s + '" value="' + (odata.page_size || 20) + '">' +
        '  <div id="odataFieldSection" style="' + (odata.field_binding ? '' : 'display:none;') + '">' +
        '    <label style="font-size:.7rem;color:#889;display:block;margin-bottom:2px;">Campo individual</label>' +
        '    <select id="odataBindField" style="' + _s + '"><option value="">— Lista completa —</option></select>' +
        '  </div>' +
        '</div>' +
        '<div style="display:flex;gap:5px;margin-top:6px;">' +
        '  <button onclick="ODataPanel.saveBinding(' + componentId + ')" ' +
        '    style="flex:1;background:#4154f1;color:#fff;border:none;padding:7px;border-radius:4px;cursor:pointer;font-size:.78rem;">' +
        '    💾 Salvar Binding</button>' +
        (hasBinding ? '  <button onclick="ODataPanel.clearBinding(' + componentId + ')" ' +
        '    style="background:transparent;color:#c0392b;border:1px solid #c0392b;padding:7px 10px;border-radius:4px;cursor:pointer;font-size:.78rem;">✕</button>' : '') +
        '</div>';

      // Eventos
      var connEl = document.getElementById("odataBindConn");
      if (connEl) connEl.addEventListener("change", function() {
        var cid = parseInt(this.value);
        var es  = document.getElementById("odataEntitySection");
        var qs  = document.getElementById("odataQuerySection");
        if (!cid) { if(es) es.style.display="none"; if(qs) qs.style.display="none"; return; }
        if (es) es.style.display = "";
        ODataPanel._loadEntitiesForSelect(cid, "");
      });

      if (odata.connection_id) {
        ODataPanel._loadEntitiesForSelect(odata.connection_id, odata.entity);
      }
    },

    clearBinding: function(componentId) {
      if (!confirm("Remover o binding OData deste componente?")) return;
      fetch('/api/componentes/' + componentId, {
        method: 'PUT',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({properties: {}})
      }).then(function() {
        ODataPanel._toast("Binding removido.", "info");
        ODataPanel.renderBindingPanel(componentId, {});
      });
    },

    _loadEntitiesForSelect: function (connId, selectedEntity) {
      fetch('/api/odata-connections/' + connId + '/entidades')
        .then(function(r) { return r.json(); })
        .then(function (entities) {
          var sel = document.getElementById("odataBindEntity");
          if (!sel) return;

          sel.innerHTML = '<option value="">Selecione a entidade...</option>' +
            entities.map(function(e) {
              return '<option value="' + e.name + '"' +
                     (e.name === selectedEntity ? ' selected' : '') +
                     '>' + e.label + ' (' + e.name + ')</option>';
            }).join('');

          // Ao selecionar entidade: mostra seções e carrega campos
          sel.addEventListener("change", function() {
            var qs  = document.getElementById("odataQuerySection");
            var fs  = document.getElementById("odataFieldSection");
            if (!this.value) {
              if (qs) qs.style.display = "none";
              return;
            }
            if (qs) qs.style.display = "";

            // Carrega campos da entidade para field binding
            var entity = entities.find(function(e) { return e.name === sel.value; });
            if (entity && entity.fields && entity.fields.length) {
              var fieldSel = document.getElementById("odataBindField");
              if (fieldSel) {
                if (fs) fs.style.display = "";
                fieldSel.innerHTML = '<option value="">— Lista completa —</option>' +
                  entity.fields.map(function(f) {
                    var fname = typeof f === 'string' ? f : (f.name || '');
                    var flabel = typeof f === 'string' ? f : (f.label || f.name || '');
                    return '<option value="' + fname + '">' + flabel + ' [' + (f.type || 'TEXT') + ']</option>';
                  }).join('');
              }
            }
          });

          // Dispara change se já tinha entidade selecionada
          if (selectedEntity) {
            sel.value = selectedEntity;
            sel.dispatchEvent(new Event("change"));
          }
        })
        .catch(function(e) {
          var sel = document.getElementById("odataBindEntity");
          if (sel) sel.innerHTML = '<option value="">Erro ao carregar entidades</option>';
        });
    },

    saveBinding: function (componentId) {
      var connEl     = document.getElementById("odataBindConn");
      var entityEl   = document.getElementById("odataBindEntity");
      var filterEl   = document.getElementById("odataBindFilter");
      var orderbyEl  = document.getElementById("odataBindOrderby");
      var selectEl   = document.getElementById("odataBindSelect");
      var pageSzEl   = document.getElementById("odataBindPageSize");
      var fieldEl    = document.getElementById("odataBindField");

      var connId    = connEl    ? parseInt(connEl.value)    : 0;
      var entity    = entityEl  ? entityEl.value            : "";
      var filter    = filterEl  ? filterEl.value.trim()     : "";
      var orderby   = orderbyEl ? orderbyEl.value.trim()    : "";
      var select    = selectEl  ? selectEl.value.trim()     : "";
      var pageSize  = pageSzEl  ? (parseInt(pageSzEl.value) || 20) : 20;
      var fieldBind = fieldEl   ? fieldEl.value             : "";

      if (!connId || !entity) {
        ODataPanel._toast("Selecione uma conexão e entidade antes de salvar.", "danger");
        return;
      }

      var odata = {
        connection_id: connId,
        entity:        entity,
        filter:        filter,
        orderby:       orderby,
        select:        select,
        page_size:     pageSize,
        field_binding: fieldBind || null,
        mode:          fieldBind ? "field" : "list",
      };

      // Busca as props atuais do componente e mescla o binding
      fetch('/api/componentes/' + componentId, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ properties: { odata: odata } }),
      })
        .then(function(r) { return r.json(); })
        .then(function () {
          ODataPanel._toast('⚡ Binding OData salvo com sucesso.', 'success');
          // Atualiza o painel para refletir o estado atual
          ODataPanel.renderBindingPanel(componentId, { odata: odata });
        })
        .catch(function() {
          ODataPanel._toast('Erro ao salvar binding.', 'danger');
        });
    },

    /* ── Helpers ─────────────────────────────────────────── */

    _toast: function (msg, type) {
      if (window.DSBDesigner && DSBDesigner.showToast) {
        DSBDesigner.showToast(msg, type);
      } else {
        console.log(`[ODataPanel] ${type}: ${msg}`);
      }
    },
  };

})();
