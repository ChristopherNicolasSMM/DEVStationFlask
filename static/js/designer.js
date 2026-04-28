/**
 * DevStation Builder v2 — Designer Engine
 * =========================================
 * Arquivo: static/js/designer.js
 *
 * Arquitetura MVC no frontend:
 *   DesignerState  → Model  (estado, componentes, undo/redo)
 *   CanvasManager  → View   (renderização, interact.js)
 *   DesignerCtrl   → Controller (orquestra Model + View + API)
 *
 * Módulos internos:
 *   PropsPanel     → painel de propriedades
 *   EventsPanel    → editor de eventos
 *   RulesPanel     → editor de regras
 *   OutlinePanel   → árvore de componentes
 *   PagesPanel     → gerenciador de páginas
 *   MenuBar        → ações do menu superior
 *   KeyBindings    → atalhos de teclado
 */

'use strict';

/* ═══════════════════════════════════════════════════════════
   MODEL — DesignerState
   ═══════════════════════════════════════════════════════════ */

const DesignerState = (() => {
  let _components  = [];   // [{id,type,name,x,y,width,height,z_index,properties,events,rules}]
  let _selectedId  = null;
  let _zoom        = 1;
  let _undoStack   = [];   // snapshots JSON para undo
  let _redoStack   = [];
  let _dirty       = false;
  let _uid         = Date.now();

  return {
    // ── Accessors ─────────────────────────────────────────
    get components()  { return _components; },
    get selectedId()  { return _selectedId; },
    get zoom()        { return _zoom; },
    get dirty()       { return _dirty; },
    set dirty(v)      { _dirty = v; },

    // ── Component CRUD ────────────────────────────────────
    getComp(id)     { return _components.find(c => c.id === id) || null; },
    uid()           { return 'c' + (_uid++); },

    /** Adiciona componente com defaults do catálogo */
    add(type, x, y, catalog) {
      this.pushUndo();
      const entry   = catalog[type] || {};
      const size    = entry.default_size || { width: 150, height: 40 };
      const props   = Object.assign({}, entry.default_properties || {});
      const name    = type + '_' + String(_uid).slice(-4);
      const comp = {
        id:         null,          // null = não persistido ainda
        type, name,
        x: Math.round(x),
        y: Math.round(y),
        width:   size.width,
        height:  size.height,
        z_index: _components.length + 1,
        properties: props,
        events: {},
        rules:  [],
      };
      comp._uid = this.uid();      // key temporária para o DOM
      _components.push(comp);
      _dirty = true;
      return comp;
    },

    delete(uid) {
      this.pushUndo();
      _components = _components.filter(c => (c._uid || c.id) !== uid);
      if (_selectedId === uid) _selectedId = null;
      _dirty = true;
    },

    duplicate(uid) {
      const src = this.getByUid(uid);
      if (!src) return null;
      this.pushUndo();
      const clone = JSON.parse(JSON.stringify(src));
      clone.id   = null;
      clone._uid = this.uid();
      clone.name = clone.name + '_copy';
      clone.x   += 20; clone.y += 20;
      _components.push(clone);
      _dirty = true;
      return clone;
    },

    updatePos(uid, x, y) {
      const c = this.getByUid(uid);
      if (!c) return;
      c.x = Math.round(x); c.y = Math.round(y);
      _dirty = true;
    },

    updateSize(uid, w, h) {
      const c = this.getByUid(uid);
      if (!c) return;
      c.width = Math.max(20, Math.round(w));
      c.height = Math.max(10, Math.round(h));
      _dirty = true;
    },

    updateProp(uid, key, value) {
      const c = this.getByUid(uid);
      if (!c) return;
      c[key] = value;
      _dirty = true;
    },

    updateProperty(uid, propKey, value) {
      const c = this.getByUid(uid);
      if (!c) return;
      c.properties[propKey] = value;
      _dirty = true;
    },

    setEvents(uid, events) {
      const c = this.getByUid(uid);
      if (!c) return;
      c.events = events;
      _dirty = true;
    },

    setRules(uid, rules) {
      const c = this.getByUid(uid);
      if (!c) return;
      c.rules = rules;
      _dirty = true;
    },

    select(uid)   { _selectedId = uid; },
    deselect()    { _selectedId = null; },

    /** Carrega snapshot do servidor */
    load(data) {
      _components = (data.components || []).map(c => {
        c._uid = c.id ? 'db_' + c.id : this.uid();
        return c;
      });
      _undoStack = []; _redoStack = []; _dirty = false;
      return data;
    },

    /** Serializa para envio ao servidor */
    serialize(canvasBg, canvasW, canvasH) {
      return {
        canvas_bg: canvasBg,
        canvas_w:  parseInt(canvasW),
        canvas_h:  parseInt(canvasH),
        components: _components.map(c => ({
          id:         c.id || undefined,
          type:       c.type,
          name:       c.name,
          x:          c.x,
          y:          c.y,
          width:      c.width,
          height:     c.height,
          z_index:    c.z_index,
          properties: c.properties || {},
          events:     c.events     || {},
          rules:      c.rules      || [],
        })),
      };
    },

    getByUid(uid) {
      return _components.find(c => (c._uid || c.id) === uid ||
             String(c._uid) === String(uid) ||
             String(c.id)   === String(uid)) || null;
    },

    // ── Undo / Redo ───────────────────────────────────────
    pushUndo() {
      _undoStack.push(JSON.stringify(_components));
      if (_undoStack.length > 60) _undoStack.shift();
      _redoStack = [];
    },
    undo() {
      if (!_undoStack.length) return false;
      _redoStack.push(JSON.stringify(_components));
      _components  = JSON.parse(_undoStack.pop());
      _selectedId  = null; _dirty = true; return true;
    },
    redo() {
      if (!_redoStack.length) return false;
      _undoStack.push(JSON.stringify(_components));
      _components  = JSON.parse(_redoStack.pop());
      _selectedId  = null; _dirty = true; return true;
    },

    // ── Zoom ──────────────────────────────────────────────
    setZoom(z) { _zoom = Math.max(.2, Math.min(3, z)); return _zoom; },
    zoomIn()   { return this.setZoom(_zoom + .1); },
    zoomOut()  { return this.setZoom(_zoom - .1); },
    zoomReset(){ return this.setZoom(1); },
  };
})();


/* ═══════════════════════════════════════════════════════════
   VIEW — CanvasManager
   ═══════════════════════════════════════════════════════════ */

