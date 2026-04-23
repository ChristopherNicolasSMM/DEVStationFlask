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
      if (e.key === 'F5') { e.preventDefault(); window.open(window.DSB_CONFIG.previewUrl, '_blank'); }

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
   BOOT
   ═══════════════════════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', () => DesignerCtrl.init());
