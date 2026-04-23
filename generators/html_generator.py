"""
generators/html_generator.py — Gerador de HTML
================================================
Converte os componentes de uma Página em HTML exportável.
Suporta dois modos:
  inline_css / inline_js = True  → tudo num único arquivo (preview)
  inline_css / inline_js = False → referencia style.css e app.js (zip)
"""

from components import ComponentRegistry


class HtmlGenerator:
    """Gera o HTML completo de uma Página."""

    # CDNs usados nas páginas exportadas (Bootstrap + Bootstrap Icons + Chart.js)
    _CDN_CSS = [
        "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css",
        "https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css",
    ]
    _CDN_JS = [
        "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js",
        "https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js",
    ]

    def __init__(self, project, page):
        self.project = project
        self.page    = page

    def render(self, inline_css: bool = True, inline_js: bool = True) -> str:
        """
        Monta o documento HTML completo.
        inline_css: embute CSS; False = link para style.css
        inline_js:  embute JS;  False = link para app.js
        """
        title = self.page.title or self.page.name or self.project.name
        w  = self.page.canvas_w  or self.project.canvas_w  or 1280
        h  = self.page.canvas_h  or self.project.canvas_h  or 900
        bg = self.page.canvas_bg or self.project.canvas_bg or "#ffffff"

        # Renderiza cada componente
        components_html = "\n".join(
            ComponentRegistry.render_component(c)
            for c in sorted(self.page.components, key=lambda c: c.z_index)
        )

        # CSS
        cdn_css_links = "\n  ".join(
            f'<link rel="stylesheet" href="{url}">' for url in self._CDN_CSS
        )
        if inline_css:
            css_block = f"<style>\n{self._build_page_css(bg, w, h)}\n</style>"
        else:
            css_block = '<link rel="stylesheet" href="style.css">'

        # JS
        cdn_js_tags = "\n  ".join(
            f'<script src="{url}"></script>' for url in self._CDN_JS
        )
        if inline_js:
            js_code = self._build_page_js()
            js_block = f"<script>\n{js_code}\n</script>"
        else:
            js_block = '<script src="app.js"></script>'

        return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  {cdn_css_links}
  {css_block}
</head>
<body>
  <!-- Canvas: {w}x{h} gerado pelo DevStation Builder -->
  <div id="dsb-canvas" class="dsb-canvas" style="background:{bg};">
    {components_html}
  </div>

  {cdn_js_tags}
  <!-- Runtime DSB (eventos, regras, timer, countdown) -->
  <script>
{self._dsb_runtime()}
  </script>
  {js_block}
</body>
</html>"""

    # ── CSS da página ─────────────────────────────────────────

    def _build_page_css(self, bg: str, w: int, h: int) -> str:
        """CSS base + CSS customizado de cada componente."""
        custom = "\n".join(
            ComponentRegistry.render_css(c) for c in self.page.components
        )
        return f"""
