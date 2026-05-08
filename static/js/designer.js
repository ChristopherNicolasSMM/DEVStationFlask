/**
 * designer.js — Canvas Engine v3.0.2
 * =====================================
 * Correções v3.0.2:
 *  - Overlay transparente sobre cada componente: impede que elementos
 *    filhos (button, input, select) consumam eventos de mouse antes
 *    do drag/resize chegar ao container — resolve o problema de
 *    componentes existentes "presos" no canvas.
 *  - Toolbar completa: Desfazer, Refazer, Grade visual, Snap ao grid.
 *  - Botões do painel direito (Duplicar, Deletar, Z-up, Z-down) corrigidos.
 */

(function () {
  "use strict";

  /* ── Configuração ─────────────────────────────────────────── */
  const GRID_SIZE   = 8;
  const MIN_W       = 40;
  const MIN_H       = 24;

  /* ── Estado global ────────────────────────────────────────── */
  let _canvas     = null;
  let _components = [];      // Array de objetos {id,type,name,x,y,w,h,z,props}
  let _selected   = null;    // id do componente selecionado
  let _zoom       = 1.0;
  let _snapOn     = true;
  let _gridOn     = true;
  let _undoStack  = [];
  let _redoStack  = [];
  let _tmpId      = 0;
  let _config     = {};

  /* ── Mapa de tamanhos padrão ─────────────────────────────── */
  const SIZE = {
    button:{w:150,h:40}, textbox:{w:220,h:38}, textarea:{w:260,h:100},
    numberbox:{w:160,h:38}, combobox:{w:220,h:38}, checkbox:{w:160,h:30},
    switch:{w:160,h:30}, datepicker:{w:200,h:38}, slider:{w:240,h:40},
    rating:{w:150,h:36}, fileupload:{w:220,h:38},
    label:{w:220,h:36}, heading:{w:320,h:48}, image:{w:300,h:200},
    icon:{w:50,h:50}, badge:{w:80,h:28}, progressbar:{w:280,h:28},
    statusbar:{w:300,h:32}, separator:{w:300,h:10}, spinner:{w:50,h:50},
    panel:{w:320,h:180}, card:{w:300,h:200}, groupbox:{w:300,h:160},
    tabs:{w:400,h:200}, accordion:{w:360,h:150},
    datagrid:{w:480,h:200}, chart:{w:400,h:260}, pagination:{w:280,h:40},
    alert:{w:340,h:56}, modal:{w:200,h:40},
    navbar:{w:600,h:56}, breadcrumb:{w:280,h:32}, stepper:{w:480,h:60},
    timer:{w:150,h:40}, countdown:{w:150,h:60},
  };

  /* ── Cores por tipo ──────────────────────────────────────── */
  const COLOR = {
    button:"#4154f1", textbox:"#17a2b8", textarea:"#17a2b8",
    numberbox:"#17a2b8", combobox:"#6f42c1", checkbox:"#20c997",
    switch:"#20c997", datepicker:"#fd7e14", slider:"#6610f2",
    label:"#6c757d", heading:"#012970", image:"#0d6efd",
    icon:"#ffc107", badge:"#198754", progressbar:"#0d6efd",
    statusbar:"#198754", separator:"#adb5bd", spinner:"#4154f1",
    panel:"#dee2e6", card:"#4154f1", groupbox:"#6c757d",
    tabs:"#0d6efd", accordion:"#6c757d", datagrid:"#dc3545",
    chart:"#6f42c1", pagination:"#0d6efd", alert:"#ffc107",
    modal:"#0d6efd", navbar:"#012970", breadcrumb:"#6c757d",
    stepper:"#0d6efd", timer:"#ffc107", countdown:"#dc3545",
    rating:"#ffc107", fileupload:"#17a2b8",
  };

  /* ── Init ─────────────────────────────────────────────────── */

  function init() {
    _config = window.DSB_DESIGNER_CONFIG || {};
    _canvas = document.getElementById("canvas");
    if (!_canvas) return;

    _injectGridStyle();
    _bindPalette();
    _bindCanvasBackground();
    _bindToolbar();
    _bindPropsPanel();
    _bindKeyboard();
    _updateZoom();
    if (_config.pageId) _loadFromServer();
  }

  /* ── Grade visual ────────────────────────────────────────── */

  function _injectGridStyle() {
    const style = document.createElement("style");
    style.id = "dsb-grid-style";
    style.textContent = `
      .canvas-grid-on {
        background-image:
          linear-gradient(to right, #e8edff 1px, transparent 1px),
          linear-gradient(to bottom, #e8edff 1px, transparent 1px) !important;
        background-size: ${GRID_SIZE}px ${GRID_SIZE}px !important;
      }
      .dsb-comp { position:absolute; box-sizing:border-box; }
      .dsb-comp:hover .drag-overlay { background: rgba(65,84,241,.04); }
      .dsb-selected-ring {
        outline: 2px solid var(--sel-color, #4154f1);
        box-shadow: 0 0 0 3px rgba(65,84,241,.18);
      }
    `;
    document.head.appendChild(style);

    if (_gridOn) _canvas.classList.add("canvas-grid-on");
  }

  /* ── Paleta → canvas ─────────────────────────────────────── */

  function _bindPalette() {
    document.querySelectorAll(".pal-item").forEach(function (item) {
      item.addEventListener("dragstart", function (e) {
        e.dataTransfer.setData("dsb/type",  item.dataset.type  || "label");
        e.dataTransfer.setData("dsb/label", item.dataset.label || "Componente");
        e.dataTransfer.effectAllowed = "copy";
      });
    });

    _canvas.addEventListener("dragover", function (e) {
      e.preventDefault();
      e.dataTransfer.dropEffect = "copy";
    });

    _canvas.addEventListener("drop", function (e) {
      e.preventDefault();
      const type  = e.dataTransfer.getData("dsb/type");
      const label = e.dataTransfer.getData("dsb/label");
      if (!type) return;

      const rect = _canvas.getBoundingClientRect();
      const sz   = SIZE[type] || {w:150,h:40};
      const rawX = (e.clientX - rect.left) / _zoom - sz.w / 2;
      const rawY = (e.clientY - rect.top)  / _zoom - sz.h / 2;

      _pushUndo();
      const comp = _makeComp({
        type, label,
        x: Math.max(0, _snap(rawX)),
        y: Math.max(0, _snap(rawY)),
        w: sz.w, h: sz.h,
        z: _components.length + 1,
        props: { text: label },
      });
      _addComp(comp);
      _select(comp.id);
      _hideHint();
      _refreshOutline();
    });
  }

  /* ── Criação de componente ───────────────────────────────── */

  function _makeComp(data) {
    return {
      id:    data.id   || ("t" + (++_tmpId)),
      type:  data.type || "label",
      name:  data.name || data.label || (data.type + _tmpId),
      x:     data.x || 0,
      y:     data.y || 0,
      w:     data.w || 150,
      h:     data.h || 40,
      z:     data.z || 1,
      props: data.props || {},
    };
  }

  function _addComp(comp) {
    _components.push(comp);
    _renderEl(comp);
  }

  /* ── Renderização do elemento DOM ────────────────────────── */

  function _renderEl(comp) {
    const existing = document.getElementById("ec_" + comp.id);
    if (existing) existing.remove();

    const color = COLOR[comp.type] || "#6c757d";
    const el    = document.createElement("div");
    el.id                = "ec_" + comp.id;
    el.dataset.compId    = comp.id;
    el.className         = "dsb-comp";
    el.style.cssText     = `
      left:${comp.x}px; top:${comp.y}px;
      width:${comp.w}px; min-height:${comp.h}px;
      z-index:${comp.z};
      border:1px solid ${color}40;
      border-radius:4px;
      background:${color}0d;
    `;

    /* ── Conteúdo visual (pointer-events:none impede roubo de eventos) ── */
    const content       = document.createElement("div");
    content.className   = "comp-content";
    content.style.cssText = "position:absolute;inset:0;pointer-events:none;overflow:hidden;";
    content.innerHTML   = _buildPreview(comp);
    el.appendChild(content);

    /* ── Label de nome (exibe ao selecionar) ──────────────────── */
    const nameLabel         = document.createElement("div");
    nameLabel.className     = "comp-name-label";
    nameLabel.textContent   = comp.name;
    nameLabel.style.cssText = `
      display:none; position:absolute; top:-17px; left:0;
      font-size:9px; background:${color}; color:#fff;
      padding:1px 5px; border-radius:2px; white-space:nowrap;
      pointer-events:none; z-index:10;
    `;
    el.appendChild(nameLabel);

    /* ── Overlay de drag (cobre tudo, captura mouse) ──────────── */
    const overlay       = document.createElement("div");
    overlay.className   = "drag-overlay";
    overlay.style.cssText = `
      position:absolute; inset:0; z-index:5;
      cursor:move; border-radius:3px;
    `;
    overlay.addEventListener("mousedown", _onDragStart);
    el.appendChild(overlay);

    /* ── Handle de resize (canto inferior direito) ─────────────── */
    const handle        = document.createElement("div");
    handle.className    = "resize-handle";
    handle.style.cssText = `
      display:none; position:absolute; right:0; bottom:0;
      width:12px; height:12px; z-index:6; cursor:se-resize;
      border-right:2px solid ${color}cc; border-bottom:2px solid ${color}cc;
    `;
    handle.addEventListener("mousedown", _onResizeStart);
    el.appendChild(handle);

    _canvas.appendChild(el);
  }

  /* ── Prévia visual ───────────────────────────────────────── */

  function _buildPreview(comp) {
    const c   = COLOR[comp.type] || "#6c757d";
    const txt = comp.props.text || comp.name;

    const map = {
      button:     `<button style="background:${c};color:#fff;border:none;padding:5px 14px;border-radius:4px;font-size:12px;width:100%;height:100%;">${txt}</button>`,
      textbox:    `<div style="border:1px solid #ccc;border-radius:3px;padding:5px 8px;font-size:11px;background:#fff;height:100%;display:flex;align-items:center;color:#aaa;">${comp.props.placeholder||comp.props.label||'Texto...'}</div>`,
      textarea:   `<div style="border:1px solid #ccc;border-radius:3px;padding:5px;font-size:11px;background:#fff;height:100%;color:#aaa;">Área de texto...</div>`,
      numberbox:  `<div style="border:1px solid #ccc;border-radius:3px;padding:5px 8px;font-size:11px;background:#fff;height:100%;display:flex;align-items:center;color:#aaa;">0</div>`,
      combobox:   `<div style="border:1px solid #ccc;border-radius:3px;padding:5px 8px;font-size:11px;background:#fff;height:100%;display:flex;align-items:center;justify-content:space-between;color:#aaa;">${comp.props.placeholder||'Selecione...'}<span>▾</span></div>`,
      checkbox:   `<div style="display:flex;align-items:center;gap:6px;height:100%;padding:0 6px;font-size:12px;"><span style="width:14px;height:14px;border:1px solid #ccc;display:inline-block;border-radius:2px;background:#fff;"></span>${txt}</div>`,
      switch:     `<div style="display:flex;align-items:center;gap:6px;height:100%;padding:0 6px;font-size:12px;"><span style="width:28px;height:14px;border-radius:7px;background:${c};display:inline-block;position:relative;"><span style="position:absolute;right:1px;top:1px;width:12px;height:12px;border-radius:50%;background:#fff;"></span></span>${txt}</div>`,
      datepicker: `<div style="border:1px solid #ccc;border-radius:3px;padding:5px 8px;font-size:11px;background:#fff;height:100%;display:flex;align-items:center;gap:6px;color:#aaa;">📅 Data</div>`,
      slider:     `<div style="padding:14px 8px;"><div style="height:4px;background:#e0e0e0;border-radius:2px;position:relative;"><div style="position:absolute;left:0;width:50%;height:100%;background:${c};border-radius:2px;"></div></div></div>`,
      rating:     `<div style="display:flex;align-items:center;height:100%;padding:0 4px;gap:2px;color:${c};font-size:18px;">${'★'.repeat(comp.props.value||3)}${'☆'.repeat((comp.props.max||5)-(comp.props.value||3))}</div>`,
      fileupload: `<div style="border:1px solid #ccc;border-radius:3px;padding:5px 8px;font-size:11px;background:#fff;height:100%;display:flex;align-items:center;gap:5px;color:#aaa;">📎 Escolher arquivo</div>`,
      label:      `<div style="font-size:${comp.props.font_size||13}px;color:${comp.props.text_color||'#333'};padding:4px 6px;height:100%;display:flex;align-items:center;">${txt}</div>`,
      heading:    `<div style="font-size:${comp.props.font_size||22}px;font-weight:700;color:${comp.props.text_color||'#012970'};padding:4px 6px;height:100%;display:flex;align-items:center;">${txt}</div>`,
      image:      `<div style="width:100%;height:100%;background:#e8edff;display:flex;align-items:center;justify-content:center;border-radius:3px;"><i class="bi bi-image" style="font-size:2rem;color:${c};opacity:.5;"></i></div>`,
      icon:       `<div style="display:flex;align-items:center;justify-content:center;height:100%;"><i class="bi ${comp.props.icon_class||'bi-star-fill'}" style="font-size:${comp.props.size||26}px;color:${comp.props.color||c};"></i></div>`,
      badge:      `<div style="height:100%;display:flex;align-items:center;"><span style="background:${c};color:#fff;padding:3px 10px;border-radius:10px;font-size:11px;">${txt}</span></div>`,
      progressbar:`<div style="height:100%;display:flex;align-items:center;padding:0 4px;"><div style="flex:1;height:18px;background:#e9ecef;border-radius:9px;overflow:hidden;"><div style="width:60%;height:100%;background:${c};border-radius:9px;"></div></div></div>`,
      statusbar:  `<div style="background:#d1e7dd;color:#0a3622;padding:4px 10px;border-radius:3px;font-size:11px;height:100%;display:flex;align-items:center;gap:6px;">✓ ${txt}</div>`,
      separator:  `<div style="display:flex;align-items:center;height:100%;"><hr style="flex:1;border:none;border-top:2px solid #dee2e6;"></div>`,
      spinner:    `<div style="display:flex;align-items:center;justify-content:center;height:100%;"><div style="width:22px;height:22px;border:3px solid ${c}30;border-top-color:${c};border-radius:50%;"></div></div>`,
      panel:      `<div style="width:100%;height:100%;background:#f8f9fa;border:1px dashed #ccc;border-radius:3px;display:flex;align-items:center;justify-content:center;color:#aaa;font-size:11px;">Painel</div>`,
      card:       `<div style="width:100%;height:100%;border-radius:5px;overflow:hidden;"><div style="background:${c};color:#fff;padding:6px 10px;font-size:11px;font-weight:600;">${comp.props.title||'Card'}</div><div style="padding:8px;font-size:10px;color:#666;">${comp.props.body||'Conteúdo...'}</div></div>`,
      groupbox:   `<fieldset style="border:1px solid #ccc;border-radius:3px;width:100%;height:100%;padding:4px 8px;"><legend style="font-size:10px;padding:0 5px;color:#666;">${comp.props.title||'Grupo'}</legend></fieldset>`,
      tabs:       `<div><div style="display:flex;border-bottom:1px solid #dee2e6;">${(comp.props.tabs||['Aba 1','Aba 2']).map((t,i)=>`<div style="padding:5px 12px;font-size:11px;${i===0?'border-bottom:2px solid '+c+';color:'+c:'color:#999'}">${t}</div>`).join('')}</div></div>`,
      accordion:  `<div>${(comp.props.sections||['Seção 1','Seção 2']).slice(0,3).map(s=>`<div style="border:1px solid #dee2e6;border-radius:3px;margin-bottom:2px;padding:6px 10px;font-size:11px;display:flex;justify-content:space-between;">${s}<span style="color:#999;">▾</span></div>`).join('')}</div>`,
      datagrid:   `<div style="overflow:hidden;height:100%;"><table style="width:100%;border-collapse:collapse;font-size:10px;"><thead style="background:#343a40;color:#fff;"><tr>${(comp.props.columns||['ID','Nome','Valor']).map(c=>`<th style="padding:3px 6px;text-align:left;">${c}</th>`).join('')}</tr></thead><tbody>${(comp.props.rows||[['1','Item A','—']]).slice(0,3).map(r=>`<tr>${r.map(v=>`<td style="padding:3px 6px;border-bottom:1px solid #eee;">${v}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`,
      chart:      `<div style="height:100%;display:flex;align-items:center;justify-content:center;background:#f0f4ff;border-radius:3px;"><i class="bi bi-bar-chart-fill" style="font-size:2.5rem;color:${c};opacity:.45;"></i></div>`,
      pagination: `<div style="display:flex;gap:3px;align-items:center;height:100%;padding:0 4px;">${['«','1','2','3','»'].map((n,i)=>`<span style="padding:3px 8px;border:1px solid ${i===1?c:'#dee2e6'};border-radius:3px;font-size:11px;background:${i===1?c:'#fff'};color:${i===1?'#fff':'inherit'}">${n}</span>`).join('')}</div>`,
      alert:      `<div style="background:${c}22;border-left:4px solid ${c};padding:8px 12px;border-radius:3px;font-size:11px;height:100%;display:flex;align-items:center;">ⓘ ${txt}</div>`,
      modal:      `<button style="background:${c};color:#fff;border:none;padding:5px 14px;border-radius:4px;font-size:11px;">${comp.props.trigger_label||'Abrir Modal'}</button>`,
      navbar:     `<div style="background:${c};padding:6px 12px;display:flex;align-items:center;gap:12px;height:100%;border-radius:3px;"><span style="color:#fff;font-weight:600;font-size:12px;">${comp.props.brand||'Marca'}</span><span style="color:rgba(255,255,255,.75);font-size:11px;">Link</span></div>`,
      breadcrumb: `<div style="display:flex;align-items:center;gap:4px;height:100%;font-size:11px;">${(comp.props.items||['Início','Página']).map((it,i,a)=>`<span style="color:${i===a.length-1?'#666':'#0d6efd'}">${it}</span>${i<a.length-1?'<span style="color:#aaa"> / </span>':''}`).join('')}</div>`,
      stepper:    `<div style="display:flex;align-items:center;height:100%;">${(comp.props.steps||['1','2','3']).map((s,i,a)=>`<div style="text-align:center;"><div style="width:22px;height:22px;border-radius:50%;background:${i===0?c:'#dee2e6'};color:${i===0?'#fff':'#888'};display:inline-flex;align-items:center;justify-content:center;font-size:10px;">${i+1}</div><div style="font-size:9px;color:#888;margin-top:2px;">${s}</div></div>${i<a.length-1?`<div style="flex:1;height:2px;background:#dee2e6;margin-bottom:8px;"></div>`:''}`).join('')}</div>`,
      timer:      `<div style="background:#fff3cd;border:1px solid #ffc107;padding:5px 10px;border-radius:3px;font-size:11px;height:100%;display:flex;align-items:center;gap:5px;">⏱ ${comp.props.label||'Timer'}(${comp.props.interval_ms||1000}ms)</div>`,
      countdown:  `<div style="display:flex;align-items:center;justify-content:center;height:100%;"><span style="font-size:${comp.props.font_size||26}px;font-weight:700;color:${c};font-family:monospace;">01:00</span></div>`,
    };
    return map[comp.type] || `<div style="padding:6px;font-size:11px;color:#666;height:100%;display:flex;align-items:center;gap:5px;"><span style="color:${c};">●</span>${comp.name}</div>`;
  }

  /* ── Seleção ─────────────────────────────────────────────── */

  function _select(id) {
    // Limpa seleção anterior
    document.querySelectorAll(".dsb-comp").forEach(function (el) {
      el.classList.remove("dsb-selected-ring");
      el.style.outline    = "";
      el.style.boxShadow  = "";
      const h = el.querySelector(".resize-handle");
      const l = el.querySelector(".comp-name-label");
      if (h) h.style.display = "none";
      if (l) l.style.display = "none";
    });

    _selected = id;
    if (!id) { _showPropsEmpty(); return; }

    const comp  = _find(id);
    const color = COLOR[(comp && comp.type)] || "#4154f1";
    const el    = document.getElementById("ec_" + id);
    if (el) {
      el.style.outline   = `2px solid ${color}`;
      el.style.boxShadow = `0 0 0 3px ${color}22`;
      const h = el.querySelector(".resize-handle");
      const l = el.querySelector(".comp-name-label");
      if (h) h.style.display = "block";
      if (l) l.style.display = "block";
    }
    if (comp) _updatePropsForm(comp);
  }

  function _find(id) {
    return _components.find(function (c) { return c.id === id; });
  }

  /* ── Drag de componente ──────────────────────────────────── */

  let _drag = null;  // {compId, offX, offY}

  function _onDragStart(e) {
    if (e.button !== 0) return;
    e.stopPropagation();

    const el     = e.currentTarget.parentElement;
    const compId = el.dataset.compId;
    _select(compId);
    _pushUndo();

    const comp  = _find(compId);
    const rect  = _canvas.getBoundingClientRect();
    _drag = {
      compId,
      offX: (e.clientX - rect.left) / _zoom - comp.x,
      offY: (e.clientY - rect.top)  / _zoom - comp.y,
    };

    document.addEventListener("mousemove", _onDragMove);
    document.addEventListener("mouseup",   _onDragEnd);
  }

  function _onDragMove(e) {
    if (!_drag) return;
    const comp = _find(_drag.compId);
    const rect = _canvas.getBoundingClientRect();
    comp.x = Math.max(0, _snap((e.clientX - rect.left) / _zoom - _drag.offX));
    comp.y = Math.max(0, _snap((e.clientY - rect.top)  / _zoom - _drag.offY));
    const el = document.getElementById("ec_" + _drag.compId);
    if (el) { el.style.left = comp.x + "px"; el.style.top = comp.y + "px"; }
    _syncPropsXY(comp);
  }

  function _onDragEnd() {
    _drag = null;
    document.removeEventListener("mousemove", _onDragMove);
    document.removeEventListener("mouseup",   _onDragEnd);
  }

  /* ── Resize de componente ────────────────────────────────── */

  let _resize = null;  // {compId, startX, startY, startW, startH}

  function _onResizeStart(e) {
    e.stopPropagation();
    e.preventDefault();
    const compId  = e.currentTarget.parentElement.dataset.compId;
    const comp    = _find(compId);
    _pushUndo();
    _resize = { compId, startX:e.clientX, startY:e.clientY,
                startW:comp.w, startH:comp.h };
    document.addEventListener("mousemove", _onResizeMove);
    document.addEventListener("mouseup",   _onResizeEnd);
  }

  function _onResizeMove(e) {
    if (!_resize) return;
    const comp = _find(_resize.compId);
    const dx   = (e.clientX - _resize.startX) / _zoom;
    const dy   = (e.clientY - _resize.startY) / _zoom;
    comp.w     = Math.max(MIN_W, _snap(_resize.startW + dx));
    comp.h     = Math.max(MIN_H, _snap(_resize.startH + dy));
    const el   = document.getElementById("ec_" + _resize.compId);
    if (el) { el.style.width = comp.w + "px"; el.style.minHeight = comp.h + "px"; }
    _syncPropsWH(comp);
  }

  function _onResizeEnd() {
    _resize = null;
    document.removeEventListener("mousemove", _onResizeMove);
    document.removeEventListener("mouseup",   _onResizeEnd);
  }

  /* ── Click no fundo do canvas → deseleciona ─────────────── */

  // Vinculado após criação do canvas
  function _bindCanvasBackground() {
    _canvas.addEventListener("mousedown", function (e) {
      if (e.target === _canvas) _select(null);
    });
    // Zoom por Ctrl+Scroll
    var area = document.getElementById("canvasArea");
    if (area) {
      area.addEventListener("wheel", function (e) {
        if (!e.ctrlKey) return;
        e.preventDefault();
        _setZoom(_zoom + (e.deltaY > 0 ? -0.1 : 0.1));
      }, { passive: false });
    }
  }

  /* ── Painel de propriedades ──────────────────────────────── */

  function _showPropsEmpty() {
    var empty = document.getElementById("propsEmpty");
    var form  = document.getElementById("propsForm");
    if (empty) empty.style.display = "";
    if (form)  form.style.display  = "none";
  }

  function _updatePropsForm(comp) {
    var empty = document.getElementById("propsEmpty");
    var form  = document.getElementById("propsForm");
    if (empty) empty.style.display = "none";
    if (form)  form.style.display  = "";

    _setVal("propName", comp.name);
    _setVal("propType", comp.type);
    _setVal("propX",    comp.x);
    _setVal("propY",    comp.y);
    _setVal("propW",    comp.w);
    _setVal("propH",    comp.h);
    _setVal("propZ",    comp.z);

    // Renderiza propriedades dinâmicas
    var dyn = document.getElementById("dynamicProps");
    if (!dyn) return;
    var entries = Object.entries(comp.props).slice(0, 8);
    dyn.innerHTML = entries.map(function (kv) {
      var k = kv[0]; var v = kv[1];
      var isColor  = typeof v === "string" && /^#[0-9a-fA-F]{3,6}$/.test(v);
      var isBool   = typeof v === "boolean";
      if (isColor) return `<div class="props-row"><div class="props-col">
        <label class="props-label">${k}</label>
        <input type="color" class="props-input" style="height:28px;padding:2px;" value="${v}"
               data-key="${k}" onchange="DSBDesigner.setProp('${comp.id}','${k}',this.value)">
      </div></div>`;
      if (isBool) return `<div class="props-row"><div class="props-col">
        <label class="props-label">${k}</label>
        <input type="checkbox" ${v?'checked':''} data-key="${k}"
               onchange="DSBDesigner.setProp('${comp.id}','${k}',this.checked)">
      </div></div>`;
      return `<div class="props-row"><div class="props-col">
        <label class="props-label">${k}</label>
        <input type="text" class="props-input" value="${v||''}" data-key="${k}"
               onchange="DSBDesigner.setProp('${comp.id}','${k}',this.value)">
      </div></div>`;
    }).join("");
  }

  function _syncPropsXY(comp) {
    _setVal("propX", comp.x); _setVal("propY", comp.y);
  }
  function _syncPropsWH(comp) {
    _setVal("propW", comp.w); _setVal("propH", comp.h);
  }
  function _setVal(id, v) {
    var el = document.getElementById(id);
    if (el && el.value !== String(v)) el.value = v;
  }

  function _bindPropsPanel() {
    // Mudanças de layout via inputs
    var map = {
      propX: function(v){ _setCompField("x", parseInt(v)||0, "left"); },
      propY: function(v){ _setCompField("y", parseInt(v)||0, "top"); },
      propW: function(v){ _setCompField("w", Math.max(MIN_W,parseInt(v)||MIN_W), "width"); },
      propH: function(v){ _setCompField("h", Math.max(MIN_H,parseInt(v)||MIN_H), "minHeight"); },
      propZ: function(v){ _setCompField("z", parseInt(v)||1, "zIndex"); },
      propName: function(v){ if (_selected) { var c=_find(_selected); if(c) c.name=v; } },
    };
    Object.keys(map).forEach(function(id) {
      var el = document.getElementById(id);
      if (el) el.addEventListener("change", function(){ map[id](this.value); });
    });

    // Z up/down
    var zUp   = document.getElementById("btnZUp");
    var zDown = document.getElementById("btnZDown");
    if (zUp)   zUp.addEventListener("click", function(){
      if (!_selected) return;
      var c = _find(_selected); if (c) _setCompField("z", (c.z||1)+1, "zIndex");
    });
    if (zDown) zDown.addEventListener("click", function(){
      if (!_selected) return;
      var c = _find(_selected); if (c) _setCompField("z", Math.max(0,(c.z||1)-1), "zIndex");
    });

    // Duplicar / Deletar
    var btnDup = document.getElementById("btnDuplicate");
    var btnDel = document.getElementById("btnDelete");
    if (btnDup) btnDup.addEventListener("click", _duplicate);
    if (btnDel) btnDel.addEventListener("click", _delete);
  }

  function _setCompField(field, val, cssKey) {
    if (!_selected) return;
    var comp = _find(_selected);
    if (!comp) return;
    _pushUndo();
    comp[field] = val;
    var el = document.getElementById("ec_" + _selected);
    if (el && cssKey) el.style[cssKey] = val + (cssKey === "zIndex" ? "" : "px");
    _setVal("prop" + field.charAt(0).toUpperCase() + field.slice(1), val);
  }

  /* ── Toolbar ─────────────────────────────────────────────── */

  function _bindToolbar() {
    // Undo / Redo
    var btnUndo = document.getElementById("btnUndo");
    var btnRedo = document.getElementById("btnRedo");
    if (btnUndo) btnUndo.addEventListener("click", _undo);
    if (btnRedo) btnRedo.addEventListener("click", _redo);

    // Grade visual
    var btnGrid = document.getElementById("btnGrid");
    if (btnGrid) {
      _syncToolbarBtn(btnGrid, _gridOn);
      btnGrid.addEventListener("click", function () {
        _gridOn = !_gridOn;
        _canvas.classList.toggle("canvas-grid-on", _gridOn);
        _syncToolbarBtn(btnGrid, _gridOn);
      });
    }

    // Snap
    var btnSnap = document.getElementById("btnSnap");
    if (btnSnap) {
      _syncToolbarBtn(btnSnap, _snapOn);
      btnSnap.addEventListener("click", function () {
        _snapOn = !_snapOn;
        _syncToolbarBtn(btnSnap, _snapOn);
        _showToast("Snap " + (_snapOn ? "ativado" : "desativado"), "info");
      });
    }

    // Zoom
    var zIn    = document.getElementById("btnZoomIn");
    var zOut   = document.getElementById("btnZoomOut");
    var zReset = document.getElementById("btnZoomReset");
    if (zIn)    zIn.addEventListener("click",    function(){ _setZoom(_zoom + 0.1); });
    if (zOut)   zOut.addEventListener("click",   function(){ _setZoom(_zoom - 0.1); });
    if (zReset) zReset.addEventListener("click", function(){ _setZoom(1.0); });

    // Canvas tamanho / cor
    var cW  = document.getElementById("inputCanvasW");
    var cH  = document.getElementById("inputCanvasH");
    var cBg = document.getElementById("inputCanvasBg");
    if (cW) cW.addEventListener("change", function(){ _canvas.style.width = this.value + "px"; });
    if (cH) cH.addEventListener("change", function(){ _canvas.style.minHeight = this.value + "px"; });
    if (cBg) cBg.addEventListener("input", function(){ _canvas.style.background = this.value; });

    // Nova página
    var btnNP = document.getElementById("btnNewPage");
    if (btnNP) btnNP.addEventListener("click", function() {
      var name = prompt("Nome da nova página:", "Nova Página");
      if (!name) return;
      fetch("/api/projetos/" + _config.projectId + "/paginas", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({name: name}),
      }).then(function(r){ return r.json(); })
        .then(function(pg) {
          var list = document.getElementById("pagesList");
          if (list) {
            var item = document.createElement("div");
            item.className  = "page-item";
            item.dataset.pgid = pg.id;
            item.innerHTML  = `<i class="bi bi-file-earmark-text"></i><span style="flex:1;">${pg.name}</span>`;
            item.addEventListener("click", function(){
              window.location.href = "/designer/" + _config.projectId + "/" + pg.id;
            });
            list.appendChild(item);
          }
          _showToast("Página '" + name + "' criada.", "success");
        });
    });

    // Clique em páginas existentes
    document.querySelectorAll(".page-item").forEach(function(item) {
      item.addEventListener("click", function() {
        var pgid = item.dataset.pgid;
        if (pgid && pgid !== String(_config.pageId)) {
          window.location.href = "/designer/" + _config.projectId + "/" + pgid;
        }
      });
    });
  }

  function _syncToolbarBtn(btn, active) {
    if (active) {
      btn.style.background  = "#4154f1";
      btn.style.color       = "#fff";
      btn.style.borderColor = "#4154f1";
    } else {
      btn.style.background  = "";
      btn.style.color       = "";
      btn.style.borderColor = "";
    }
  }

  /* ── Undo / Redo ─────────────────────────────────────────── */

  function _pushUndo() {
    _undoStack.push(JSON.stringify(_components));
    _redoStack = [];
    if (_undoStack.length > 60) _undoStack.shift();
  }

  function _undo() {
    if (!_undoStack.length) return;
    _redoStack.push(JSON.stringify(_components));
    _restoreState(JSON.parse(_undoStack.pop()));
    _showToast("Desfeito", "info");
  }

  function _redo() {
    if (!_redoStack.length) return;
    _undoStack.push(JSON.stringify(_components));
    _restoreState(JSON.parse(_redoStack.pop()));
    _showToast("Refeito", "info");
  }

  function _restoreState(state) {
    _components = state;
    _select(null);
    document.querySelectorAll(".dsb-comp").forEach(function(el){ el.remove(); });
    _components.forEach(_renderEl);
    _refreshOutline();
    if (_components.length) _hideHint(); else _showHint();
  }

  /* ── Duplicar / Deletar ──────────────────────────────────── */

  function _duplicate() {
    if (!_selected) return;
    var src = _find(_selected);
    if (!src) return;
    _pushUndo();
    var copy = _makeComp({
      type:  src.type,
      name:  src.name + "_copia",
      x:     src.x + 16, y: src.y + 16,
      w:     src.w,       h: src.h,
      z:     src.z + 1,
      props: JSON.parse(JSON.stringify(src.props)),
    });
    _addComp(copy);
    _select(copy.id);
    _refreshOutline();
  }

  function _delete() {
    if (!_selected) return;
    _pushUndo();
    _components = _components.filter(function(c){ return c.id !== _selected; });
    var el = document.getElementById("ec_" + _selected);
    if (el) el.remove();
    _select(null);
    _refreshOutline();
    if (!_components.length) _showHint();
  }

  /* ── Zoom ─────────────────────────────────────────────────── */

  function _setZoom(z) {
    _zoom = Math.min(3.0, Math.max(0.2, parseFloat(z.toFixed(1))));
    _canvas.style.transform       = "scale(" + _zoom + ")";
    _canvas.style.transformOrigin = "top left";
    _updateZoom();
  }

  function _updateZoom() {
    var lbl = document.getElementById("zoomLabel");
    if (lbl) lbl.textContent = Math.round(_zoom * 100) + "%";
  }

  /* ── Snap ─────────────────────────────────────────────────── */

  function _snap(v) {
    return _snapOn ? Math.round(v / GRID_SIZE) * GRID_SIZE : Math.round(v);
  }

  /* ── Atalhos de teclado ──────────────────────────────────── */

  function _bindKeyboard() {
    document.addEventListener("keydown", function (e) {
      if (["INPUT","TEXTAREA","SELECT"].includes(e.target.tagName)) return;

      if (e.ctrlKey && e.key === "z") { e.preventDefault(); _undo(); }
      if (e.ctrlKey && e.key === "y") { e.preventDefault(); _redo(); }
      if (e.ctrlKey && e.key === "d") { e.preventDefault(); _duplicate(); }
      if (e.key === "Delete" || e.key === "Backspace") { e.preventDefault(); _delete(); }
      if (e.key === "Escape") _select(null);

      if (_selected && ["ArrowUp","ArrowDown","ArrowLeft","ArrowRight"].includes(e.key)) {
        e.preventDefault();
        var step = e.shiftKey ? 10 : 2;
        var comp = _find(_selected);
        if (!comp) return;
        _pushUndo();
        if (e.key === "ArrowLeft")  comp.x = Math.max(0, comp.x - step);
        if (e.key === "ArrowRight") comp.x += step;
        if (e.key === "ArrowUp")    comp.y = Math.max(0, comp.y - step);
        if (e.key === "ArrowDown")  comp.y += step;
        var el = document.getElementById("ec_" + _selected);
        if (el) { el.style.left = comp.x + "px"; el.style.top = comp.y + "px"; }
        _syncPropsXY(comp);
      }
    });
  }

  /* ── Outline ─────────────────────────────────────────────── */

  function _refreshOutline() {
    var list = document.getElementById("outlineList");
    if (!list) return;
    list.innerHTML = _components.map(function(c) {
      var col = COLOR[c.type] || "#666";
      return `<div style="padding:5px 10px;cursor:pointer;display:flex;align-items:center;gap:6px;font-size:.78rem;border-radius:3px;"
                   onclick="DSBDesigner.selectById('${c.id}')"
                   onmouseover="this.style.background='#1e2340'"
                   onmouseout="this.style.background=''">
               <span style="width:8px;height:8px;border-radius:50%;background:${col};display:inline-block;flex-shrink:0;"></span>
               <span style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${c.name}</span>
               <span style="color:#445;font-size:.7rem;">${c.type}</span>
             </div>`;
    }).join("") || '<div style="padding:10px;color:#445;font-size:.75rem;">Sem componentes.</div>';
  }

  /* ── Carregar do servidor ────────────────────────────────── */

  function _loadFromServer() {
    fetch("/api/paginas/" + _config.pageId)
      .then(function(r){ return r.json(); })
      .then(function(page) {
        var list = page.components || [];
        list.forEach(function(c) {
          var comp = _makeComp({
            id:    c.id,
            type:  c.type,
            name:  c.name,
            x:     c.x,
            y:     c.y,
            w:     c.width,
            h:     c.height,
            z:     c.z_index,
            props: c.properties || {},
          });
          _addComp(comp);
        });
        if (list.length) { _hideHint(); _refreshOutline(); } else _showHint();
      })
      .catch(function(e){ console.error("[DSBDesigner] load error:", e); });
  }

  /* ── Canvas hint ─────────────────────────────────────────── */

  function _hideHint() {
    var h = document.getElementById("canvasHint");
    if (h) h.style.display = "none";
  }
  function _showHint() {
    var h = document.getElementById("canvasHint");
    if (h) h.style.display = "";
  }

  /* ── Toast ───────────────────────────────────────────────── */

  function _showToast(msg, type) {
    if (window.dsToast) { window.dsToast(msg, type); return; }
    var c = document.getElementById("dsToastContainer");
    if (!c) {
      c = document.createElement("div");
      c.id = "dsToastContainer";
      c.style.cssText = "position:fixed;bottom:56px;right:20px;z-index:9999;display:flex;flex-direction:column;gap:6px;";
      document.body.appendChild(c);
    }
    var t = document.createElement("div");
    var bg = {success:"#1a7a4a", danger:"#c0392b", info:"#0d47a1"}[type] || "#333";
    t.style.cssText = `background:${bg};color:#fff;padding:9px 14px;border-radius:5px;font-size:.82rem;box-shadow:0 3px 10px rgba(0,0,0,.3);`;
    t.textContent   = msg;
    c.appendChild(t);
    setTimeout(function(){ t.remove(); }, 2800);
  }

  /* ── API pública ─────────────────────────────────────────── */

  window.DSBDesigner = {
    selectById: function(id) { _select(id); },

    setProp: function(id, key, val) {
      var comp = _find(id);
      if (!comp) return;
      comp.props[key] = val;
      // Re-renderiza conteúdo sem mover o elemento
      var el = document.getElementById("ec_" + id);
      if (el) {
        var content = el.querySelector(".comp-content");
        if (content) content.innerHTML = _buildPreview(comp);
      }
    },

    getComponents: function() {
      return _components.map(function(c) {
        return {
          id:         (typeof c.id === "string" && c.id.startsWith("t")) ? undefined : c.id,
          type:       c.type,
          name:       c.name,
          x:          c.x,
          y:          c.y,
          width:      c.w,
          height:     c.h,
          z_index:    c.z,
          properties: c.props || {},
          events:     {},
          rules:      [],
        };
      });
    },

    getSelectedProps: function() {
      if (!_selected) return {};
      var c = _find(_selected);
      return c ? c.props : {};
    },

    reloadCanvas: function() {
      _components = [];
      _select(null);
      document.querySelectorAll(".dsb-comp").forEach(function(el){ el.remove(); });
      _loadFromServer();
    },

    reloadPages: function() {
      setTimeout(function(){ window.location.reload(); }, 400);
    },

    showToast: _showToast,
  };

  /* ── Boot ─────────────────────────────────────────────────── */

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

})();