const CanvasManager = (() => {
  let canvas, hint;
  let onSelect = () => {};  // callback ao selecionar
  let catalog  = {};        // cache do catálogo de componentes

  /** Inicializa referências */
  function init(canvasEl, hintEl, selectCallback) {
    canvas   = canvasEl;
    hint     = hintEl;
    onSelect = selectCallback;
  }

  /** Re-renderiza TODOS os componentes */
  function renderAll() {
    canvas.querySelectorAll('.canvas-comp').forEach(el => el.remove());
    const sel = DesignerState.selectedId;
    DesignerState.components
      .slice()
      .sort((a, b) => (a.z_index || 1) - (b.z_index || 1))
      .forEach(c => renderOne(c));
    hint.style.opacity = DesignerState.components.length ? '0' : '1';
    if (sel) {
      const el = canvas.querySelector(`[data-uid="${sel}"]`);
      if (el) el.classList.add('selected');
    }
  }

  /** Renderiza / atualiza um único componente */
  function renderOne(comp) {
    const uid     = comp._uid || comp.id;
    let el        = canvas.querySelector(`[data-uid="${uid}"]`);
    const isNew   = !el;

    if (isNew) {
      el = document.createElement('div');
      el.className = 'canvas-comp';
      el.dataset.uid  = uid;
      el.dataset.type = comp.type;
      canvas.appendChild(el);
      _attachEvents(el, comp, uid);
      _makeInteractable(el, comp, uid);
    }

    // Aplicar posição / tamanho
    el.style.cssText = [
      `left:${comp.x}px`, `top:${comp.y}px`,
      `width:${comp.width}px`, `min-height:${comp.height}px`,
      `z-index:${comp.z_index || 1}`,
      'position:absolute', 'box-sizing:border-box',
    ].join(';') + ';';

    // Conteúdo visual
    el.innerHTML = _buildInner(comp) +
      `<div class="resize-se"></div>` +
      `<div class="comp-label">${comp.name || comp.type}</div>`;

    if (uid === DesignerState.selectedId) el.classList.add('selected');
    hint.style.opacity = DesignerState.components.length ? '0' : '1';
  }

  function removeEl(uid) {
    canvas.querySelector(`[data-uid="${uid}"]`)?.remove();
    hint.style.opacity = DesignerState.components.length ? '0' : '1';
  }

  /** Destaca o componente selecionado */
  function highlight(uid) {
    canvas.querySelectorAll('.canvas-comp.selected')
          .forEach(e => e.classList.remove('selected'));
    if (uid) {
      canvas.querySelector(`[data-uid="${uid}"]`)?.classList.add('selected');
    }
  }

  /** Aplica escala zoom no canvas */
  function applyZoom(z) {
    canvas.style.transform       = `scale(${z})`;
    canvas.style.transformOrigin = 'top left';
  }

  /** Aplica cor e tamanho do canvas */
  function applyCanvasSettings(bg, w, h, showGrid) {
    canvas.style.background = bg;
    canvas.style.width      = w + 'px';
    canvas.style.minHeight  = h + 'px';
    canvas.classList.toggle('show-grid', !!showGrid);
  }

  // ── Geração de HTML interno (preview no canvas) ────────
  function _buildInner(comp) {
    const p = comp.properties || {};
    const t = p.text || p.label || p.title || p.brand || p.placeholder || '';

    switch (comp.type) {
      case 'button':
        return `<button class="btn btn-${p.variant||'primary'} ${p.size==='sm'?'btn-sm':p.size==='lg'?'btn-lg':''}"
          style="width:100%;height:100%;background:${p.bg_color||''};color:${p.text_color||'#fff'};
                 border-radius:${p.border_radius||4}px;font-size:${p.font_size||14}px;border:none;"
          ${p.disabled?'disabled':''}>${p.icon?`<i class="bi ${p.icon} me-1"></i>`:''}${p.text||'Botão'}</button>`;

      case 'label':
        return `<${p.tag||'p'} style="margin:0;font-size:${p.font_size||14}px;
          color:${p.text_color||'#333'};font-weight:${p.bold?'bold':'normal'};
          font-style:${p.italic?'italic':'normal'};text-align:${p.text_align||'left'};"
          >${p.text||'Texto'}</${p.tag||'p'}>`;

      case 'heading':
        return `<${p.tag||'h2'} style="margin:0;font-size:${p.font_size||26}px;
          color:${p.text_color||'#012970'};font-weight:${p.bold!==false?'bold':'normal'};"
          >${p.text||'Título'}</${p.tag||'h2'}>`;

      case 'textbox':
      case 'numberbox':
        return `<input type="${comp.type==='numberbox'?'number':'text'}" class="form-control"
          placeholder="${p.placeholder||''}" value="${p.value||''}"
          style="width:100%;font-size:${p.font_size||14}px;border-radius:${p.border_radius||4}px;"
          ${p.disabled?'disabled':''} ${p.readonly?'readonly':''}>`;

      case 'textarea':
        return `<textarea class="form-control" placeholder="${p.placeholder||''}"
          style="width:100%;height:100%;resize:none;font-size:${p.font_size||14}px;"
          ${p.disabled?'disabled':''} ${p.readonly?'readonly':''}>${p.value||''}</textarea>`;

      case 'checkbox':
      case 'switch':
        return `<div class="form-check ${comp.type==='switch'?'form-switch':''}">
          <input class="form-check-input" type="checkbox" ${p.checked?'checked':''}
                 ${p.disabled?'disabled':''}>
          <label class="form-check-label" style="font-size:${p.font_size||14}px;">${p.text||'Opção'}</label></div>`;

      case 'radiobutton':
        return `<div class="form-check"><input class="form-check-input" type="radio" ${p.checked?'checked':''}>
          <label class="form-check-label">${p.text||'Opção'}</label></div>`;

      case 'combobox':
        return `<select class="form-select" style="font-size:${p.font_size||14}px;" ${p.disabled?'disabled':''}>
          <option>${p.placeholder||'Selecione...'}</option>
          ${(p.items||[]).map(i=>`<option>${i}</option>`).join('')}</select>`;

      case 'slider':
        return `<input type="range" class="form-range" min="${p.min||0}" max="${p.max||100}" value="${p.value||50}">`;

      case 'datepicker':
        return `<input type="date" class="form-control" value="${p.value||''}" ${p.disabled?'disabled':''}>`;

      case 'rating':
        return Array.from({length:p.max||5},(_,i)=>
          `<i class="bi bi-star${i<(p.value||3)?'-fill':''}" style="color:${p.color||'#ffc107'};font-size:${p.size||24}px;cursor:pointer;"></i>`
        ).join('');

      case 'fileupload':
        return `<input type="file" class="form-control" accept="${p.accept||'*/*'}" ${p.multiple?'multiple':''}>`;

      case 'image':
        return `<img src="${p.src||'https://placehold.co/300x200/e8edff/4154f1?text=Imagem'}"
          style="width:100%;height:100%;object-fit:${p.object_fit||'cover'};display:block;
                 border-radius:${p.border_radius||4}px;">`;

      case 'icon':
        return `<div style="display:flex;align-items:center;justify-content:center;height:100%;">
          <i class="bi ${p.icon_class||'bi-star-fill'}" style="font-size:${p.size||32}px;color:${p.color||'#4154f1'};"></i></div>`;

      case 'badge':
        return `<span class="badge bg-${p.variant||'primary'} ${p.pill?'rounded-pill':''}"
          style="font-size:${p.font_size||12}px;">${p.text||'Badge'}</span>`;

      case 'progressbar':
        const pct = Math.round((parseInt(p.value||60)/parseInt(p.max||100))*100);
        return `<div class="progress" style="height:${p.height||20}px;">
          <div class="progress-bar bg-${p.variant||'primary'} ${p.striped?'progress-bar-striped':''} ${p.animated?'progress-bar-animated':''}"
               style="width:${pct}%">${p.show_text?pct+'%':''}</div></div>`;

      case 'statusbar':
        return `<div style="display:flex;align-items:center;gap:6px;padding:4px 12px;
          background:${p.bg_color||'#d1e7dd'};color:${p.text_color||'#0a3622'};height:100%;border-radius:4px;">
          <i class="bi ${p.icon||'bi-check-circle'}"></i>
          <span style="font-size:${p.font_size||13}px;">${p.text||'Pronto'}</span></div>`;

      case 'separator':
        return `<hr style="border:none;border-top:${p.thickness||2}px ${p.style||'solid'} ${p.color||'#dee2e6'};margin:0;width:100%;">`;

      case 'spinner':
        return `<div class="spinner-${p.type||'border'} text-${p.variant||'primary'}" role="status"></div>`;

      case 'panel':
        return `<div style="width:100%;height:100%;background:${p.bg_color||'#f8f9fa'};
          border:1px solid ${p.border||'#dee2e6'};padding:${p.padding||'16px'};
          border-radius:${p.border_radius||4}px;${p.shadow?'box-shadow:0 2px 10px rgba(0,0,0,.1);':''}"></div>`;

      case 'card':
        return `<div class="card" style="width:100%;height:100%;border-radius:${p.border_radius||8}px;overflow:hidden;">
          <div class="card-header" style="background:${p.header_bg||'#4154f1'};color:${p.header_color||'#fff'};padding:8px 12px;">
            <strong>${p.title||'Card'}</strong></div>
          <div class="card-body" style="font-size:13px;overflow:hidden;">${p.body||'Conteúdo...'}</div></div>`;

      case 'groupbox':
        return `<fieldset style="width:100%;height:100%;border:1px solid ${p.border||'#ced4da'};padding:8px;">
          <legend style="font-size:${p.font_size||13}px;padding:0 8px;width:auto;">${p.title||'Grupo'}</legend></fieldset>`;

      case 'tabs':
        return `<div style="width:100%;height:100%;">
          <ul class="nav nav-${p.variant||'tabs'} mb-0">
            ${(p.tabs||['Aba 1','Aba 2']).map((t,i)=>
              `<li class="nav-item"><a class="nav-link ${i===0?'active':''}" href="#">${t}</a></li>`).join('')}
          </ul>
          <div class="border border-top-0 p-2" style="height:calc(100% - 40px);background:#fff;"></div></div>`;

      case 'accordion':
        return `<div class="accordion">${(p.sections||['Seção 1','Seção 2']).map((s,i)=>
          `<div class="accordion-item"><h2 class="accordion-header">
           <button class="accordion-button ${i>0?'collapsed':''}" type="button">${s}</button></h2>
           <div class="accordion-collapse collapse ${i===0?'show':''}">
           <div class="accordion-body" style="font-size:12px;"></div></div></div>`).join('')}</div>`;

      case 'datagrid':
        return `<div style="overflow:auto;width:100%;height:100%;">
          <table class="table ${p.striped?'table-striped':''} ${p.hover?'table-hover':''} table-sm mb-0">
            <thead class="table-dark"><tr>${(p.columns||['ID','Nome','Valor']).map(c=>`<th>${c}</th>`).join('')}</tr></thead>
            <tbody>${(p.rows||[['1','Item A','R$10'],['2','Item B','R$20']]).map(r=>
              `<tr>${r.map(cell=>`<td>${cell}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;

      case 'chart':
        return `<div style="display:flex;align-items:center;justify-content:center;height:100%;
          background:#f8f9fa;border:1px solid #dee2e6;border-radius:4px;flex-direction:column;gap:4px;">
          <i class="bi bi-bar-chart" style="font-size:2rem;color:#4154f1;"></i>
          <small style="color:#666;font-size:11px;">${p.chart_type||'bar'} chart</small></div>`;

      case 'pagination':
        return `<ul class="pagination pagination-sm mb-0">
          <li class="page-item disabled"><a class="page-link">«</a></li>
          ${[1,2,3].map(n=>`<li class="page-item ${n===1?'active':''}"><a class="page-link">${n}</a></li>`).join('')}
          <li class="page-item"><a class="page-link">»</a></li></ul>`;

      case 'alert':
        return `<div class="alert alert-${p.variant||'info'} mb-0" style="font-size:${p.font_size||14}px;">
          ${p.icon?`<i class="bi ${p.icon} me-2"></i>`:''}${p.text||'Mensagem'}</div>`;

      case 'modal':
        return `<button class="btn btn-primary" style="font-size:${p.font_size||14}px;">
          ${p.trigger_label||'Abrir Dialog'}</button>`;

      case 'navbar':
        return `<nav class="navbar navbar-expand-lg navbar-${p.variant||'dark'} bg-${p.bg||'primary'}"
          style="width:100%;height:100%;padding:0 12px;">
          <a class="navbar-brand" href="#">${p.brand||'Meu Site'}</a>
          <div class="navbar-nav d-flex flex-row gap-2">
            ${(p.links||['Início','Sobre']).map(l=>`<a class="nav-link" href="#">${l}</a>`).join('')}
          </div></nav>`;

      case 'breadcrumb':
        return `<nav><ol class="breadcrumb mb-0">
          ${(p.items||['Início','Página']).map((it,i,a)=>
            `<li class="breadcrumb-item ${i===a.length-1?'active':''}">${it}</li>`).join('')}
          </ol></nav>`;

      case 'stepper':
        return `<div style="display:flex;align-items:center;width:100%;">
          ${(p.steps||['Passo 1','Passo 2','Passo 3']).map((s,i)=>
            `<div style="flex:1;text-align:center;">
               <div style="width:28px;height:28px;border-radius:50%;
                    background:${i<(p.current||1)?'#4154f1':'#dee2e6'};
                    color:${i<(p.current||1)?'#fff':'#666'};
                    display:inline-flex;align-items:center;justify-content:center;font-size:12px;">${i+1}</div>
               <div style="font-size:10px;margin-top:3px;">${s}</div></div>`).join(
            `<div style="flex:1;height:2px;background:#dee2e6;margin-bottom:14px;"></div>`
          )}</div>`;

      case 'timer':
        return `<div style="display:flex;align-items:center;gap:6px;padding:6px 10px;
          background:#fff3cd;border:1px solid #ffc107;border-radius:4px;height:100%;">
          <i class="bi bi-alarm text-warning"></i>
          <span style="font-size:12px;">${p.label||'Timer'} (${p.interval_ms||1000}ms)</span></div>`;

      case 'countdown':
        const s = parseInt(p.seconds||60); const mm=String(Math.floor(s/60)).padStart(2,'0'); const ss=String(s%60).padStart(2,'0');
        return `<div style="display:flex;align-items:center;justify-content:center;height:100%;">
          <span class="countdown-display" style="font-size:${p.font_size||32}px;color:${p.color||'#4154f1'};
                font-family:monospace;font-weight:bold;">${mm}:${ss}</span></div>`;

      default:
        return `<div style="padding:8px;font-size:12px;color:#666;">${comp.type}</div>`;
    }
  }

  // ── Interact.js (drag + resize) ───────────────────────
  function _attachEvents(el, comp, uid) {
    el.addEventListener('mousedown', (e) => {
      if (e.button === 0) DesignerCtrl.select(uid);
    });
    el.addEventListener('contextmenu', (e) => {
      e.preventDefault();
      DesignerCtrl.select(uid);
      ContextMenu.show(e.clientX, e.clientY, uid);
    });
    el.addEventListener('dblclick', () => {
      _startInlineEdit(el, comp, uid);
    });
  }

  function _makeInteractable(el, comp, uid) {
    interact(el)
      .draggable({
        listeners: {
          start() { DesignerState.pushUndo(); },
          move(ev) {
            const z = DesignerState.zoom;
            const c = DesignerState.getByUid(uid);
            if (!c) return;
            c.x = Math.round((c.x + ev.dx / z) / 5) * 5;
            c.y = Math.round((c.y + ev.dy / z) / 5) * 5;
            el.style.left = c.x + 'px';
            el.style.top  = c.y + 'px';
            PropsPanel.syncPosition(c);
            DesignerState.dirty = true;
          },
        },
        modifiers: [
          interact.modifiers.restrictRect({ restriction: canvas, endOnly: false }),
        ],
      })
      .resizable({
        edges: { bottom: true, right: true, bottomRight: true },
        listeners: {
          start() { DesignerState.pushUndo(); },
          move(ev) {
            const z = DesignerState.zoom;
            const c = DesignerState.getByUid(uid);
            if (!c) return;
            c.width  = Math.max(20, Math.round(ev.rect.width  / z / 5) * 5);
            c.height = Math.max(10, Math.round(ev.rect.height / z / 5) * 5);
            el.style.width     = c.width  + 'px';
            el.style.minHeight = c.height + 'px';
            PropsPanel.syncSize(c);
            DesignerState.dirty = true;
          },
        },
        modifiers: [
          interact.modifiers.restrictSize({ minWidth: 20, minHeight: 10 }),
        ],
      });
  }

  // ── Inline text editing (double-click) ───────────────
  function _startInlineEdit(el, comp, uid) {
    const textTypes = ['label','heading','button','badge','alert','card','panel','groupbox','container'];
    if (!textTypes.includes(comp.type)) return;
    const textEl = el.querySelector('p,h1,h2,h3,h4,h5,h6,button,span.badge,.card-body,.accordion-body');
    if (!textEl) return;
    textEl.contentEditable = true;
    textEl.focus();
    const sel = window.getSelection();
    const range = document.createRange();
    range.selectNodeContents(textEl);
    sel.removeAllRanges(); sel.addRange(range);
    textEl.addEventListener('blur', () => {
      textEl.contentEditable = false;
      comp.properties.text = textEl.textContent;
      DesignerState.dirty = true;
      PropsPanel.refreshDynamic(comp);
    }, { once: true });
    textEl.addEventListener('keydown', e => {
      if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); textEl.blur(); }
      if (e.key === 'Escape') { textEl.textContent = comp.properties.text || ''; textEl.blur(); }
    });
  }

  // Public API
  return { init, renderAll, renderOne, removeEl, highlight, applyZoom, applyCanvasSettings };
})();


/* ═══════════════════════════════════════════════════════════
   CONTROLLER — DesignerCtrl
   ═══════════════════════════════════════════════════════════ */

