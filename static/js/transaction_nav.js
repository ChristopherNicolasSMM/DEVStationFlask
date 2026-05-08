/**
 * transaction_nav.js — Navegação Global por Transações v3.0
 * ===========================================================
 * - Campo de transação presente em todas as telas (via base.html)
 * - Autocomplete com busca na API /api/transacoes
 * - Histórico dos últimos 10 códigos usados (localStorage)
 * - Atalho global Ctrl+F5 para focar o campo
 * - Launchpad: renderiza cards de transações por grupo
 */

(function () {
  "use strict";

  const TX_HISTORY_KEY = "dsb_tx_history";
  const TX_HISTORY_MAX = 10;

  /* ── Histórico local ─────────────────────────────────────── */

  function getHistory() {
    try { return JSON.parse(localStorage.getItem(TX_HISTORY_KEY) || "[]"); }
    catch (_) { return []; }
  }

  function pushHistory(code) {
    let hist = getHistory().filter(c => c !== code);
    hist.unshift(code);
    if (hist.length > TX_HISTORY_MAX) hist = hist.slice(0, TX_HISTORY_MAX);
    localStorage.setItem(TX_HISTORY_KEY, JSON.stringify(hist));
  }

  /* ── Busca de transações ─────────────────────────────────── */

  let _txCache = [];
  let _fetchTimer = null;

  function fetchTransactions(q) {
    return fetch(`/api/transacoes?q=${encodeURIComponent(q)}`)
      .then(r => r.json())
      .catch(() => []);
  }

  /* ── Campo de transação no header ─────────────────────────── */

  function initTxField() {
    const input    = document.getElementById("inputTransacao");
    const btn      = document.getElementById("btnIrTransacao");
    const dropdown = document.getElementById("txDropdown");

    if (!input) return;  // header pode não estar presente em telas especiais

    // Atalho global Ctrl+F5
    document.addEventListener("keydown", function (e) {
      if (e.ctrlKey && e.key === "F5") {
        e.preventDefault();
        input.focus();
        input.select();
      }
    });

    // Autocomplete ao digitar
    input.addEventListener("input", function () {
      const q = input.value.trim();
      clearTimeout(_fetchTimer);
      if (q.length < 1) { hideDropdown(dropdown); return; }

      _fetchTimer = setTimeout(function () {
        fetchTransactions(q).then(function (txs) {
          showDropdown(dropdown, txs, input);
        });
      }, 180);
    });

    // Navega ao pressionar Enter
    input.addEventListener("keydown", function (e) {
      if (e.key === "Enter") {
        e.preventDefault();
        const highlighted = dropdown && dropdown.querySelector(".tx-item.active");
        const code = (highlighted ? highlighted.dataset.code : input.value).trim().toUpperCase();
        navigateTo(code);
      }
      if (e.key === "Escape") {
        hideDropdown(dropdown);
        input.value = "";
      }
      if (e.key === "ArrowDown" && dropdown) {
        e.preventDefault();
        moveFocus(dropdown, 1);
      }
      if (e.key === "ArrowUp" && dropdown) {
        e.preventDefault();
        moveFocus(dropdown, -1);
      }
    });

    // Botão →
    if (btn) {
      btn.addEventListener("click", function () {
        navigateTo(input.value.trim().toUpperCase());
      });
    }

    // Fecha dropdown ao clicar fora
    document.addEventListener("click", function (e) {
      if (!input.contains(e.target) && dropdown && !dropdown.contains(e.target)) {
        hideDropdown(dropdown);
      }
    });

    // Exibe histórico ao focar campo vazio
    input.addEventListener("focus", function () {
      if (!input.value.trim()) {
        const hist = getHistory();
        if (hist.length) {
          const histItems = hist.map(code => ({ code, label: code, group: "Recente", icon: "bi-clock-history" }));
          showDropdown(dropdown, histItems, input);
        }
      }
    });
  }

  function showDropdown(dropdown, txs, input) {
    if (!dropdown) return;
    if (!txs.length) { hideDropdown(dropdown); return; }

    dropdown.innerHTML = txs.slice(0, 8).map(tx =>
      `<div class="tx-item" data-code="${tx.code}" tabindex="-1">
         <i class="bi ${tx.icon || 'bi-app'} tx-icon"></i>
         <span class="tx-code">${tx.code}</span>
         <span class="tx-label text-muted ms-2 small">${tx.label || ""}</span>
       </div>`
    ).join("");

    dropdown.querySelectorAll(".tx-item").forEach(function (item) {
      item.addEventListener("mousedown", function (e) {
        e.preventDefault();
        navigateTo(item.dataset.code);
      });
      item.addEventListener("mouseover", function () {
        dropdown.querySelectorAll(".tx-item").forEach(i => i.classList.remove("active"));
        item.classList.add("active");
      });
    });

    dropdown.style.display = "block";
  }

  function hideDropdown(dropdown) {
    if (dropdown) dropdown.style.display = "none";
  }

  function moveFocus(dropdown, direction) {
    const items   = Array.from(dropdown.querySelectorAll(".tx-item"));
    const current = dropdown.querySelector(".tx-item.active");
    let   idx     = current ? items.indexOf(current) + direction : 0;
    idx = Math.max(0, Math.min(items.length - 1, idx));
    items.forEach(i => i.classList.remove("active"));
    if (items[idx]) items[idx].classList.add("active");
  }

  function navigateTo(code) {
    if (!code) return;
    pushHistory(code);
    window.location.href = `/transacoes/${code}`;
  }

  /* ── Launchpad: grade de cards de transações ───────────────── */

  function initLaunchpad() {
    const container = document.getElementById("txLaunchpad");
    if (!container) return;

    fetch("/api/transacoes")
      .then(r => r.json())
      .then(function (txs) {
        // Agrupa por group
        const groups = {};
        txs.forEach(function (tx) {
          (groups[tx.group] = groups[tx.group] || []).push(tx);
        });

        const GROUP_ORDER = ["Core","Design","Integration","DevOps","Platform","Admin"];
        const ordered = Object.keys(groups).sort(function (a, b) {
          return (GROUP_ORDER.indexOf(a) + 1 || 99) - (GROUP_ORDER.indexOf(b) + 1 || 99);
        });

        container.innerHTML = ordered.map(function (group) {
          const cards = groups[group].map(tx => _txCard(tx)).join("");
          return `
            <div class="tx-group mb-4">
              <h6 class="tx-group-label text-uppercase fw-semibold text-secondary mb-2">
                <i class="bi bi-grid me-1"></i>${group}
              </h6>
              <div class="tx-card-row d-flex flex-wrap gap-2">${cards}</div>
            </div>`;
        }).join("");

        // Bind clicks
        container.querySelectorAll("[data-tx-code]").forEach(function (card) {
          card.addEventListener("click", function () {
            navigateTo(card.dataset.txCode);
          });
        });

        // Busca no launchpad
        const searchInput = document.getElementById("txLaunchpadSearch");
        if (searchInput) {
          searchInput.addEventListener("input", function () {
            const q = searchInput.value.toLowerCase();
            container.querySelectorAll(".tx-card").forEach(function (card) {
              const matches = card.dataset.txCode.toLowerCase().includes(q) ||
                              card.dataset.txLabel.toLowerCase().includes(q);
              card.style.display = matches ? "" : "none";
            });
          });
        }
      });
  }

  function _txCard(tx) {
    const badge = _profileBadge(tx.min_profile);
    return `
      <div class="tx-card card border-0 shadow-sm" style="width:160px;cursor:pointer;"
           data-tx-code="${tx.code}" data-tx-label="${tx.label || ''}">
        <div class="card-body text-center py-3 px-2">
          <i class="bi ${tx.icon || 'bi-app'} fs-2 text-primary"></i>
          <div class="tx-card-code small fw-bold mt-1">${tx.code}</div>
          <div class="tx-card-label small text-muted">${tx.label || ''}</div>
          ${badge}
        </div>
      </div>`;
  }

  function _profileBadge(profile) {
    const colors = {
      "USER": "secondary", "PUSER": "info", "BANALYST": "primary",
      "DEVELOPER": "success", "CORE_DEV": "warning", "DEV_ALL": "warning",
      "ADMIN": "danger"
    };
    const color = colors[profile] || "secondary";
    return `<span class="badge bg-${color}-subtle text-${color} mt-1" style="font-size:.65rem">${profile}</span>`;
  }

  /* ── Inicialização ───────────────────────────────────────── */

  document.addEventListener("DOMContentLoaded", function () {
    initTxField();
    initLaunchpad();
  });

})();