/* DevStation Builder — Gerado automaticamente */
*, *::before, *::after {{ box-sizing: border-box; }}
body {{
  margin: 0;
  padding: 16px;
  background: #f0f4ff;
  font-family: 'Segoe UI', system-ui, sans-serif;
}}
.dsb-canvas {{
  position: relative;
  width: {w}px;
  min-height: {h}px;
  background: {bg};
  margin: 0 auto;
  box-shadow: 0 2px 20px rgba(0,0,0,.1);
  overflow: hidden;
}}
@media (max-width: {w}px) {{
  .dsb-canvas {{
    width: 100%;
    min-height: auto;
  }}
  [style*="position:absolute"] {{
    position: relative !important;
    left: auto !important;
    top: auto !important;
    width: 100% !important;
    margin-bottom: 8px;
  }}
}}
/* Toast notification */
#dsb-toast-container {{
  position: fixed; top: 20px; right: 20px; z-index: 9999;
  display: flex; flex-direction: column; gap: 8px;
}}
.dsb-toast {{
  padding: 12px 20px; border-radius: 6px; color: #fff;
  font-size: 14px; min-width: 220px;
  animation: dsb-slide-in .3s ease;
}}
@keyframes dsb-slide-in {{
  from {{ transform: translateX(120%); opacity: 0; }}
  to   {{ transform: translateX(0);    opacity: 1; }}
}}
.dsb-toast.info    {{ background: #0d6efd; }}
.dsb-toast.success {{ background: #198754; }}
.dsb-toast.warning {{ background: #fd7e14; }}
.dsb-toast.error   {{ background: #dc3545; }}
{custom}"""

    # ── JS da página ──────────────────────────────────────────

    def _build_page_js(self) -> str:
        """JS de eventos e regras de cada componente."""
        lines = ["// Eventos e Regras — DevStation Builder", "document.addEventListener('DOMContentLoaded', () => {"]
        for c in self.page.components:
            js = ComponentRegistry.render_js(c)
            if js.strip():
                lines.append(js)
        lines.append("  DSB.initAll();")
        lines.append("});")
        return "\n".join(lines)

    # ── Runtime DSB embutido ──────────────────────────────────

    @staticmethod
    def _dsb_runtime() -> str:
        """
        Mini-runtime JavaScript injetado em toda página exportada.
        Fornece: DSB.toast, DSB.setValue, DSB.rules.*, timers, countdown.
        """
        return r"""
const DSB = {
  /* ── Toast ──────────────────────────────────────────── */
  toast(msg, type = 'info', duration = 3000) {
    let c = document.getElementById('dsb-toast-container');
    if (!c) { c = document.createElement('div'); c.id = 'dsb-toast-container'; document.body.appendChild(c); }
    const t = document.createElement('div');
    t.className = `dsb-toast ${type}`;
    t.textContent = msg;
    c.appendChild(t);
    setTimeout(() => t.remove(), duration);
  },

  /* ── Valor de campos ─────────────────────────────────── */
  val(id) {
    const el = document.getElementById(id);
    if (!el) return '';
    if (el.type === 'checkbox' || el.type === 'radio') return el.checked;
    return el.value || el.textContent || '';
  },
  setValue(id, v) {
    const el = document.getElementById(id);
    if (!el) return;
    if ('value' in el) el.value = v;
    else el.textContent = v;
  },
  setText(id, text) {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
  },
  setVisible(id, v) {
    const el = document.getElementById(id);
    if (el) el.style.display = v ? '' : 'none';
  },
  toggleVisible(id) {
    const el = document.getElementById(id);
    if (el) el.style.display = el.style.display === 'none' ? '' : 'none';
  },
  setEnabled(id, v) {
    const el = document.getElementById(id);
    if (el) el.disabled = !v;
  },
  setProgress(id, val) {
    const wrap = document.getElementById(id);
    if (!wrap) return;
    const bar = wrap.querySelector('.progress-bar');
    if (bar) { bar.style.width = val + '%'; bar.textContent = val + '%'; }
  },

  /* ── Timers ──────────────────────────────────────────── */
  _timers: {},
  startTimer(id, ms) {
    DSB.stopTimer(id);
    const el = document.getElementById(id);
    DSB._timers[id] = setInterval(() => {
      el?.dispatchEvent(new CustomEvent('tick', { detail: { id } }));
    }, ms || 1000);
  },
  stopTimer(id) {
    clearInterval(DSB._timers[id]);
    delete DSB._timers[id];
  },

  /* ── Countdown ────────────────────────────────────────── */
  _countdowns: {},
  startCountdown(id) {
    const el = document.getElementById(id);
    if (!el) return;
    let secs = parseInt(el.dataset.seconds || 60);
    const disp = el.querySelector('.countdown-display');
    DSB._countdowns[id] = setInterval(() => {
      secs--;
      const mm = String(Math.floor(secs / 60)).padStart(2, '0');
      const ss = String(secs % 60).padStart(2, '0');
      if (disp) disp.textContent = `${mm}:${ss}`;
      el.dispatchEvent(new CustomEvent('tick', { detail: { secs } }));
      if (secs <= 0) {
        clearInterval(DSB._countdowns[id]);
        el.dispatchEvent(new CustomEvent('complete'));
      }
    }, 1000);
  },

  /* ── Regras ──────────────────────────────────────────── */
  rules: {
    _err(el, msg) {
      el.classList.add('is-invalid');
      let fb = el.parentElement?.querySelector('.invalid-feedback');
      if (!fb) { fb = document.createElement('div'); fb.className = 'invalid-feedback'; el.after(fb); }
      fb.textContent = msg;
    },
    _ok(el) { el.classList.remove('is-invalid'); },
    required(el, msg) { if (!el.value.trim()) { DSB.rules._err(el,msg); return false; } DSB.rules._ok(el); return true; },
    minLength(el, min, msg) { if (el.value.length < min) { DSB.rules._err(el, msg.replace('{min}',min)); return false; } DSB.rules._ok(el); return true; },
    maxLength(el, max, msg) { if (el.value.length > max) { DSB.rules._err(el, msg.replace('{max}',max)); return false; } DSB.rules._ok(el); return true; },
    email(el, msg) { if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(el.value)) { DSB.rules._err(el,msg); return false; } DSB.rules._ok(el); return true; },
    onlyNumbers(el, msg) { if (!/^\d+$/.test(el.value)) { DSB.rules._err(el,msg); return false; } DSB.rules._ok(el); return true; },
    minValue(el, min, msg) { if (parseFloat(el.value) < min) { DSB.rules._err(el, msg.replace('{min}',min)); return false; } DSB.rules._ok(el); return true; },
    maxValue(el, max, msg) { if (parseFloat(el.value) > max) { DSB.rules._err(el, msg.replace('{max}',max)); return false; } DSB.rules._ok(el); return true; },
    validDate(el, msg) { if (!el.value || isNaN(Date.parse(el.value))) { DSB.rules._err(el,msg); return false; } DSB.rules._ok(el); return true; },
    cpf(el, msg) {
      const v = el.value.replace(/\D/g,'');
      let valid = v.length===11 && !/^(\d)\1{10}$/.test(v);
      if (valid) {
        let s=0; for(let i=0;i<9;i++) s+=parseInt(v[i])*(10-i);
        let r=s%11<2?0:11-s%11; valid=r===parseInt(v[9]);
        if(valid){s=0;for(let i=0;i<10;i++)s+=parseInt(v[i])*(11-i);r=s%11<2?0:11-s%11;valid=r===parseInt(v[10]);}
      }
      if(!valid){DSB.rules._err(el,msg);return false;}DSB.rules._ok(el);return true;
    },
    cnpj(el, msg) {
      const v = el.value.replace(/\D/g,'');
      if(v.length!==14||/^(\d)\1{13}$/.test(v)){DSB.rules._err(el,msg);return false;}
      DSB.rules._ok(el); return true; // simplified
    },
    visibleIf(el, srcId, op, val) {
      const src = document.getElementById(srcId); if(!src) return;
      const sv = DSB.val(srcId); const cond = DSB._compare(sv,op,val);
      el.style.display = cond ? '' : 'none';
    },
    hiddenIf(el, srcId, op, val) {
      const src = document.getElementById(srcId); if(!src) return;
      el.style.display = DSB._compare(DSB.val(srcId),op,val) ? 'none' : '';
    },
    enabledIf(el, srcId, op, val) {
      const sv = DSB.val(srcId);
      const cond = op==='filled' ? sv!=='' : op==='empty' ? sv==='' : DSB._compare(sv,op,val);
      el.disabled = !cond;
    },
    calculate(targetId, fn) { try { DSB.setValue(targetId, fn()); } catch(e){} },
    sum(ids, targetId) {
      const total = ids.reduce((acc, id) => acc + (parseFloat(DSB.val(id))||0), 0);
      DSB.setValue(targetId, total.toFixed(2));
    },
    linkProgress(srcId, min, max, targetId) {
      const v = parseFloat(DSB.val(srcId)) || 0;
      const pct = Math.min(100, Math.max(0, (v - min) / (max - min) * 100));
      DSB.setProgress(targetId, Math.round(pct));
    },
    statusMap(srcId, mapping, targetId) {
      const v = DSB.val(srcId);
      const map = typeof mapping === 'string' ? JSON.parse(mapping) : mapping;
      DSB.setText(targetId, map[v] || v);
    },
    format(srcId, fmt, targetId) {
      DSB.setText(targetId, fmt.replace('{v}', DSB.val(srcId)));
    },
  },

  /* ── Utilitários ─────────────────────────────────────── */
  _compare(a, op, b) {
    switch(op) {
      case '==': return String(a) === String(b);
      case '!=': return String(a) !== String(b);
      case '>':  return parseFloat(a) > parseFloat(b);
      case '<':  return parseFloat(a) < parseFloat(b);
      case '>=': return parseFloat(a) >= parseFloat(b);
      case '<=': return parseFloat(a) <= parseFloat(b);
      case 'contains': return String(a).includes(String(b));
      default: return false;
    }
  },
  validateAll() {
    let ok = true;
    document.querySelectorAll('[data-rules]').forEach(el => {
      try { const rules = JSON.parse(el.dataset.rules); /* execute each */ } catch(e){}
    });
    return ok;
  },
  clearValidations() {
    document.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
  },
  callApi(url, method, targetId) {
    fetch(url, {method}).then(r=>r.json()).then(d=>{
      if(targetId) DSB.setValue(targetId, JSON.stringify(d));
    }).catch(e=>DSB.toast('Erro na API: '+e.message,'error'));
  },
  exportCsv(gridId) {
    const tbl = document.querySelector(`#${gridId} table`); if(!tbl) return;
    const rows = [...tbl.querySelectorAll('tr')].map(r=>
      [...r.querySelectorAll('th,td')].map(c=>'"'+c.textContent.replace(/"/g,'""')+'"').join(',')
    ).join('\n');
    const a = document.createElement('a'); a.href='data:text/csv;charset=utf-8,'+encodeURIComponent(rows);
    a.download='export.csv'; a.click();
  },
  initAll() {
    /* Auto-start timers/countdowns */
    document.querySelectorAll('[data-dsb][data-enabled="true"]').forEach(el => {
      const ms = parseInt(el.dataset.interval);
      if (ms) DSB.startTimer(el.id, ms);
    });
    document.querySelectorAll('[data-dsb][data-auto="true"]').forEach(el => {
      DSB.startCountdown(el.id);
    });
  },
};"""