const DesignerCtrl = (() => {
  let cfg      = {};
  let catalog  = {};   // { type: { default_properties, default_size, available_events, available_rules } }
  let eventCatalog  = {};
  let actionCatalog = [];
  let ruleCatalog   = [];
  let _gridOn = true;
  let _snapOn = true;
  let _autoSaveId = null;

  async function init() {
    cfg = window.DSB_CONFIG || {};
    // Carrega catálogos do servidor
    [catalog, eventCatalog, actionCatalog, ruleCatalog] = await Promise.all([
      fetch(cfg.compCatalog).then(r=>r.json()).then(arr => {
        const map = {};
        arr.forEach(g => g.items.forEach(i => map[i.type] = i));
        return map;
      }),
      fetch(cfg.eventTypes).then(r=>r.json()),
      fetch(cfg.eventActions).then(r=>r.json()),
      fetch(cfg.ruleTypes).then(r=>r.json()),
    ]);

    // Init canvas
    const canvas = document.getElementById('canvas');
    const hint   = document.getElementById('canvasHint');
    CanvasManager.init(canvas, hint, select);
    CanvasManager.applyCanvasSettings(cfg.canvasBg, cfg.canvasW, cfg.canvasH, _gridOn);

    // Carrega componentes da página atual
    const pageData = await fetch(cfg.loadUrl).then(r=>r.json());
    DesignerState.load(pageData);
    CanvasManager.renderAll();

    // Sub-módulos
    PropsPanel.init(catalog);
    EventsPanel.init(eventCatalog, actionCatalog);
    RulesPanel.init(ruleCatalog);
    OutlinePanel.init();
    PagesPanel.init();
    MenuBar.init(cfg);
    KeyBindings.init();
    PaletteDrag.init(catalog);
    CanvasDrop.init(canvas, catalog);
    ContextMenu.init();

    // Atualiza outline
    OutlinePanel.render();

    // Auto-save a cada 30s
    _autoSaveId = setInterval(() => { if (DesignerState.dirty) save(true); }, 30000);

    // Ajusta canvas settings quando inputs mudam
    document.getElementById('inputCanvasW')?.addEventListener('change', _applyCanvasInputs);
    document.getElementById('inputCanvasH')?.addEventListener('change', _applyCanvasInputs);
    document.getElementById('inputCanvasBg')?.addEventListener('input', _applyCanvasInputs);
  }

  function _applyCanvasInputs() {
    const bg = document.getElementById('inputCanvasBg')?.value || cfg.canvasBg;
    const w  = document.getElementById('inputCanvasW')?.value  || cfg.canvasW;
    const h  = document.getElementById('inputCanvasH')?.value  || cfg.canvasH;
    CanvasManager.applyCanvasSettings(bg, w, h, _gridOn);
    DesignerState.dirty = true;
  }

  function select(uid) {
    DesignerState.select(uid);
    CanvasManager.highlight(uid);
    const comp = DesignerState.getByUid(uid);
    PropsPanel.load(comp);
    EventsPanel.load(comp);
    RulesPanel.load(comp);
    OutlinePanel.highlight(uid);
  }

  function deselect() {
    DesignerState.deselect();
    CanvasManager.highlight(null);
    PropsPanel.clear();
    EventsPanel.clear();
    RulesPanel.clear();
  }

  function addComponent(type, x, y) {
    const comp = DesignerState.add(type, x, y, catalog);
    CanvasManager.renderOne(comp);
    OutlinePanel.render();
    select(comp._uid);
    return comp;
  }

  function deleteSelected() {
    const uid = DesignerState.selectedId;
    if (!uid) return;
    DesignerState.delete(uid);
    CanvasManager.removeEl(uid);
    deselect();
    OutlinePanel.render();
  }

  function duplicateSelected() {
    const uid = DesignerState.selectedId;
    if (!uid) return;
    const clone = DesignerState.duplicate(uid);
    if (!clone) return;
    CanvasManager.renderOne(clone);
    OutlinePanel.render();
    select(clone._uid);
  }

  function undo() {
    if (DesignerState.undo()) { CanvasManager.renderAll(); PropsPanel.clear(); OutlinePanel.render(); }
  }

  function redo() {
    if (DesignerState.redo()) { CanvasManager.renderAll(); PropsPanel.clear(); OutlinePanel.render(); }
  }

  async function save(silent = false) {
    const bg = document.getElementById('inputCanvasBg')?.value || cfg.canvasBg;
    const w  = document.getElementById('inputCanvasW')?.value  || cfg.canvasW;
    const h  = document.getElementById('inputCanvasH')?.value  || cfg.canvasH;
    const payload = DesignerState.serialize(bg, w, h);
    const r = await fetch(cfg.saveUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const d = await r.json();
    if (!silent) {
      const st = document.getElementById('statusSave');
      if (st) { st.textContent = `✓ Salvo ${d.saved_at}`; st.classList.add('save-flash'); }
    }
    // Re-carrega para obter IDs reais do banco
    const refreshed = await fetch(cfg.loadUrl).then(rx => rx.json());
    DesignerState.load(refreshed);
    CanvasManager.renderAll();
    const sel = DesignerState.selectedId;
    if (sel) CanvasManager.highlight(sel);
  }

  function toggleGrid() {
    _gridOn = !_gridOn;
    const bg = document.getElementById('inputCanvasBg')?.value || cfg.canvasBg;
    const w  = document.getElementById('inputCanvasW')?.value  || cfg.canvasW;
    const h  = document.getElementById('inputCanvasH')?.value  || cfg.canvasH;
    CanvasManager.applyCanvasSettings(bg, w, h, _gridOn);
    document.getElementById('btnGrid')?.setAttribute('data-active', _gridOn);
  }

  function applyZoom(z) {
    const newZ = DesignerState.setZoom(z);
    CanvasManager.applyZoom(newZ);
    const lbl = document.getElementById('zoomLabel');
    if (lbl) lbl.textContent = Math.round(newZ * 100) + '%';
  }

  function align(direction) {
    const uid = DesignerState.selectedId;
    const comp = DesignerState.getByUid(uid);
    const canvasW = parseInt(document.getElementById('inputCanvasW')?.value || cfg.canvasW);
    if (!comp) return;
    DesignerState.pushUndo();
    if (direction === 'left')   comp.x = 0;
    if (direction === 'center') comp.x = Math.round((canvasW - comp.width) / 2);
    if (direction === 'right')  comp.x = canvasW - comp.width;
    CanvasManager.renderOne(comp);
    PropsPanel.syncPosition(comp);
    DesignerState.dirty = true;
  }

  return { init, select, deselect, addComponent, deleteSelected,
           duplicateSelected, undo, redo, save, toggleGrid,
           applyZoom, align, getCatalog: () => catalog };
})();


/* ═══════════════════════════════════════════════════════════
   PropsPanel — Painel de Propriedades
   ═══════════════════════════════════════════════════════════ */

const PropsPanel = (() => {
  let _catalog = {};

  function init(catalog) { _catalog = catalog; _attachListeners(); }

  function load(comp) {
    if (!comp) { clear(); return; }
    document.getElementById('propsEmpty').style.display = 'none';
    document.getElementById('propsForm').style.display  = '';

    document.getElementById('propName').value = comp.name || '';
    document.getElementById('propType').value = comp.type || '';
    document.getElementById('propX').value    = comp.x;
    document.getElementById('propY').value    = comp.y;
    document.getElementById('propW').value    = comp.width;
    document.getElementById('propH').value    = comp.height;
    document.getElementById('propZ').value    = comp.z_index || 1;

    const p = comp.properties || {};

    // Tipografia
    const typoSec = document.getElementById('sectionTypo');
    if (p.font_size !== undefined) {
      typoSec.style.display = '';
      document.getElementById('propFontSize').value    = p.font_size || 14;
      document.getElementById('propTextColor').value   = p.text_color || '#333333';
      document.getElementById('propBold')?.classList.toggle('active',   !!p.bold);
      document.getElementById('propItalic')?.classList.toggle('active', !!p.italic);
      document.querySelectorAll('[data-align]').forEach(btn =>
        btn.classList.toggle('active', btn.dataset.align === (p.text_align || 'left')));
    } else { typoSec.style.display = 'none'; }

    // Aparência
    document.getElementById('propBgColor').value = p.bg_color || p.bgColor || '#f8f9fa';
    document.getElementById('propRadius').value  = p.border_radius || 4;
    document.getElementById('propClasses').value = p.extraClasses || '';

    // Campos dinâmicos
    refreshDynamic(comp);
  }

  function refreshDynamic(comp) {
    const container = document.getElementById('dynamicProps');
    if (!container) return;
    const p = comp.properties || {};
    const fields = [];

    // Campos comuns por tipo
    if (['button','label','heading','badge','alert','card','groupbox','navbar'].includes(comp.type))
      fields.push({key:'text', label:'Texto', type:'text'});
    if (comp.type === 'heading') fields.push({key:'tag', label:'Tag', type:'select', opts:['h1','h2','h3','h4','h5','h6']});
    if (['label','heading'].includes(comp.type)) fields.push({key:'tag', label:'Tag HTML', type:'select', opts:['p','h1','h2','h3','h4','h5','h6','span','div']});
    if (['textbox','textarea','numberbox','combobox','datepicker','fileupload'].includes(comp.type))
      fields.push({key:'placeholder', label:'Placeholder', type:'text'});
    if (comp.type === 'image') {
      fields.push({key:'src', label:'URL da Imagem', type:'text'});
      fields.push({key:'object_fit', label:'Object Fit', type:'select', opts:['cover','contain','fill','none']});
    }
    if (comp.type === 'icon') fields.push({key:'icon_class', label:'Ícone (ex: bi-star-fill)', type:'text'});
    if (comp.type === 'progressbar') {
      fields.push({key:'value', label:'Valor (%)', type:'number'});
      fields.push({key:'variant', label:'Variante', type:'select', opts:['primary','success','warning','danger','info']});
    }
    if (comp.type === 'timer') {
      fields.push({key:'interval_ms', label:'Intervalo (ms)', type:'number'});
      fields.push({key:'label', label:'Label', type:'text'});
    }
    if (comp.type === 'countdown') fields.push({key:'seconds', label:'Segundos', type:'number'});
    if (comp.type === 'statusbar') {
      fields.push({key:'text', label:'Texto', type:'text'});
      fields.push({key:'icon', label:'Ícone', type:'text'});
    }
    if (comp.type === 'button') fields.push({key:'variant', label:'Variante', type:'select',
      opts:['primary','secondary','success','danger','warning','info','light','dark','outline-primary','outline-secondary']});
    if (comp.type === 'alert') fields.push({key:'variant', label:'Variante', type:'select',
      opts:['primary','secondary','success','danger','warning','info','light','dark']});

    container.innerHTML = fields.map(f => {
      const val = p[f.key] !== undefined ? p[f.key] : '';
      if (f.type === 'select') {
        return `<div class="mb-2"><label class="props-label">${f.label}</label>
          <select class="form-select form-select-sm" data-prop="${f.key}">
            ${f.opts.map(o => `<option ${val===o?'selected':''}>${o}</option>`).join('')}
          </select></div>`;
      }
      return `<div class="mb-2"><label class="props-label">${f.label}</label>
        <input type="${f.type||'text'}" class="form-control form-control-sm"
               data-prop="${f.key}" value="${String(val).replace(/"/g,'&quot;')}"></div>`;
    }).join('');

    // Live update
    container.querySelectorAll('[data-prop]').forEach(el => {
      el.addEventListener('input', () => {
        const uid = DesignerState.selectedId;
        const comp = DesignerState.getByUid(uid);
        if (!comp) return;
        comp.properties[el.dataset.prop] = el.type === 'number' ? +el.value : el.value;
        CanvasManager.renderOne(comp);
        DesignerState.dirty = true;
      });
    });
  }

  function clear() {
    document.getElementById('propsEmpty').style.display = '';
    document.getElementById('propsForm').style.display  = 'none';
  }

  function syncPosition(comp) {
    document.getElementById('propX').value = comp.x;
    document.getElementById('propY').value = comp.y;
  }
  function syncSize(comp) {
    document.getElementById('propW').value = comp.width;
    document.getElementById('propH').value = comp.height;
  }

  function _attachListeners() {
    const sync = (id, fn) => document.getElementById(id)?.addEventListener('input', fn);

    sync('propX', e => _updPos());
    sync('propY', e => _updPos());
    sync('propW', e => _updSize());
    sync('propH', e => _updSize());
    sync('propZ', e => {
      const c = _sel(); if (!c) return;
      c.z_index = +e.target.value; CanvasManager.renderOne(c); DesignerState.dirty=true;
    });
    sync('propName', e => {
      const c = _sel(); if (!c) return;
      c.name = e.target.value; CanvasManager.renderOne(c); DesignerState.dirty=true;
    });
    sync('propFontSize', e => _updProp('font_size', +e.target.value));
    sync('propTextColor', e => _updProp('text_color', e.target.value));
    sync('propBgColor',   e => _updProp('bg_color',   e.target.value));
    sync('propRadius',    e => _updProp('border_radius', +e.target.value));
    sync('propClasses',   e => _updProp('extraClasses', e.target.value));

    document.getElementById('propBold')?.addEventListener('click', () => {
      const c = _sel(); if (!c) return;
      c.properties.bold = !c.properties.bold;
      document.getElementById('propBold').classList.toggle('active', c.properties.bold);
      CanvasManager.renderOne(c); DesignerState.dirty=true;
    });
    document.getElementById('propItalic')?.addEventListener('click', () => {
      const c = _sel(); if (!c) return;
      c.properties.italic = !c.properties.italic;
      document.getElementById('propItalic').classList.toggle('active', c.properties.italic);
      CanvasManager.renderOne(c); DesignerState.dirty=true;
    });
    document.querySelectorAll('[data-align]').forEach(btn => {
      btn.addEventListener('click', () => {
        _updProp('text_align', btn.dataset.align);
        document.querySelectorAll('[data-align]').forEach(b => b.classList.toggle('active', b===btn));
      });
    });
    document.getElementById('btnZUp')?.addEventListener('click', () => {
      const c = _sel(); if (!c) return;
      c.z_index = (c.z_index||1) + 1;
      document.getElementById('propZ').value = c.z_index;
      CanvasManager.renderOne(c); DesignerState.dirty=true;
    });
    document.getElementById('btnZDown')?.addEventListener('click', () => {
      const c = _sel(); if (!c) return;
      c.z_index = Math.max(0, (c.z_index||1) - 1);
      document.getElementById('propZ').value = c.z_index;
      CanvasManager.renderOne(c); DesignerState.dirty=true;
    });
    document.getElementById('btnDuplicate')?.addEventListener('click', () => DesignerCtrl.duplicateSelected());
    document.getElementById('btnDelete')?.addEventListener('click', () => DesignerCtrl.deleteSelected());
  }

  function _sel() { return DesignerState.getByUid(DesignerState.selectedId); }
  function _updPos() {
    const c = _sel(); if (!c) return;
    c.x = +document.getElementById('propX').value || 0;
    c.y = +document.getElementById('propY').value || 0;
    CanvasManager.renderOne(c); DesignerState.dirty=true;
  }
  function _updSize() {
    const c = _sel(); if (!c) return;
    c.width  = +document.getElementById('propW').value || 50;
    c.height = +document.getElementById('propH').value || 20;
    CanvasManager.renderOne(c); DesignerState.dirty=true;
  }
  function _updProp(key, val) {
    const c = _sel(); if (!c) return;
    c.properties[key] = val; CanvasManager.renderOne(c); DesignerState.dirty=true;
  }

  return { init, load, clear, refreshDynamic, syncPosition, syncSize };
})();


/* ═══════════════════════════════════════════════════════════
   EventsPanel / RulesPanel / OutlinePanel / PagesPanel (compact)
   ═══════════════════════════════════════════════════════════ */

const EventsPanel = (() => {
  let _evCat = {}; let _actCat = [];
  function init(ec, ac) { _evCat=ec; _actCat=ac; _attachBtns(); }

  function load(comp) {
    if (!comp) { clear(); return; }
    document.getElementById('eventsEmpty').style.display = 'none';
    document.getElementById('eventsForm').style.display  = '';
    _renderList(comp);
  }
  function clear() {
    document.getElementById('eventsEmpty').style.display = '';
    document.getElementById('eventsForm').style.display  = 'none';
  }
  function _renderList(comp) {
    const container = document.getElementById('eventsList');
    const events = comp.events || {};
    container.innerHTML = Object.entries(events).map(([ev, code]) =>
      `<div class="event-row" data-ev="${ev}">
         <i class="bi bi-lightning-charge"></i>
         <div class="row-body">
           <div class="row-name">${ev}</div>
           <div class="row-code">${code.substring(0,60)}${code.length>60?'…':''}</div>
         </div>
         <button class="btn-row-del" data-ev="${ev}"><i class="bi bi-x"></i></button>
       </div>`
    ).join('') || '<small class="text-muted px-2">Nenhum evento</small>';

    container.querySelectorAll('.btn-row-del').forEach(btn => {
      btn.addEventListener('click', () => {
        const uid = DesignerState.selectedId;
        const c   = DesignerState.getByUid(uid); if (!c) return;
        const ev  = btn.dataset.ev;
        delete c.events[ev];
        DesignerState.dirty = true;
        _renderList(c);
      });
    });
  }

  function _attachBtns() {
    document.getElementById('btnAddEvent')?.addEventListener('click', () => {
      const comp = DesignerState.getByUid(DesignerState.selectedId); if (!comp) return;
      // Populate event types
      const sel = document.getElementById('selEvent');
      const universalEvs = _evCat.universal || [];
      sel.innerHTML = universalEvs.map(e => `<option value="${e.name}">${e.label} (${e.name})</option>`).join('');

      // Populate actions
      const selAct = document.getElementById('selAction');
      selAct.innerHTML = '<option value="">— Código customizado —</option>' +
        _actCat.flatMap(g => g.actions.map(a =>
          `<option value="${a.id}" data-template="${encodeURIComponent(JSON.stringify(a))}">${g.group}: ${a.label}</option>`
        )).join('');

      selAct.addEventListener('change', () => {
        const opt = selAct.selectedOptions[0];
        if (!opt.value) { document.getElementById('actionParamsArea').style.display='none'; return; }
        const action = JSON.parse(decodeURIComponent(opt.dataset.template));
        const paramsArea = document.getElementById('actionParamsArea');
        paramsArea.style.display = action.params?.length ? '' : 'none';
        paramsArea.innerHTML = (action.params||[]).map(p =>
          `<div class="mb-2"><label class="form-label" style="font-size:11px;">${p.label}</label>
           ${p.type==='select'?
             `<select class="form-select form-select-sm bg-dark text-light border-secondary" data-param="${p.name}">
               ${(p.options||[]).map(o=>`<option value="${o}">${o}</option>`).join('')}</select>`
             :`<input type="${p.type||'text'}" class="form-control form-control-sm bg-dark text-light border-secondary"
               data-param="${p.name}" value="${p.default||''}">`}</div>`
        ).join('');

        // Auto-fill code template
        let code = action.template || '';
        (action.params||[]).forEach(p => {
          const input = paramsArea.querySelector(`[data-param="${p.name}"]`);
          code = code.replace(`{${p.name}}`, input?.value || p.default || '');
        });
        document.getElementById('eventCode').value = code;
      });

      new bootstrap.Modal(document.getElementById('modalAddEvent')).show();
    });

    document.getElementById('btnSaveEvent')?.addEventListener('click', () => {
      const uid  = DesignerState.selectedId;
      const comp = DesignerState.getByUid(uid); if (!comp) return;
      const ev   = document.getElementById('selEvent').value;
      const code = document.getElementById('eventCode').value.trim();
      if (ev && code) {
        comp.events[ev] = code;
        DesignerState.dirty = true;
        _renderList(comp);
      }
      bootstrap.Modal.getInstance(document.getElementById('modalAddEvent'))?.hide();
    });
  }

  return { init, load, clear };
})();


const RulesPanel = (() => {
  let _ruleCat = [];
  function init(rc) { _ruleCat=rc; _attachBtns(); }

  function load(comp) {
    if (!comp) { clear(); return; }
    document.getElementById('rulesEmpty').style.display = 'none';
    document.getElementById('rulesForm').style.display  = '';
    _renderList(comp);
  }
  function clear() {
    document.getElementById('rulesEmpty').style.display = '';
    document.getElementById('rulesForm').style.display  = 'none';
  }
  function _renderList(comp) {
    const container = document.getElementById('rulesList');
    const rules = comp.rules || [];
    container.innerHTML = rules.map((r, i) =>
      `<div class="rule-row" data-ri="${i}">
         <i class="bi bi-funnel"></i>
         <div class="row-body">
           <div class="row-name">${r.type||'Regra'}</div>
           <div class="row-code">${JSON.stringify(r.params||{}).substring(0,50)}</div>
         </div>
         <button class="btn-row-del" data-ri="${i}"><i class="bi bi-x"></i></button>
       </div>`
    ).join('') || '<small class="text-muted px-2">Nenhuma regra</small>';

    container.querySelectorAll('.btn-row-del').forEach(btn => {
      btn.addEventListener('click', () => {
        const c = DesignerState.getByUid(DesignerState.selectedId); if (!c) return;
        c.rules.splice(parseInt(btn.dataset.ri), 1);
        DesignerState.dirty = true;
        _renderList(c);
      });
    });
  }

  function _attachBtns() {
    document.getElementById('btnAddRule')?.addEventListener('click', () => {
      const sel = document.getElementById('selRule');
      sel.innerHTML = _ruleCat.flatMap(g => g.rules.map(r =>
        `<option value="${r.id}" data-rule='${JSON.stringify(r)}'>${g.group}: ${r.label}</option>`
      )).join('');

      sel.addEventListener('change', _buildRuleParams);
      _buildRuleParams.call(sel);
      new bootstrap.Modal(document.getElementById('modalAddRule')).show();
    });

    document.getElementById('btnSaveRule')?.addEventListener('click', () => {
      const comp = DesignerState.getByUid(DesignerState.selectedId); if (!comp) return;
      const sel  = document.getElementById('selRule');
      const opt  = sel.selectedOptions[0]; if (!opt) return;
      const rule = JSON.parse(opt.dataset.rule);
      const params = {};
      document.querySelectorAll('#ruleParamsArea [data-rparam]').forEach(el => {
        params[el.dataset.rparam] = el.value;
      });
      comp.rules.push({ type: rule.id, params });
      DesignerState.dirty = true;
      const c = DesignerState.getByUid(DesignerState.selectedId);
      if (c) _renderList(c);
      bootstrap.Modal.getInstance(document.getElementById('modalAddRule'))?.hide();
    });
  }

  function _buildRuleParams() {
    const opt = this.selectedOptions?.[0]; if (!opt) return;
    const rule = JSON.parse(opt.dataset.rule || '{}');
    const area = document.getElementById('ruleParamsArea');
    area.innerHTML = (rule.params||[]).map(p =>
      `<div class="mb-2"><label class="form-label" style="font-size:11px;">${p.label}</label>
       ${p.type==='select'?
         `<select class="form-select form-select-sm bg-dark text-light border-secondary" data-rparam="${p.name}">
            ${(p.options||[]).map(o=>`<option>${o}</option>`).join('')}</select>` :
         p.type==='textarea'?
         `<textarea class="form-control form-control-sm bg-dark text-light border-secondary" rows="3" data-rparam="${p.name}">${p.default||''}</textarea>`:
         `<input type="${p.type||'text'}" class="form-control form-control-sm bg-dark text-light border-secondary"
                 data-rparam="${p.name}" value="${p.default||''}">`}</div>`
    ).join('');
  }

  return { init, load, clear };
})();


const OutlinePanel = (() => {
  function init() {}
  function render() {
    const container = document.getElementById('outlineList'); if (!container) return;
    container.innerHTML = DesignerState.components.map(c => {
      const uid = c._uid || c.id;
      return `<div class="outline-item ${uid===DesignerState.selectedId?'active':''}" data-uid="${uid}">
                <i class="bi bi-dot"></i>
                <span>${c.name || c.type}</span>
                <small class="ms-auto text-muted" style="font-size:10px;">${c.type}</small>
              </div>`;
    }).join('') || '<small class="text-muted px-2 py-2 d-block">Canvas vazio</small>';

    container.querySelectorAll('.outline-item').forEach(el => {
      el.addEventListener('click', () => DesignerCtrl.select(el.dataset.uid));
    });
  }
  function highlight(uid) {
    document.querySelectorAll('.outline-item').forEach(el => {
      el.classList.toggle('active', el.dataset.uid === uid);
    });
  }
  return { init, render, highlight };
})();


const PagesPanel = (() => {
  function init() {
    // Clicar numa página → navega
    document.querySelectorAll('.page-item[data-pgid]').forEach(el => {
      el.addEventListener('click', () => {
        const pid  = el.dataset.pid;
        const pgid = el.dataset.pgid;
        window.location.href = `/designer/${pid}/${pgid}`;
      });
    });

    // Deletar página
    document.querySelectorAll('.btn-page-del').forEach(btn => {
      btn.addEventListener('click', async (e) => {
        e.stopPropagation();
        if (!confirm('Deletar esta página?')) return;
        const pgid = btn.dataset.pgid;
        const r = await fetch(`/paginas/${pgid}/deletar`, { method: 'POST' });
        const d = await r.json();
        if (d.ok) {
          window.location.href = `/designer/${window.DSB_CONFIG.projectId}`;
        } else { alert(d.error); }
      });
    });

    // Nova página
    document.getElementById('btnNewPage')?.addEventListener('click', async () => {
      const name = prompt('Nome da nova página:', 'Nova Página');
      if (!name) return;
      const r = await fetch(`/projetos/${window.DSB_CONFIG.projectId}/paginas/nova`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name }),
      });
      const d = await r.json();
      window.location.href = `/designer/${window.DSB_CONFIG.projectId}/${d.id}`;
    });

    // Troca de abas do painel esquerdo
    _initPanelTabs('leftPanel');
    _initPanelTabs('rightPanel');
  }

  function _initPanelTabs(panelId) {
    const panel = document.getElementById(panelId); if (!panel) return;
    panel.querySelectorAll('.ptab').forEach(btn => {
      btn.addEventListener('click', () => {
        const tabId = btn.dataset.tab;
        panel.querySelectorAll('.ptab').forEach(b => b.classList.remove('active'));
        panel.querySelectorAll('.panel-tab-content').forEach(t => t.classList.remove('active'));
        btn.classList.add('active');
        document.getElementById(tabId)?.classList.add('active');
      });
    });
  }

  return { init };
})();


