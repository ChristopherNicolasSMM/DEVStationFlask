/**
 * version_panel.js — Painel de Versões no DS_DESIGNER v3.0
 * ==========================================================
 * Aba "Histórico" no painel esquerdo do Designer.
 * - Timeline de versões da página atual
 * - Criar versão nomeada
 * - Restaurar versão (com confirmação)
 * - Ver sugestões de purga
 * - Deletar versão (gera .dsk automaticamente)
 */

(function () {
  "use strict";

  let _pageId  = null;
  let _versions = [];

  window.VersionPanel = {

    init: function (pageId) {
      _pageId = pageId;
      this.load();
    },

    load: function () {
      if (!_pageId) return;
      fetch(`/api/paginas/${_pageId}/versoes`)
        .then(r => r.json())
        .then(function (versions) {
          _versions = versions;
          VersionPanel.render();
        })
        .catch(function (e) { console.error("[VersionPanel] load error", e); });
    },

    render: function () {
      const container = document.getElementById("versionTimeline");
      if (!container) return;

      const purgeCount = _versions.filter(v => v.purge_suggested && !v.deleted).length;

      let headerHtml = `
        <div class="d-flex align-items-center mb-2 px-2 pt-2">
          <span class="fw-semibold small flex-grow-1">Histórico (${_versions.length})</span>
          ${purgeCount ? `<span class="badge bg-warning-subtle text-warning me-2"
                                 onclick="VersionPanel.showPurgeSuggestions()" style="cursor:pointer">
                           ${purgeCount} sugerida(s) p/ purga
                         </span>` : ""}
          <button class="btn btn-xs btn-outline-primary" onclick="VersionPanel.openCreateModal()">
            <i class="bi bi-plus-lg"></i> Versão
          </button>
        </div>`;

      const itemsHtml = _versions.slice(0, 30).map(function (v) {
        const auto  = v.is_auto;
        const icon  = auto ? "bi-arrow-clockwise text-secondary" : "bi-tag-fill text-primary";
        const label = v.version_label.length > 18 ? v.version_label.slice(0, 18) + "…" : v.version_label;
        const tags  = (v.tags || []).map(t => `<span class="badge bg-secondary-subtle text-secondary me-1" style="font-size:.6rem">${t}</span>`).join("");
        const purge = v.purge_suggested ? `<i class="bi bi-exclamation-triangle text-warning ms-1" title="Sugerido para purga"></i>` : "";
        const deleted = v.deleted ? "opacity-50" : "";

        return `
          <div class="version-item px-2 py-1 border-bottom ${deleted}" data-vid="${v.id}">
            <div class="d-flex align-items-center">
              <i class="bi ${icon} me-2"></i>
              <div class="flex-grow-1 overflow-hidden">
                <div class="small fw-semibold text-truncate">${label}${purge}</div>
                <div class="text-muted" style="font-size:.68rem">${v.created_at} • ${v.component_count} comp.</div>
                <div class="mt-1">${tags}</div>
              </div>
              ${!v.deleted ? `
              <div class="btn-group btn-group-sm ms-1">
                <button class="btn btn-xs btn-outline-success" title="Restaurar"
                        onclick="VersionPanel.restore(${v.id}, '${label}')">
                  <i class="bi bi-arrow-counterclockwise"></i>
                </button>
                <button class="btn btn-xs btn-outline-danger" title="Deletar (gera .dsk)"
                        onclick="VersionPanel.deleteVersion(${v.id}, '${label}')">
                  <i class="bi bi-trash"></i>
                </button>
              </div>` : `<span class="badge bg-danger-subtle text-danger small">deletada</span>`}
            </div>
          </div>`;
      }).join("");

      container.innerHTML = headerHtml + itemsHtml;
    },

    /* ── Criar versão nomeada ─────────────────────────────── */

    openCreateModal: function () {
      const modal = document.getElementById("modalCriarVersao");
      if (modal) modal.style.display = 'flex';
    },

    saveVersion: function () {
      const label = document.getElementById("versionLabel").value.trim();
      const desc  = document.getElementById("versionDesc").value.trim();
      const tags  = document.getElementById("versionTags").value
                            .split(",").map(t => t.trim()).filter(Boolean);

      if (!label) { alert("Informe um label para a versão."); return; }

      fetch(`/api/paginas/${_pageId}/versoes`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ label, description: desc, tags }),
      })
        .then(r => r.json())
        .then(function (v) {
          _versions.unshift(v);
          VersionPanel.render();
          const modal = document.getElementById("modalCriarVersao");
          if (modal) modal.style.display = 'none';
          VersionPanel._toast(`Versão "${v.version_label}" criada.`, "success");
        });
    },

    /* ── Restaurar versão ────────────────────────────────── */

    restore: function (vid, label) {
      if (!confirm(`Restaurar a página para a versão "${label}"?\n\nUm snapshot pré-restauração será criado automaticamente.`))
        return;

      fetch(`/api/versoes/${vid}/restaurar`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ triggered_by: "usuario" }),
      })
        .then(r => r.json())
        .then(function (result) {
          if (result.ok) {
            VersionPanel._toast(`Página restaurada para "${label}". Recarregando canvas...`, "success");
            setTimeout(function () {
              if (window.DSBDesigner && DSBDesigner.reloadCanvas) {
                DSBDesigner.reloadCanvas();
              }
              VersionPanel.load();
            }, 800);
          }
        });
    },

    /* ── Deletar versão (com .dsk) ───────────────────────── */

    deleteVersion: function (vid, label) {
      const confirmed = confirm(
        `Deletar a versão "${label}"?\n\n` +
        `⚠️ Um backup .dsk será gerado automaticamente antes da exclusão.\n` +
        `O backup ficará disponível na lista de backups do projeto.`
      );
      if (!confirmed) return;

      fetch(`/api/versoes/${vid}`, {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ triggered_by: "usuario" }),
      })
        .then(r => r.json())
        .then(function (result) {
          if (result.ok) {
            VersionPanel._toast(`Versão deletada. Backup: ${result.backup_name}`, "success");
            VersionPanel.load();
          } else {
            VersionPanel._toast(`Erro: ${result.error}`, "danger");
          }
        });
    },

    /* ── Sugestões de purga ──────────────────────────────── */

    showPurgeSuggestions: function () {
      fetch(`/api/paginas/${_pageId}/versoes/sugestoes-purga`)
        .then(r => r.json())
        .then(function (sugs) {
          const modal = document.getElementById("modalPurgeSugestoes");
          const list  = document.getElementById("purgeSugestoesList");
          if (!list || !modal) return;

          list.innerHTML = sugs.map(v =>
            `<div class="d-flex align-items-center border-bottom py-1">
              <i class="bi bi-exclamation-triangle text-warning me-2"></i>
              <div class="flex-grow-1 small">
                <b>${v.version_label}</b> — ${v.created_at}<br>
                <span class="text-muted">${v.purge_reason || ""}</span>
              </div>
              <button class="btn btn-xs btn-outline-danger ms-2"
                      onclick="VersionPanel.deleteVersion(${v.id}, '${v.version_label}')">
                Deletar c/ .dsk
              </button>
            </div>`
          ).join("") || `<div class="text-muted small">Nenhuma sugestão pendente.</div>`;

          modal.style.display = 'flex';
        });
    },

    /* ── Helper ─────────────────────────────────────────── */

    _toast: function (msg, type) {
      if (window.DSBDesigner && DSBDesigner.showToast) {
        DSBDesigner.showToast(msg, type);
      } else {
        console.log(`[VersionPanel] ${type}: ${msg}`);
      }
    },
  };

})();