/* ═══════════════════════════════════════════════════════════
   MenuBar — ações do menu superior
   ═══════════════════════════════════════════════════════════ */

const MenuBar = (() => {
  function init(cfg) {
    // Ações dos itens de menu
    document.querySelectorAll('[data-action]').forEach(el => {
      el.addEventListener('click', (e) => {
        e.preventDefault();
        _dispatch(el.dataset.action, cfg);
      });
    });

    // Botões da toolbar
    document.getElementById('btnSave')?.addEventListener('click',    () => DesignerCtrl.save());
    document.getElementById('btnUndo')?.addEventListener('click',    () => DesignerCtrl.undo());
    document.getElementById('btnRedo')?.addEventListener('click',    () => DesignerCtrl.redo());
    document.getElementById('btnGrid')?.addEventListener('click',    () => DesignerCtrl.toggleGrid());
    document.getElementById('btnPreview')?.addEventListener('click', () => window.open(cfg.previewUrl, '_blank'));
    document.getElementById('btnExport')?.addEventListener('click',  () => { window.location.href = cfg.exportUrl; });
    document.getElementById('btnZoomIn')?.addEventListener('click',  () => DesignerCtrl.applyZoom(DesignerState.zoom + .1));
    document.getElementById('btnZoomOut')?.addEventListener('click', () => DesignerCtrl.applyZoom(DesignerState.zoom - .1));
    document.getElementById('btnZoomReset')?.addEventListener('click',() => DesignerCtrl.applyZoom(1));

    // Renomear projeto
    document.getElementById('lblNome')?.addEventListener('click', async () => {
      const lbl  = document.getElementById('lblNome');
      const nome = prompt('Renomear projeto:', lbl.textContent);
      if (!nome) return;
      await fetch(cfg.renameUrl, { method:'POST', headers:{'Content-Type':'application/json'},
                                   body: JSON.stringify({name: nome}) });
      lbl.textContent = nome;
      document.title  = `Designer — ${nome}`;
    });

    // Click no canvas (deselect)
    document.getElementById('canvas')?.addEventListener('mousedown', (e) => {
      if (e.target === document.getElementById('canvas') ||
          e.target === document.getElementById('canvasHint')) {
        DesignerCtrl.deselect();
      }
    });
  }

  function _dispatch(action, cfg) {
    switch (action) {
      case 'save':          DesignerCtrl.save(); break;
      case 'undo':          DesignerCtrl.undo(); break;
      case 'redo':          DesignerCtrl.redo(); break;
      case 'preview':       window.open(cfg.previewUrl, '_blank'); break;
      case 'export_zip':    window.location.href = cfg.exportUrl; break;
      case 'new_project':   window.location.href = '/'; break;
      case 'zoom_in':       DesignerCtrl.applyZoom(DesignerState.zoom + .1); break;
      case 'zoom_out':      DesignerCtrl.applyZoom(DesignerState.zoom - .1); break;
      case 'zoom_reset':    DesignerCtrl.applyZoom(1); break;
      case 'toggle_grid':   DesignerCtrl.toggleGrid(); break;
      case 'duplicate':     DesignerCtrl.duplicateSelected(); break;
      case 'delete':        DesignerCtrl.deleteSelected(); break;
      case 'select_all':
        DesignerState.components.forEach(c => DesignerCtrl.select(c._uid||c.id));
        break;
      default:
        if (action.startsWith('insert:')) {
          const type = action.split(':')[1];
          DesignerCtrl.addComponent(type, 100, 100);
        }
    }
  }

  return { init };
})();


/* ═══════════════════════════════════════════════════════════
   ContextMenu
   ═══════════════════════════════════════════════════════════ */

const ContextMenu = (() => {
  let _uid = null;
  function init() {
    document.addEventListener('click', hide);
    document.querySelectorAll('.ctx-item[data-action]').forEach(el => {
      el.addEventListener('click', () => {
        const a = el.dataset.action;
        if (a === 'delete')        DesignerCtrl.deleteSelected();
        else if (a === 'duplicate') DesignerCtrl.duplicateSelected();
        else if (a === 'layer_up') {
          const c = DesignerState.getByUid(_uid); if (c) { c.z_index=(c.z_index||1)+1; CanvasManager.renderOne(c); }
        }
        else if (a === 'layer_dn') {
          const c = DesignerState.getByUid(_uid); if (c) { c.z_index=Math.max(0,(c.z_index||1)-1); CanvasManager.renderOne(c); }
        }
        else if (a === 'align_left')   DesignerCtrl.align('left');
        else if (a === 'align_center') DesignerCtrl.align('center');
        else if (a === 'align_right')  DesignerCtrl.align('right');
        hide();
      });
    });
  }
  function show(x, y, uid) {
    _uid = uid;
    const m = document.getElementById('ctxMenu');
    m.style.cssText = `display:block;left:${x}px;top:${y}px;`;
  }
  function hide() { document.getElementById('ctxMenu').style.display='none'; }
  return { init, show, hide };
})();


/* ═══════════════════════════════════════════════════════════
   PaletteDrag — drag from palette
   ═══════════════════════════════════════════════════════════ */

const PaletteDrag = (() => {
  function init(catalog) {
    document.querySelectorAll('.palette-item').forEach(el => {
      el.addEventListener('dragstart', e => {
        e.dataTransfer.setData('comp-type', el.dataset.type);
        e.dataTransfer.effectAllowed = 'copy';
      });
    });
    // Search filter
    document.getElementById('paletteSearch')?.addEventListener('input', e => {
      const q = e.target.value.toLowerCase();
      document.querySelectorAll('.palette-item').forEach(item => {
        const match = item.dataset.label?.toLowerCase().includes(q) ||
                      item.dataset.type?.toLowerCase().includes(q);
        item.classList.toggle('hidden', !match);
      });
      document.querySelectorAll('.palette-group').forEach(g => {
        const vis = [...g.querySelectorAll('.palette-item')].some(i => !i.classList.contains('hidden'));
        g.style.display = vis ? '' : 'none';
      });
    });
  }
  return { init };
})();


/* ═══════════════════════════════════════════════════════════
   CanvasDrop — drop onto canvas
   ═══════════════════════════════════════════════════════════ */

const CanvasDrop = (() => {
  function init(canvas, catalog) {
    canvas.addEventListener('dragover', e => {
      e.preventDefault();
      e.dataTransfer.dropEffect = 'copy';
      canvas.classList.add('drag-over');
    });
    canvas.addEventListener('dragleave', () => canvas.classList.remove('drag-over'));
    canvas.addEventListener('drop', e => {
      e.preventDefault();
      canvas.classList.remove('drag-over');
      const type = e.dataTransfer.getData('comp-type');
      if (!type) return;
      const rect = canvas.getBoundingClientRect();
      const z    = DesignerState.zoom;
      const x    = Math.round((e.clientX - rect.left) / z / 5) * 5;
      const y    = Math.round((e.clientY - rect.top)  / z / 5) * 5;
      const entry = catalog[type]; const sz = entry?.default_size || {width:150,height:40};
      DesignerCtrl.addComponent(type, Math.max(0, x - sz.width/2), Math.max(0, y - sz.height/2));
    });
  }
  return { init };
})();


/* ═══════════════════════════════════════════════════════════
   KeyBindings — atalhos de teclado
   ═══════════════════════════════════════════════════════════ */

const KeyBindings = (() => {
  function init() {
    document.addEventListener('keydown', e => {
      // Ignorar inputs
      if (['INPUT','TEXTAREA','SELECT'].includes(e.target.tagName) ||
          e.target.contentEditable === 'true') return;

      const ctrl = e.ctrlKey || e.metaKey;

      if (ctrl && e.key === 's') { e.preventDefault(); DesignerCtrl.save(); }
      if (ctrl && e.key === 'z') { e.preventDefault(); DesignerCtrl.undo(); }
      if (ctrl && (e.key === 'y' || (e.shiftKey && e.key === 'z'))) { e.preventDefault(); DesignerCtrl.redo(); }
      if (ctrl && e.key === 'd') { e.preventDefault(); DesignerCtrl.duplicateSelected(); }
      if (ctrl && e.key === 'a') { e.preventDefault(); }

      if (e.key === 'Delete' || e.key === 'Backspace') {
        if (DesignerState.selectedId) { e.preventDefault(); DesignerCtrl.deleteSelected(); }
      }
      if (e.key === 'Escape') DesignerCtrl.deselect();
      if (e.key === 'F5') { e.preventDefault(); ResponsivePreview.open(); }

      // Nudge com setas
      const nudge = e.shiftKey ? 10 : 2;
      const c = DesignerState.getByUid(DesignerState.selectedId);
      if (c) {
        if (e.key === 'ArrowLeft')  { e.preventDefault(); c.x -= nudge; }
        if (e.key === 'ArrowRight') { e.preventDefault(); c.x += nudge; }
        if (e.key === 'ArrowUp')    { e.preventDefault(); c.y -= nudge; }
        if (e.key === 'ArrowDown')  { e.preventDefault(); c.y += nudge; }
        if (['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.key)) {
          CanvasManager.renderOne(c);
          PropsPanel.syncPosition(c);
          DesignerState.dirty = true;
        }
      }
    });
  }
  return { init };
})();


/* ═══════════════════════════════════════════════════════════
   TemplateGallery — galeria de templates prontos
   ═══════════════════════════════════════════════════════════ */

const TemplateGallery = (() => {
  let _modal = null;

  /** Inicializa eventos do botão e modal */
  function init() {
    document.getElementById('btnTemplates')?.addEventListener('click', open);
  }

  async function open() {
    _modal = _modal || new bootstrap.Modal(document.getElementById('modalTemplates'));
    _modal.show();
    await _loadTemplates();
  }

  async function _loadTemplates() {
    const grid = document.getElementById('templateGrid');
    try {
      const r   = await fetch(window.DSB_CONFIG.templatesUrl);
      const d   = await r.json();
      const tpls = d.templates || [];

      // Agrupamento por categoria
      const cats = {};
      tpls.forEach(t => {
        if (!cats[t.category]) cats[t.category] = [];
        cats[t.category].push(t);
      });

      grid.innerHTML = Object.entries(cats).map(([cat, items]) => `
        <div class="col-12"><h6 class="text-muted mb-2" style="font-size:11px;text-transform:uppercase;letter-spacing:.7px;">${cat}</h6></div>
        ${items.map(t => `
          <div class="col-md-4">
            <div class="card bg-dark border-secondary template-card h-100"
                 data-id="${t.id}" style="cursor:pointer;transition:.15s;">
              <div class="card-body p-3">
                <div class="d-flex align-items-center gap-2 mb-2">
                  <i class="bi ${t.icon} fs-4 text-warning"></i>
                  <strong class="text-white" style="font-size:13px;">${t.name}</strong>
                </div>
                <p class="text-muted small mb-2">${t.description}</p>
                <small class="text-muted">
                  <i class="bi bi-grid-3x3-gap me-1"></i>${t.comp_count} componentes
                </small>
              </div>
              <div class="card-footer border-secondary d-flex gap-2">
                <button class="btn btn-sm btn-warning flex-fill btn-apply-tpl" data-id="${t.id}">
                  <i class="bi bi-lightning me-1"></i>Aplicar
                </button>
              </div>
            </div>
          </div>
        `).join('')}
      `).join('');

      // Hover effect
      grid.querySelectorAll('.template-card').forEach(card => {
        card.addEventListener('mouseenter', () => card.style.borderColor = '#ffc107');
        card.addEventListener('mouseleave', () => card.style.borderColor = '');
      });

      // Apply buttons
      grid.querySelectorAll('.btn-apply-tpl').forEach(btn => {
        btn.addEventListener('click', async () => {
          const id   = btn.dataset.id;
          const keep = document.getElementById('chkKeepExisting')?.checked;
          if (!keep && !confirm('Isso substituirá todos os componentes atuais. Continuar?')) return;

          btn.disabled = true;
          btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Aplicando...';

          const url = window.DSB_CONFIG.applyTplUrl.replace('{id}', id);
          const r   = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ keep_existing: keep }),
          });
          const d = await r.json();

          if (d.ok) {
            _modal.hide();
            // Reload page data
            const refreshed = await fetch(window.DSB_CONFIG.loadUrl).then(rx => rx.json());
            DesignerState.load(refreshed);
            // Apply canvas settings
            document.getElementById('inputCanvasBg').value = d.canvas_bg;
            document.getElementById('inputCanvasW').value  = d.canvas_w;
            document.getElementById('inputCanvasH').value  = d.canvas_h;
            CanvasManager.applyCanvasSettings(d.canvas_bg, d.canvas_w, d.canvas_h, true);
            CanvasManager.renderAll();
            OutlinePanel.render();
            const st = document.getElementById('statusSave');
            if (st) { st.textContent = `✓ Template "${id}" aplicado`; st.classList.add('save-flash'); }
          } else {
            alert('Erro ao aplicar template: ' + d.error);
          }
          btn.disabled = false;
          btn.innerHTML = '<i class="bi bi-lightning me-1"></i>Aplicar';
        });
      });
    } catch (err) {
      grid.innerHTML = `<div class="col-12 text-danger">Erro ao carregar templates: ${err.message}</div>`;
    }
  }

  return { init, open };
})();


/* ═══════════════════════════════════════════════════════════
   ImageManager — upload e seleção de imagens
   ═══════════════════════════════════════════════════════════ */

const ImageManager = (() => {
  let _modal       = null;
  let _selectedUrl = null;
  let _onSelect    = null;  // callback(url) quando usuário confirma

  function init() {
    const dropZone  = document.getElementById('uploadDropZone');
    const fileInput = document.getElementById('fileInputUpload');

    // Clique na drop zone → abre seletor
    dropZone?.addEventListener('click', () => fileInput?.click());

    // Drag & drop
    dropZone?.addEventListener('dragover', (e) => {
      e.preventDefault();
      dropZone.style.background = 'rgba(65,84,241,.15)';
    });
    dropZone?.addEventListener('dragleave', () => dropZone.style.background = '');
    dropZone?.addEventListener('drop', (e) => {
      e.preventDefault();
      dropZone.style.background = '';
      _uploadFiles(e.dataTransfer.files);
    });

    // Mudança no input de arquivo
    fileInput?.addEventListener('change', () => _uploadFiles(fileInput.files));

    // Botão "Usar imagem"
    document.getElementById('btnUseImage')?.addEventListener('click', () => {
      if (_selectedUrl && _onSelect) {
        _onSelect(_selectedUrl);
        _modal?.hide();
      }
    });
  }

  /** Abre o modal de imagens; callback é chamado com a URL quando o usuário seleciona */
  function open(onSelectCallback) {
    _onSelect    = onSelectCallback || null;
    _selectedUrl = null;
    document.getElementById('btnUseImage').disabled = true;
    document.getElementById('selectedImageUrl').textContent = '';
    _modal = _modal || new bootstrap.Modal(document.getElementById('modalImageUpload'));
    _modal.show();
    _loadGallery();
  }

  async function _uploadFiles(files) {
    if (!files || !files.length) return;
    const prog   = document.getElementById('uploadProgress');
    const status = document.getElementById('uploadStatus');
    prog.style.display = '';
    const bar = prog.querySelector('.progress-bar');

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      status.textContent = `Enviando ${file.name}...`;
      bar.style.width = Math.round((i / files.length) * 80) + '%';

      const fd = new FormData();
      fd.append('file', file);
      try {
        const r = await fetch(window.DSB_CONFIG.uploadUrl, { method: 'POST', body: fd });
        const d = await r.json();
        if (!d.ok) { alert('Erro: ' + d.error); }
      } catch (err) { alert('Erro no upload: ' + err.message); }
    }

    bar.style.width = '100%';
    status.textContent = 'Concluído!';
    setTimeout(() => { prog.style.display = 'none'; bar.style.width = '0%'; }, 1500);
    await _loadGallery();
    document.getElementById('fileInputUpload').value = '';
  }

  async function _loadGallery() {
    const gallery = document.getElementById('imageGallery');
    gallery.innerHTML = '<div class="col-12 text-center text-muted py-2"><span class="spinner-border spinner-border-sm"></span></div>';

    try {
      const r = await fetch(window.DSB_CONFIG.listUploadsUrl);
      const d = await r.json();

      if (!d.images || !d.images.length) {
        gallery.innerHTML = '<div class="col-12 text-center text-muted py-3"><i class="bi bi-images fs-3 d-block mb-2"></i>Nenhuma imagem enviada ainda</div>';
        return;
      }

      gallery.innerHTML = d.images.map(img => `
        <div class="col-md-3 col-sm-4 col-6">
          <div class="img-thumb-card border border-secondary rounded overflow-hidden"
               data-url="${img.url}" style="cursor:pointer;aspect-ratio:1;position:relative;transition:.15s;">
            <img src="${img.url}" style="width:100%;height:100%;object-fit:cover;"
                 onerror="this.src='https://placehold.co/120x120/333/999?text=ERR'">
            <div class="img-overlay" style="position:absolute;inset:0;background:rgba(0,0,0,.5);
                 opacity:0;transition:.15s;display:flex;align-items:center;justify-content:center;gap:6px;">
              <button class="btn btn-xs btn-light btn-use-img" data-url="${img.url}" title="Usar">
                <i class="bi bi-check-lg"></i>
              </button>
              <button class="btn btn-xs btn-danger btn-del-img" data-filename="${img.filename}" title="Deletar">
                <i class="bi bi-trash"></i>
              </button>
            </div>
            <div style="position:absolute;bottom:0;left:0;right:0;background:rgba(0,0,0,.6);
                 padding:2px 5px;font-size:9px;color:#ccc;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
              ${img.filename} (${img.size_kb}KB)
            </div>
          </div>
        </div>
      `).join('');

      // Hover effects
      gallery.querySelectorAll('.img-thumb-card').forEach(card => {
        card.addEventListener('mouseenter', () => {
          card.style.borderColor = '#4154f1';
          card.querySelector('.img-overlay').style.opacity = '1';
        });
        card.addEventListener('mouseleave', () => {
          card.style.borderColor = '';
          card.querySelector('.img-overlay').style.opacity = '0';
        });
      });

      // Use image
      gallery.querySelectorAll('.btn-use-img').forEach(btn => {
        btn.addEventListener('click', (e) => {
          e.stopPropagation();
          _selectedUrl = btn.dataset.url;
          document.getElementById('selectedImageUrl').textContent = _selectedUrl;
          document.getElementById('btnUseImage').disabled = false;
          gallery.querySelectorAll('.img-thumb-card').forEach(c => c.style.outline = '');
          btn.closest('.img-thumb-card').style.outline = '2px solid #4154f1';
        });
      });

      // Delete image
      gallery.querySelectorAll('.btn-del-img').forEach(btn => {
        btn.addEventListener('click', async (e) => {
          e.stopPropagation();
          if (!confirm('Deletar esta imagem?')) return;
          const r = await fetch(`/upload/imagem/${btn.dataset.filename}`, { method: 'DELETE' });
          const d = await r.json();
          if (d.ok) await _loadGallery();
          else alert('Erro: ' + d.error);
        });
      });
    } catch (err) {
      gallery.innerHTML = `<div class="col-12 text-danger">Erro: ${err.message}</div>`;
    }
  }

  return { init, open };
})();


/* ═══════════════════════════════════════════════════════════
   ResponsivePreview — preview com toggle de viewport
   ═══════════════════════════════════════════════════════════ */

const ResponsivePreview = (() => {
  let _modal = null;

  const VIEWPORTS = {
    desktop: { w: '100%',  label: 'Desktop (1280px)' },
    tablet:  { w: '768px', label: 'Tablet (768px)'   },
    mobile:  { w: '375px', label: 'Mobile (375px)'   },
  };

  function init() {
    // Override do botão de preview padrão
    document.getElementById('btnPreview')?.addEventListener('click', (e) => {
      e.stopImmediatePropagation();
      open();
    });

    // Viewport toggle buttons
    document.getElementById('viewportToggle')?.querySelectorAll('[data-vp]').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('#viewportToggle [data-vp]').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const vp = VIEWPORTS[btn.dataset.vp];
        const frame = document.getElementById('previewFrame');
        if (frame) {
          frame.style.width = vp.w;
          frame.style.minHeight = '80vh';
        }
        const lbl = document.getElementById('vpLabel');
        if (lbl) lbl.textContent = vp.label;
      });
    });
  }

  function open() {
    _modal = _modal || new bootstrap.Modal(document.getElementById('modalResponsivePreview'));

    // Build preview inline (saves then renders)
    const frame = document.getElementById('previewFrame');
    frame.style.width     = '100%';
    frame.style.minHeight = '80vh';
    frame.innerHTML       = '<div style="padding:40px;text-align:center;color:#666;"><span class="spinner-border"></span><br>Carregando preview...</div>';

    _modal.show();

    // After save, load preview in iframe
    DesignerCtrl.save(true).then(() => {
      const iframe = document.createElement('iframe');
      iframe.src    = window.DSB_CONFIG.previewUrl;
      iframe.style.cssText = 'width:100%;height:80vh;border:none;display:block;';
      frame.innerHTML = '';
      frame.appendChild(iframe);
    });
  }

  return { init, open };
})();


/* ═══════════════════════════════════════════════════════════
   BOOT
   ═══════════════════════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', () => {
  DesignerCtrl.init().then(() => {
    TemplateGallery.init();
    ImageManager.init();
    ResponsivePreview.init();
    // Sprint 3
    MultiSelect.init();
    LayersPanel.init();
    PageManager.initDuplicate();
  });
});


/* ═══════════════════════════════════════════════════════════
   SPRINT 3 — MultiSelect
   ═══════════════════════════════════════════════════════════
   Gerencia seleção múltipla de componentes no canvas.

   Métodos públicos:
     init()                   — inicializa eventos de canvas
     getSelectedUids()        → Set de uids selecionados
     isMultiMode()            → true se 2+ componentes selecionados
     add(uid)                 — adiciona uid à seleção múltipla
     remove(uid)              — remove uid da seleção múltipla
     clear()                  — limpa toda seleção múltipla
     selectAll()              — seleciona todos os componentes
     deleteSelected()         — remove todos selecionados
     duplicateSelected()      — duplica todos selecionados
     alignSelected(dir)       — alinha selecionados (left/center/right/top/bottom)
     moveSelected(dx,dy)      — desloca grupo em dx,dy pixels
   ═══════════════════════════════════════════════════════════ */

const MultiSelect = (() => {
  // Set de UIDs em seleção múltipla
  const _sel = new Set();

  // Estado do rubber-band
  let _rbActive  = false;
  let _rbStart   = { x: 0, y: 0 };
  let _rbEl      = null;
  let _canvasEl  = null;
  let _wrapEl    = null;

  // ── API pública ────────────────────────────────────────
  function getSelectedUids() { return new Set(_sel); }
  function isMultiMode()     { return _sel.size >= 2; }
  function has(uid)          { return _sel.has(uid); }

  function add(uid) {
    _sel.add(uid);
    _refreshVisuals();
    _refreshBadge();
    LayersPanel.render();
  }

  function remove(uid) {
    _sel.delete(uid);
    _refreshVisuals();
    _refreshBadge();
    LayersPanel.render();
  }

  function clear() {
    _sel.clear();
    _refreshVisuals();
    _refreshBadge();
    LayersPanel.render();
  }

  function selectAll() {
    _sel.clear();
    DesignerState.components.forEach(c => _sel.add(c._uid || c.id));
    DesignerState.deselect();
    _refreshVisuals();
    _refreshBadge();
    LayersPanel.render();
  }

  /** Deleta todos os componentes na seleção múltipla */
  function deleteSelected() {
    if (!_sel.size) return;
    DesignerState.pushUndo();
    const uids = new Set(_sel);
    uids.forEach(uid => {
      DesignerState.delete(uid);
      CanvasManager.removeEl(uid);
    });
    _sel.clear();
    _refreshBadge();
    OutlinePanel.render();
    LayersPanel.render();
    DesignerState.dirty = true;
  }

  /** Duplica todos os componentes da seleção */
  function duplicateSelected() {
    if (!_sel.size) return;
    const uids   = new Set(_sel);
    const clones = [];
    DesignerState.pushUndo();
    uids.forEach(uid => {
      const clone = DesignerState.duplicate(uid);
      if (clone) { clones.push(clone); CanvasManager.renderOne(clone); }
    });
    // Seleciona os clones
    _sel.clear();
    clones.forEach(c => _sel.add(c._uid));
    _refreshVisuals();
    _refreshBadge();
    OutlinePanel.render();
    LayersPanel.render();
  }

  /**
   * Alinha todos os selecionados em relação ao grupo ou canvas.
   * @param {string} dir — 'left'|'center'|'right'|'top'|'middle'|'bottom'
   */
  function alignSelected(dir) {
    if (_sel.size < 2) return;
    const comps  = [..._sel].map(uid => DesignerState.getByUid(uid)).filter(Boolean);
    const canvasW = parseInt(document.getElementById('inputCanvasW')?.value || 1280);
    const canvasH = parseInt(document.getElementById('inputCanvasH')?.value || 900);

    const minX   = Math.min(...comps.map(c => c.x));
    const maxX   = Math.max(...comps.map(c => c.x + c.width));
    const minY   = Math.min(...comps.map(c => c.y));
    const maxY   = Math.max(...comps.map(c => c.y + c.height));
    const groupW = maxX - minX;
    const groupH = maxY - minY;

    DesignerState.pushUndo();
    comps.forEach(c => {
      switch (dir) {
        case 'left':   c.x = 0;                              break;
        case 'center': c.x = Math.round((canvasW - c.width) / 2); break;
        case 'right':  c.x = canvasW - c.width;              break;
        case 'top':    c.y = 0;                              break;
        case 'middle': c.y = Math.round((canvasH - c.height) / 2); break;
        case 'bottom': c.y = canvasH - c.height;             break;
        // Relativos ao grupo:
        case 'group_left':   c.x = minX;                         break;
        case 'group_right':  c.x = maxX - c.width;               break;
        case 'group_top':    c.y = minY;                         break;
        case 'group_bottom': c.y = maxY - c.height;              break;
        case 'group_center': c.x = minX + Math.round((groupW - c.width)  / 2); break;
        case 'group_middle': c.y = minY + Math.round((groupH - c.height) / 2); break;
        // Distribuição equidistante:
        case 'dist_h':
          // Distribuído horizontalmente — calculado fora deste forEach
          break;
        case 'dist_v':
          break;
      }
      CanvasManager.renderOne(c);
    });

    // Distribuição equidistante requer ordenação
    if (dir === 'dist_h') {
      const sorted = [...comps].sort((a,b) => a.x - b.x);
      const totalW = sorted.reduce((s,c) => s + c.width, 0);
      const gap    = Math.round((groupW - totalW) / (sorted.length - 1));
      let  curX    = minX;
      sorted.forEach(c => { c.x = curX; curX += c.width + gap; CanvasManager.renderOne(c); });
    }
    if (dir === 'dist_v') {
      const sorted = [...comps].sort((a,b) => a.y - b.y);
      const totalH = sorted.reduce((s,c) => s + c.height, 0);
      const gap    = Math.round((groupH - totalH) / (sorted.length - 1));
      let  curY    = minY;
      sorted.forEach(c => { c.y = curY; curY += c.height + gap; CanvasManager.renderOne(c); });
    }

    DesignerState.dirty = true;
  }

  /** Desloca todos os selecionados dx,dy pixels */
  function moveSelected(dx, dy) {
    const comps = [..._sel].map(uid => DesignerState.getByUid(uid)).filter(Boolean);
    comps.forEach(c => {
      c.x += dx; c.y += dy;
      const el = document.querySelector(`[data-uid="${c._uid || c.id}"]`);
      if (el) { el.style.left = c.x + 'px'; el.style.top = c.y + 'px'; }
    });
    DesignerState.dirty = true;
  }

  // ── Visuals ───────────────────────────────────────────
  function _refreshVisuals() {
    document.querySelectorAll('.canvas-comp').forEach(el => {
      const uid = el.dataset.uid;
      el.classList.toggle('multi-selected', _sel.has(uid));
      // Se apenas 1 elemento no multisel, remove o highlight individual
      if (_sel.size === 1 && _sel.has(uid)) {
        el.classList.remove('multi-selected');
      }
    });
  }

  /** Mostra/oculta o badge flutuante com contagem e ações rápidas */
  function _refreshBadge() {
    const badge = document.getElementById('selectionBadge');
    if (!badge) return;
    const bar   = document.getElementById('multiSelectBar');

    if (_sel.size >= 2) {
      badge.style.display = 'flex';
      badge.innerHTML = `
        <span class="sb-count">${_sel.size} selecionados</span>
        <div class="sb-actions">
          <button class="sb-btn" id="sbDup"    title="Duplicar (Ctrl+D)"><i class="bi bi-copy"></i></button>
          <button class="sb-btn" id="sbAlignL" title="Alinhar à esquerda"><i class="bi bi-align-start"></i></button>
          <button class="sb-btn" id="sbAlignC" title="Centralizar"><i class="bi bi-align-center"></i></button>
          <button class="sb-btn" id="sbAlignR" title="Alinhar à direita"><i class="bi bi-align-end"></i></button>
          <button class="sb-btn" id="sbDistH"  title="Distribuir horizontal"><i class="bi bi-distribute-horizontal"></i></button>
          <button class="sb-btn" id="sbDistV"  title="Distribuir vertical"><i class="bi bi-distribute-vertical"></i></button>
          <button class="sb-btn danger" id="sbDel" title="Deletar seleção"><i class="bi bi-trash"></i></button>
        </div>
        <button class="sb-btn" id="sbClear" title="Limpar seleção (Esc)"><i class="bi bi-x-lg"></i></button>
      `;
      // Bind badge buttons
      badge.querySelector('#sbDup')?.addEventListener('click',    () => duplicateSelected());
      badge.querySelector('#sbAlignL')?.addEventListener('click', () => alignSelected('center')); // canvas center
      badge.querySelector('#sbAlignC')?.addEventListener('click', () => alignSelected('group_center'));
      badge.querySelector('#sbAlignR')?.addEventListener('click', () => alignSelected('group_right'));
      badge.querySelector('#sbDistH')?.addEventListener('click',  () => alignSelected('dist_h'));
      badge.querySelector('#sbDistV')?.addEventListener('click',  () => alignSelected('dist_v'));
      badge.querySelector('#sbDel')?.addEventListener('click',    () => deleteSelected());
      badge.querySelector('#sbClear')?.addEventListener('click',  () => clear());

      // Show Layers toolbar
      if (bar) {
        bar.style.display = 'flex';
        bar.querySelector('#multiSelectCount').textContent = `${_sel.size} selecionados`;
      }
      document.getElementById('btnLayersDelSel').style.display = '';
    } else {
      badge.style.display = 'none';
      if (bar) bar.style.display = 'none';
      document.getElementById('btnLayersDelSel').style.display = 'none';
    }
  }

  // ── Rubber-band selection ─────────────────────────────
  function init() {
    _canvasEl = document.getElementById('canvas');
    _wrapEl   = document.getElementById('canvasScrollWrap');
    _rbEl     = document.getElementById('rubberBand');

    // Teclado: Escape limpa multi, Ctrl+A seleciona tudo
    document.addEventListener('keydown', _onKeyDown);

    // Mouse down no canvas (fora de um componente) → inicia rubber band
    _canvasEl.addEventListener('mousedown', _onCanvasMouseDown);

    // Botões do Layers toolbar
    document.getElementById('btnLayersSelAll')?.addEventListener('click', selectAll);
    document.getElementById('btnLayersDelSel')?.addEventListener('click', deleteSelected);
    document.getElementById('btnMultiDup')?.addEventListener('click',    duplicateSelected);
    document.getElementById('btnMultiAlignL')?.addEventListener('click', () => alignSelected('group_left'));
    document.getElementById('btnMultiAlignC')?.addEventListener('click', () => alignSelected('group_center'));
    document.getElementById('btnMultiAlignR')?.addEventListener('click', () => alignSelected('group_right'));
    document.getElementById('btnMultiDel')?.addEventListener('click',    deleteSelected);

    // Shift+Click em componente → toggle na seleção múltipla
    _canvasEl.addEventListener('mousedown', (e) => {
      if (!e.shiftKey) return;
      const comp = e.target.closest('.canvas-comp');
      if (!comp) return;
      e.stopPropagation();
      const uid = comp.dataset.uid;
      if (_sel.has(uid)) {
        _sel.delete(uid);
        comp.classList.remove('multi-selected');
      } else {
        _sel.add(uid);
        comp.classList.add('multi-selected');
        // Deselect the single selection
        DesignerCtrl.deselect();
      }
      _refreshBadge();
      LayersPanel.render();
    }, true);
  }

  function _onKeyDown(e) {
    if (['INPUT','TEXTAREA','SELECT'].includes(e.target.tagName) ||
        e.target.contentEditable === 'true') return;

    const ctrl = e.ctrlKey || e.metaKey;

    if (e.key === 'Escape' && _sel.size) { e.preventDefault(); clear(); }

    if (ctrl && e.key === 'a') {
      e.preventDefault();
      selectAll();
    }

    if ((e.key === 'Delete' || e.key === 'Backspace') && _sel.size >= 2) {
      e.preventDefault();
      deleteSelected();
    }

    if (ctrl && e.key === 'd' && _sel.size >= 2) {
      e.preventDefault();
      duplicateSelected();
    }

    // Arrow nudge for multi-selection
    if (_sel.size >= 2) {
      const nudge = e.shiftKey ? 10 : 2;
      if (e.key === 'ArrowLeft')  { e.preventDefault(); moveSelected(-nudge, 0); }
      if (e.key === 'ArrowRight') { e.preventDefault(); moveSelected( nudge, 0); }
      if (e.key === 'ArrowUp')    { e.preventDefault(); moveSelected(0, -nudge); }
      if (e.key === 'ArrowDown')  { e.preventDefault(); moveSelected(0,  nudge); }
    }
  }

  function _onCanvasMouseDown(e) {
    // Só inicia rubber-band se clicar diretamente no canvas (não em componente)
    if (e.target !== _canvasEl && e.target !== document.getElementById('canvasHint')) return;
    if (e.button !== 0) return;
    if (e.shiftKey) return; // Shift+click tem comportamento próprio

    // Se não é Ctrl, limpa seleção
    if (!e.ctrlKey) {
      clear();
      DesignerCtrl.deselect();
    }

    _rbActive = true;
    const rect  = _canvasEl.getBoundingClientRect();
    const z     = DesignerState.zoom;
    _rbStart = {
      x: (e.clientX - rect.left) / z,
      y: (e.clientY - rect.top)  / z,
    };

    _rbEl.style.cssText = `display:block;left:${_rbStart.x}px;top:${_rbStart.y}px;width:0;height:0;`;

    const onMove = (me) => {
      if (!_rbActive) return;
      const curX = (me.clientX - rect.left) / z;
      const curY = (me.clientY - rect.top)  / z;
      const x    = Math.min(_rbStart.x, curX);
      const y    = Math.min(_rbStart.y, curY);
      const w    = Math.abs(curX - _rbStart.x);
      const h    = Math.abs(curY - _rbStart.y);
      _rbEl.style.left   = x + 'px';
      _rbEl.style.top    = y + 'px';
      _rbEl.style.width  = w + 'px';
      _rbEl.style.height = h + 'px';
    };

    const onUp = () => {
      if (!_rbActive) return;
      _rbActive = false;
      _rbEl.style.display = 'none';

      // Detect which components are inside the rubber-band rect
      const rbRect = _rbEl.getBoundingClientRect();
      if (rbRect.width < 4 && rbRect.height < 4) {
        // Too small — just a click, don't select
        document.removeEventListener('mousemove', onMove);
        document.removeEventListener('mouseup',   onUp);
        return;
      }

      DesignerState.components.forEach(c => {
        const el = document.querySelector(`[data-uid="${c._uid || c.id}"]`);
        if (!el) return;
        const er = el.getBoundingClientRect();
        // Check if component intersects rubber-band
        if (er.left < rbRect.right  && er.right  > rbRect.left &&
            er.top  < rbRect.bottom && er.bottom > rbRect.top) {
          _sel.add(c._uid || c.id);
        }
      });

      _refreshVisuals();
      _refreshBadge();
      LayersPanel.render();
      document.removeEventListener('mousemove', onMove);
      document.removeEventListener('mouseup',   onUp);
    };

    document.addEventListener('mousemove', onMove);
    document.addEventListener('mouseup',   onUp);
  }

  return {
    init, getSelectedUids, isMultiMode, has,
    add, remove, clear, selectAll,
    deleteSelected, duplicateSelected,
    alignSelected, moveSelected,
  };
})();


/* ═══════════════════════════════════════════════════════════
   SPRINT 3 — LayersPanel
   ═══════════════════════════════════════════════════════════
   Painel de camadas com:
   - Lista de componentes ordenada por z-index (reversa — topo primeiro)
   - Drag para reordenar z-index
   - Toggle de visibilidade (temporário, não persiste no servidor)
   - Toggle de lock (impede drag/resize no canvas)
   - Seleção múltipla integrada com MultiSelect
   - Rename inline com duplo clique
   ═══════════════════════════════════════════════════════════ */

const LayersPanel = (() => {
  // Map uid → {hidden: bool, locked: bool}
  const _meta = new Map();
  let   _dragSrcUid = null;

  // Ícones por tipo de componente
  const TYPE_ICONS = {
    button:'bi-app', textbox:'bi-input-cursor-text', textarea:'bi-textarea',
    numberbox:'bi-123', checkbox:'bi-check-square', radiobutton:'bi-record-circle',
    combobox:'bi-menu-button-wide', switch:'bi-toggle-on', slider:'bi-sliders',
    datepicker:'bi-calendar3', rating:'bi-star-half', fileupload:'bi-upload',
    label:'bi-paragraph', heading:'bi-type-h1', image:'bi-image', icon:'bi-star',
    badge:'bi-tag', progressbar:'bi-bar-chart-steps', statusbar:'bi-info-circle',
    separator:'bi-hr', spinner:'bi-arrow-repeat',
    panel:'bi-bounding-box', card:'bi-card-text', groupbox:'bi-collection',
    tabs:'bi-folder-symlink', accordion:'bi-layout-accordion-collapsed',
    datagrid:'bi-table', chart:'bi-bar-chart', pagination:'bi-arrow-left-right',
    alert:'bi-info-circle', modal:'bi-window-stack',
    navbar:'bi-layout-text-sidebar-reverse', breadcrumb:'bi-chevron-right',
    stepper:'bi-list-ol', timer:'bi-alarm', countdown:'bi-stopwatch',
  };

  function init() {
    // Layer list is rendered after each change via render()
  }

  /** Renderiza a lista de layers completa */
  function render() {
    const container = document.getElementById('layersList');
    if (!container) return;

    // Ordena z-index decrescente (topo da lista = frente do canvas)
    const comps = [...DesignerState.components]
      .sort((a, b) => (b.z_index || 1) - (a.z_index || 1));

    if (!comps.length) {
      container.innerHTML = '<div class="text-muted px-3 py-3" style="font-size:11px;">Nenhum componente na página</div>';
      return;
    }

    const selUid    = DesignerState.selectedId;
    const multiSel  = MultiSelect.getSelectedUids();

    container.innerHTML = comps.map(c => {
      const uid     = c._uid || c.id;
      const meta    = _meta.get(uid) || {};
      const isHid   = !!meta.hidden;
      const isLock  = !!meta.locked;
      const isSel   = selUid === uid;
      const isMulti = multiSel.has(uid);
      const icon    = TYPE_ICONS[c.type] || 'bi-puzzle';

      return `
        <div class="layer-item
             ${isSel   ? 'selected-layer' : ''}
             ${isMulti ? 'multi-layer'    : ''}
             ${isHid   ? 'hidden-layer'   : ''}
             ${isLock  ? 'locked-layer'   : ''}"
             data-uid="${uid}"
             draggable="true"
             title="z-index: ${c.z_index || 1}">
          <i class="bi bi-grip-vertical layer-drag-handle"></i>
          <i class="bi ${icon} layer-icon"></i>
          <span class="layer-name" data-uid="${uid}">${c.name || c.type}</span>
          <div class="layer-actions">
            <button class="layer-btn ${isHid ? '' : 'active-vis'} btn-layer-vis"
                    data-uid="${uid}" title="${isHid ? 'Mostrar' : 'Ocultar'}">
              <i class="bi ${isHid ? 'bi-eye-slash' : 'bi-eye'}"></i>
            </button>
            <button class="layer-btn ${isLock ? 'active-lock' : ''} btn-layer-lock"
                    data-uid="${uid}" title="${isLock ? 'Desbloquear' : 'Bloquear'}">
              <i class="bi ${isLock ? 'bi-lock-fill' : 'bi-unlock'}"></i>
            </button>
            <button class="layer-btn danger btn-layer-del"
                    data-uid="${uid}" title="Deletar">
              <i class="bi bi-x"></i>
            </button>
          </div>
        </div>
      `;
    }).join('');

    _attachLayerEvents(container);
  }

  function _attachLayerEvents(container) {
    // ── Clique → select (com Shift para multi) ──────────
    container.querySelectorAll('.layer-item').forEach(el => {
      el.addEventListener('click', (e) => {
        if (e.target.closest('.layer-actions')) return;
        if (e.target.closest('.layer-drag-handle')) return;
        const uid = el.dataset.uid;
        const meta = _meta.get(uid) || {};
        if (meta.locked) return;

        if (e.shiftKey) {
          if (MultiSelect.has(uid)) MultiSelect.remove(uid);
          else { MultiSelect.add(uid); DesignerCtrl.deselect(); }
        } else {
          MultiSelect.clear();
          DesignerCtrl.select(uid);
        }
      });
    });

    // ── Duplo clique → rename inline ───────────────────
    container.querySelectorAll('.layer-name').forEach(span => {
      span.addEventListener('dblclick', (e) => {
        e.stopPropagation();
        const uid  = span.dataset.uid;
        const comp = DesignerState.getByUid(uid);
        if (!comp) return;
        const input = document.createElement('input');
        input.className   = 'layer-name-input';
        input.value       = comp.name;
        span.replaceWith(input);
        input.focus(); input.select();
        const finish = () => {
          const newName = input.value.trim() || comp.name;
          comp.name = newName;
          DesignerState.dirty = true;
          CanvasManager.renderOne(comp);
          render();
          // Sync to props panel if this comp is selected
          if (DesignerState.selectedId === uid) {
            document.getElementById('propName').value = newName;
          }
        };
        input.addEventListener('blur', finish);
        input.addEventListener('keydown', e => {
          if (e.key === 'Enter') input.blur();
          if (e.key === 'Escape') { comp.name = comp.name; input.blur(); }
        });
      });
    });

    // ── Visibility toggle ──────────────────────────────
    container.querySelectorAll('.btn-layer-vis').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const uid  = btn.dataset.uid;
        const meta = _meta.get(uid) || {};
        meta.hidden = !meta.hidden;
        _meta.set(uid, meta);
        const canvasEl = document.querySelector(`[data-uid="${uid}"]`);
        if (canvasEl) canvasEl.style.opacity = meta.hidden ? '0.1' : '';
        render();
      });
    });

    // ── Lock toggle ────────────────────────────────────
    container.querySelectorAll('.btn-layer-lock').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const uid  = btn.dataset.uid;
        const meta = _meta.get(uid) || {};
        meta.locked = !meta.locked;
        _meta.set(uid, meta);
        // Apply/remove interact.js on canvas element
        const canvasEl = document.querySelector(`[data-uid="${uid}"]`);
        if (canvasEl) {
          canvasEl.style.cursor = meta.locked ? 'not-allowed' : 'move';
          canvasEl.style.outline = meta.locked ? '2px dashed #ff9800' : '';
          // Disable interact if locked
          if (meta.locked) interact(canvasEl).draggable(false).resizable(false);
          else {
            const comp = DesignerState.getByUid(uid);
            // Re-init interact (CanvasManager will re-render on next renderOne call)
            if (comp) CanvasManager.renderOne(comp);
          }
        }
        render();
      });
    });

    // ── Delete ─────────────────────────────────────────
    container.querySelectorAll('.btn-layer-del').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const uid = btn.dataset.uid;
        DesignerState.delete(uid);
        CanvasManager.removeEl(uid);
        MultiSelect.remove(uid);
        _meta.delete(uid);
        render();
        OutlinePanel.render();
      });
    });

    // ── Drag to reorder (z-index) ──────────────────────
    container.querySelectorAll('.layer-item[draggable]').forEach(el => {
      el.addEventListener('dragstart', (e) => {
        _dragSrcUid = el.dataset.uid;
        e.dataTransfer.effectAllowed = 'move';
        setTimeout(() => el.style.opacity = '.4', 0);
      });
      el.addEventListener('dragend',   () => {
        el.style.opacity = '';
        container.querySelectorAll('.layer-item').forEach(i => i.classList.remove('dragging-over-top'));
      });
      el.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
        container.querySelectorAll('.layer-item').forEach(i => i.classList.remove('dragging-over-top'));
        el.classList.add('dragging-over-top');
      });
      el.addEventListener('drop', (e) => {
        e.preventDefault();
        if (_dragSrcUid === el.dataset.uid) return;
        _reorderLayers(_dragSrcUid, el.dataset.uid);
      });
    });
  }

  /** Reordena z-indexes após drag */
  function _reorderLayers(srcUid, targetUid) {
    // Layers are displayed top→bottom (highest z-index first)
    const comps  = [...DesignerState.components]
      .sort((a,b) => (b.z_index||1) - (a.z_index||1));
    const srcIdx = comps.findIndex(c => (c._uid||c.id) === srcUid);
    const tgtIdx = comps.findIndex(c => (c._uid||c.id) === targetUid);
    if (srcIdx === -1 || tgtIdx === -1) return;

    DesignerState.pushUndo();
    // Splice source out and insert before target
    const [srcComp] = comps.splice(srcIdx, 1);
    const insertAt  = tgtIdx > srcIdx ? tgtIdx - 1 : tgtIdx;
    comps.splice(insertAt, 0, srcComp);

    // Re-assign z-indexes (comps[0] = top = highest z-index)
    comps.forEach((c, i) => {
      c.z_index = comps.length - i;
      CanvasManager.renderOne(c);
    });
    DesignerState.dirty = true;
    render();
  }

  /** Retorna se um uid está bloqueado */
  function isLocked(uid) {
    return !!(_meta.get(uid) || {}).locked;
  }

  return { init, render, isLocked };
})();


/* ═══════════════════════════════════════════════════════════
   SPRINT 3 — PageManager (Duplicate Page)
   ═══════════════════════════════════════════════════════════ */

const PageManager = (() => {

  function initDuplicate() {
    document.getElementById('btnDupPage')?.addEventListener('click', async () => {
      const btn  = document.getElementById('btnDupPage');
      const pgid = window.DSB_CONFIG.pageId;

      btn.disabled = true;
      btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';

      try {
        const r = await fetch(`/paginas/${pgid}/duplicar`, { method: 'POST' });
        const d = await r.json();
        if (d.ok) {
          // Navigate to the new duplicated page
          window.location.href = d.redirect_url;
        } else {
          alert('Erro ao duplicar página: ' + (d.error || 'Erro desconhecido'));
        }
      } catch (err) {
        alert('Erro: ' + err.message);
      } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-copy"></i>';
      }
    });
  }

  return { initDuplicate };
})();
