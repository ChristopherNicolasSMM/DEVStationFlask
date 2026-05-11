"""
components/definitions.py — Todos os Componentes do Sistema
=============================================================
Cada classe implementa BaseComponent para um tipo específico.

Grupos:
  Entrada    → Button, TextBox, TextArea, NumberBox, CheckBox,
                RadioButton, ComboBox, DatePicker, Switch, Slider, Rating, FileUpload
  Visualização → Label, Heading, Image, Icon, Badge,
                  ProgressBar, StatusBar, Separator, Spinner
  Container  → Panel, Card, GroupBox, Tabs, Accordion, Grid
  Dados      → DataGrid, Chart, Pagination, TreeView
  Feedback   → Alert, Toast (modal), MessageBox
  Navegação  → Navbar, Breadcrumb, Stepper, Sidebar
  Tempo      → Timer, Countdown
"""

from typing import Any, Dict, List

from .base_component import BaseComponent

# ═══════════════════════════════════════════════════════════════
#  ENTRADA
# ═══════════════════════════════════════════════════════════════


class ButtonComponent(BaseComponent):
    type = "button"
    label = "Botão"
    icon = "bi-app"
    group = "Entrada"

    @property
    def default_properties(self):
        return {
            "text": "Botão",
            "variant": "primary",  # primary|secondary|success|danger|warning|info|light|dark|outline-primary
            "size": "md",  # sm|md|lg
            "icon": "",  # bi-save, bi-trash …
            "icon_pos": "left",  # left|right
            "disabled": False,
            "full_width": False,
            "border_radius": 4,
            "bg_color": "#4154f1",
            "text_color": "#ffffff",
            "font_size": 14,
        }

    @property
    def default_size(self):
        return {"width": 150, "height": 40}

    @property
    def available_events(self):
        return [
            "onClick",
            "onDoubleClick",
            "onMouseEnter",
            "onMouseLeave",
            "onFocus",
            "onBlur",
        ]

    def render_html(self, comp_id, name, props, x, y, width, height, z_index):
        v = props.get("variant", "primary")
        sz = {"sm": "btn-sm", "lg": "btn-lg", "md": ""}.get(props.get("size", "md"), "")
        dis = "disabled" if props.get("disabled") else ""
        fw = "w-100" if props.get("full_width") else ""
        icon_cls = (
            f'<i class="bi {props["icon"]} me-1"></i>' if props.get("icon") else ""
        )
        style = (
            f"background-color:{props.get('bg_color','')};color:{props.get('text_color','#fff')};"
            f"border-radius:{props.get('border_radius',4)}px;"
            f"font-size:{props.get('font_size',14)}px;"
        )
        pos = self.position_style(x, y, width, height, z_index)
        return (
            f'<div style="{pos}">'
            f'<button id="{comp_id}" class="btn btn-{v} {sz} {fw}" '
            f'style="{style}" {dis} data-dsb="{name}">'
            f'{icon_cls}{props.get("text","Botão")}</button></div>'
        )


class TextBoxComponent(BaseComponent):
    type = "textbox"
    label = "Campo Texto"
    icon = "bi-input-cursor-text"
    group = "Entrada"

    @property
    def default_properties(self):
        return {
            "placeholder": "Digite aqui...",
            "value": "",
            "maxlength": "",
            "readonly": False,
            "disabled": False,
            "input_type": "text",  # text|email|password|tel|url
            "label": "",  # label acima do campo
            "helper_text": "",
            "border_color": "#ced4da",
            "border_radius": 4,
            "font_size": 14,
        }

    @property
    def default_size(self):
        return {"width": 220, "height": 38}

    @property
    def available_events(self):
        return ["onChange", "onKeyUp", "onKeyDown", "onFocus", "onBlur", "onInput"]

    @property
    def available_rules(self):
        return [
            "obrigatorio",
            "min_length",
            "max_length",
            "email",
            "cpf",
            "cnpj",
            "visivel_se",
            "habilitado_se",
        ]

    def render_html(self, comp_id, name, props, x, y, width, height, z_index):
        lbl = (
            f'<label class="form-label mb-1" style="font-size:12px;">{props["label"]}</label>'
            if props.get("label")
            else ""
        )
        pos = self.position_style(x, y, width, height, z_index)
        itype = props.get("input_type", "text")
        style = (
            f"border-color:{props.get('border_color','#ced4da')};"
            f"border-radius:{props.get('border_radius',4)}px;"
            f"font-size:{props.get('font_size',14)}px;"
        )
        ro = "readonly" if props.get("readonly") else ""
        dis = "disabled" if props.get("disabled") else ""
        mxl = f'maxlength="{props["maxlength"]}"' if props.get("maxlength") else ""
        return (
            f'<div style="{pos}">{lbl}'
            f'<input id="{comp_id}" type="{itype}" class="form-control" '
            f'placeholder="{props.get("placeholder","")}" value="{props.get("value","")}" '
            f'style="{style}" {ro} {dis} {mxl} data-dsb="{name}"></div>'
        )


class TextAreaComponent(BaseComponent):
    type = "textarea"
    label = "Área de Texto"
    icon = "bi-textarea"
    group = "Entrada"

    @property
    def default_properties(self):
        return {
            "placeholder": "Texto...",
            "value": "",
            "rows": 4,
            "maxlength": "",
            "readonly": False,
            "label": "",
            "resize": "vertical",  # none|vertical|horizontal|both
            "font_size": 14,
        }

    @property
    def default_size(self):
        return {"width": 260, "height": 100}

    @property
    def available_events(self):
        return ["onChange", "onKeyUp", "onFocus", "onBlur"]

    @property
    def available_rules(self):
        return [
            "obrigatorio",
            "min_length",
            "max_length",
            "visivel_se",
            "habilitado_se",
        ]

    def render_html(self, comp_id, name, props, x, y, width, height, z_index):
        pos = self.position_style(x, y, width, height, z_index)
        return (
            f'<div style="{pos}">'
            f'<textarea id="{comp_id}" class="form-control" '
            f'rows="{props.get("rows",4)}" '
            f'placeholder="{props.get("placeholder","")}" '
            f'style="resize:{props.get("resize","vertical")};font-size:{props.get("font_size",14)}px;" '
            f'data-dsb="{name}">{props.get("value","")}</textarea></div>'
        )


class NumberBoxComponent(BaseComponent):
    type = "numberbox"
    label = "Campo Número"
    icon = "bi-123"
    group = "Entrada"

    @property
    def default_properties(self):
        return {
            "value": "",
            "min": "",
            "max": "",
            "step": 1,
            "placeholder": "0",
            "label": "",
            "font_size": 14,
        }

    @property
    def default_size(self):
        return {"width": 160, "height": 38}

    @property
    def available_events(self):
        return ["onChange", "onFocus", "onBlur"]

    @property
    def available_rules(self):
        return ["obrigatorio", "min_valor", "max_valor", "visivel_se", "habilitado_se"]

    def render_html(self, comp_id, name, props, x, y, width, height, z_index):
        pos = self.position_style(x, y, width, height, z_index)
        mn = f'min="{props["min"]}"' if props.get("min", "") != "" else ""
        mx = f'max="{props["max"]}"' if props.get("max", "") != "" else ""
        return (
            f'<div style="{pos}">'
            f'<input id="{comp_id}" type="number" class="form-control" '
            f'value="{props.get("value","")}" step="{props.get("step",1)}" '
            f'{mn} {mx} placeholder="{props.get("placeholder","0")}" '
            f'style="font-size:{props.get("font_size",14)}px;" data-dsb="{name}"></div>'
        )


class CheckBoxComponent(BaseComponent):
    type = "checkbox"
    label = "CheckBox"
    icon = "bi-check-square"
    group = "Entrada"

    @property
    def default_properties(self):
        return {"text": "Opção", "checked": False, "disabled": False, "font_size": 14}

    @property
    def default_size(self):
        return {"width": 160, "height": 30}

    @property
    def available_events(self):
        return ["onChange", "onClick"]

    def render_html(self, comp_id, name, props, x, y, width, height, z_index):
        pos = self.position_style(
            x, y, width, height, z_index, "display:flex;align-items:center;"
        )
        chk = "checked" if props.get("checked") else ""
        dis = "disabled" if props.get("disabled") else ""
        return (
            f'<div style="{pos}" class="form-check">'
            f'<input id="{comp_id}" type="checkbox" class="form-check-input" '
            f'{chk} {dis} data-dsb="{name}">'
            f'<label class="form-check-label ms-2" for="{comp_id}" '
            f'style="font-size:{props.get("font_size",14)}px;">'
            f'{props.get("text","Opção")}</label></div>'
        )


class RadioButtonComponent(BaseComponent):
    type = "radiobutton"
    label = "RadioButton"
    icon = "bi-record-circle"
    group = "Entrada"

    @property
    def default_properties(self):
        return {
            "text": "Opção",
            "checked": False,
            "group_name": "grupo1",
            "disabled": False,
            "font_size": 14,
        }

    @property
    def default_size(self):
        return {"width": 160, "height": 30}

    @property
    def available_events(self):
        return ["onChange", "onClick"]

    def render_html(self, comp_id, name, props, x, y, width, height, z_index):
        pos = self.position_style(
            x, y, width, height, z_index, "display:flex;align-items:center;"
        )
        chk = "checked" if props.get("checked") else ""
        return (
            f'<div style="{pos}" class="form-check">'
            f'<input id="{comp_id}" type="radio" name="{props.get("group_name","grupo1")}" '
            f'class="form-check-input" {chk} data-dsb="{name}">'
            f'<label class="form-check-label ms-2" for="{comp_id}" '
            f'style="font-size:{props.get("font_size",14)}px;">'
            f'{props.get("text","Opção")}</label></div>'
        )


class ComboBoxComponent(BaseComponent):
    type = "combobox"
    label = "ComboBox"
    icon = "bi-menu-button-wide"
    group = "Entrada"

    @property
    def default_properties(self):
        return {
            "label": "",
            "placeholder": "Selecione...",
            "items": ["Opção 1", "Opção 2", "Opção 3"],
            "selected_value": "",
            "disabled": False,
            "font_size": 14,
        }

    @property
    def default_size(self):
        return {"width": 220, "height": 38}

    @property
    def available_events(self):
        return ["onChange", "onFocus", "onBlur"]

    @property
    def available_rules(self):
        return ["obrigatorio", "visivel_se", "habilitado_se"]

    def render_html(self, comp_id, name, props, x, y, width, height, z_index):
        pos = self.position_style(x, y, width, height, z_index)
        opts = "".join(
            f'<option value="{o}" {"selected" if o==props.get("selected_value") else ""}>{o}</option>'
            for o in (props.get("items") or [])
        )
        dis = "disabled" if props.get("disabled") else ""
        return (
            f'<div style="{pos}">'
            f'<select id="{comp_id}" class="form-select" {dis} data-dsb="{name}" '
            f'style="font-size:{props.get("font_size",14)}px;">'
            f'<option value="">{props.get("placeholder","Selecione...")}</option>'
            f"{opts}</select></div>"
        )


class SwitchComponent(BaseComponent):
    type = "switch"
    label = "Switch/Toggle"
    icon = "bi-toggle-on"
    group = "Entrada"

    @property
    def default_properties(self):
        return {
            "text": "Ativado",
            "checked": False,
            "font_size": 14,
            "color": "#4154f1",
        }

    @property
    def default_size(self):
        return {"width": 160, "height": 30}

    @property
    def available_events(self):
        return ["onChange", "onClick"]

    def render_html(self, comp_id, name, props, x, y, width, height, z_index):
        pos = self.position_style(
            x, y, width, height, z_index, "display:flex;align-items:center;"
        )
        chk = "checked" if props.get("checked") else ""
        return (
            f'<div style="{pos}" class="form-check form-switch">'
            f'<input id="{comp_id}" type="checkbox" class="form-check-input" role="switch" '
            f'{chk} data-dsb="{name}">'
            f'<label class="form-check-label ms-2" for="{comp_id}" '
            f'style="font-size:{props.get("font_size",14)}px;">'
            f'{props.get("text","")}</label></div>'
        )


class SliderComponent(BaseComponent):
    type = "slider"
    label = "Slider"
    icon = "bi-sliders"
    group = "Entrada"

    @property
    def default_properties(self):
        return {
            "value": 50,
            "min": 0,
            "max": 100,
            "step": 1,
            "label": "",
            "show_value": True,
        }

    @property
    def default_size(self):
        return {"width": 240, "height": 40}

    @property
    def available_events(self):
        return ["onChange", "onInput"]

    def render_html(self, comp_id, name, props, x, y, width, height, z_index):
        pos = self.position_style(x, y, width, height, z_index)
        sv = (
            f'<output id="{comp_id}_out">{props.get("value",50)}</output>'
            if props.get("show_value")
            else ""
        )
        return (
            f'<div style="{pos}">'
            f'<input id="{comp_id}" type="range" class="form-range" '
            f'min="{props.get("min",0)}" max="{props.get("max",100)}" '
            f'step="{props.get("step",1)}" value="{props.get("value",50)}" '
            f"oninput=\"document.getElementById('{comp_id}_out').value=this.value\" "
            f'data-dsb="{name}"> {sv}</div>'
        )


class DatePickerComponent(BaseComponent):
    type = "datepicker"
    label = "Data"
    icon = "bi-calendar3"
    group = "Entrada"

    @property
    def default_properties(self):
        return {"value": "", "min": "", "max": "", "label": "", "disabled": False}

    @property
    def default_size(self):
        return {"width": 200, "height": 38}

    @property
    def available_events(self):
        return ["onChange"]

    @property
    def available_rules(self):
        return ["obrigatorio", "data_valida", "visivel_se", "habilitado_se"]

    def render_html(self, comp_id, name, props, x, y, width, height, z_index):
        pos = self.position_style(x, y, width, height, z_index)
        mn = f'min="{props["min"]}"' if props.get("min") else ""
        mx = f'max="{props["max"]}"' if props.get("max") else ""
        return (
            f'<div style="{pos}">'
            f'<input id="{comp_id}" type="date" class="form-control" '
            f'value="{props.get("value","")}" {mn} {mx} data-dsb="{name}"></div>'
        )


class RatingComponent(BaseComponent):
    type = "rating"
    label = "Rating"
    icon = "bi-star-half"
    group = "Entrada"

    @property
    def default_properties(self):
        return {"value": 3, "max": 5, "color": "#ffc107", "size": 24}

    @property
    def default_size(self):
        return {"width": 150, "height": 36}

    @property
    def available_events(self):
        return ["onChange"]

    def render_html(self, comp_id, name, props, x, y, width, height, z_index):
        pos = self.position_style(x, y, width, height, z_index, "display:flex;gap:4px;")
        val = int(props.get("value", 3))
        mx = int(props.get("max", 5))
        color = props.get("color", "#ffc107")
        sz = props.get("size", 24)
        stars = "".join(
            f'<i class="bi bi-star{"" if i > val else "-fill"}" '
            f'style="font-size:{sz}px;color:{color};cursor:pointer;" '
            f'data-star="{i}"></i>'
            for i in range(1, mx + 1)
        )
        return f'<div id="{comp_id}" style="{pos}" data-dsb="{name}">{stars}</div>'


class FileUploadComponent(BaseComponent):
    type = "fileupload"
    label = "Upload Arquivo"
    icon = "bi-upload"
    group = "Entrada"

    @property
    def default_properties(self):
        return {
            "accept": "*/*",
            "multiple": False,
            "label": "Escolher arquivo",
            "max_size_mb": 10,
        }

    @property
    def default_size(self):
        return {"width": 220, "height": 38}

    @property
    def available_events(self):
        return ["onChange"]

    def render_html(self, comp_id, name, props, x, y, width, height, z_index):
        pos = self.position_style(x, y, width, height, z_index)
        mult = "multiple" if props.get("multiple") else ""
        return (
            f'<div style="{pos}">'
            f'<input id="{comp_id}" type="file" class="form-control" '
            f'accept="{props.get("accept","*/*")}" {mult} data-dsb="{name}"></div>'
        )


# ═══════════════════════════════════════════════════════════════
#  VISUALIZAÇÃO
# ═══════════════════════════════════════════════════════════════


class LabelComponent(BaseComponent):
    type = "label"
    label = "Texto / Label"
    icon = "bi-paragraph"
    group = "Visualização"

    @property
    def default_properties(self):
        return {
            "text": "Texto parágrafo",
            "tag": "p",  # p|span|div|small|strong
            "font_size": 14,
            "text_color": "#333333",
            "bg_color": "",
            "bold": False,
            "italic": False,
            "text_align": "left",
            "line_height": 1.5,
        }

    @property
    def default_size(self):
        return {"width": 220, "height": 36}

    @property
    def available_events(self):
        return ["onClick"]

    def render_html(self, comp_id, name, props, x, y, width, height, z_index):
        pos = self.position_style(x, y, width, height, z_index)
        tag = props.get("tag", "p")
        style = (
            f"font-size:{props.get('font_size',14)}px;"
            f"color:{props.get('text_color','#333')};"
            f"font-weight:{'bold' if props.get('bold') else 'normal'};"
            f"font-style:{'italic' if props.get('italic') else 'normal'};"
            f"text-align:{props.get('text_align','left')};"
            f"line-height:{props.get('line_height',1.5)};"
            f"margin:0;padding:0;"
        )
        if props.get("bg_color"):
            style += f"background-color:{props['bg_color']};"
        return (
            f'<div style="{pos}">'
            f'<{tag} id="{comp_id}" style="{style}" data-dsb="{name}">'
            f'{props.get("text","")}</{tag}></div>'
        )


class HeadingComponent(BaseComponent):
    type = "heading"
    label = "Título"
    icon = "bi-type-h1"
    group = "Visualização"

    @property
    def default_properties(self):
        return {
            "text": "Título da Seção",
            "tag": "h2",  # h1..h6
            "font_size": 26,
            "text_color": "#012970",
            "bold": True,
            "text_align": "left",
        }

    @property
    def default_size(self):
        return {"width": 320, "height": 48}

    def render_html(self, comp_id, name, props, x, y, width, height, z_index):
        pos = self.position_style(x, y, width, height, z_index)
        tag = props.get("tag", "h2")
        style = (
            f"font-size:{props.get('font_size',26)}px;"
            f"color:{props.get('text_color','#012970')};"
            f"font-weight:{'bold' if props.get('bold',True) else 'normal'};"
            f"text-align:{props.get('text_align','left')};margin:0;"
        )
        return (
            f'<div style="{pos}">'
            f'<{tag} id="{comp_id}" style="{style}" data-dsb="{name}">'
            f'{props.get("text","Título")}</{tag}></div>'
        )


class ImageComponent(BaseComponent):
    type = "image"
    label = "Imagem"
    icon = "bi-image"
    group = "Visualização"

    @property
    def default_properties(self):
        return {
            "src": "https://placehold.co/300x200/e8edff/4154f1?text=Imagem",
            "alt": "Imagem",
            "object_fit": "cover",  # cover|contain|fill|none
            "border_radius": 4,
        }

    @property
    def default_size(self):
        return {"width": 300, "height": 200}

    @property
    def available_events(self):
        return ["onClick"]

    def render_html(self, comp_id, name, props, x, y, width, height, z_index):
        pos = self.position_style(x, y, width, height, z_index, "overflow:hidden;")
        style = (
            f"width:100%;height:100%;"
            f"object-fit:{props.get('object_fit','cover')};"
            f"border-radius:{props.get('border_radius',4)}px;display:block;"
        )
        return (
            f'<div id="{comp_id}" style="{pos}" data-dsb="{name}">'
            f'<img src="{props.get("src","")}" alt="{props.get("alt","")}" style="{style}"></div>'
        )


class IconComponent(BaseComponent):
    type = "icon"
    label = "Ícone"
    icon = "bi-star"
    group = "Visualização"

    @property
    def default_properties(self):
        return {"icon_class": "bi-star-fill", "size": 32, "color": "#4154f1"}

    @property
    def default_size(self):
        return {"width": 50, "height": 50}

    @property
    def available_events(self):
        return ["onClick"]

    def render_html(self, comp_id, name, props, x, y, width, height, z_index):
        pos = self.position_style(
            x,
            y,
            width,
            height,
            z_index,
            "display:flex;align-items:center;justify-content:center;",
        )
        return (
            f'<div id="{comp_id}" style="{pos}" data-dsb="{name}">'
            f'<i class="bi {props.get("icon_class","bi-star-fill")}" '
            f'style="font-size:{props.get("size",32)}px;color:{props.get("color","#4154f1")};"></i></div>'
        )


class BadgeComponent(BaseComponent):
    type = "badge"
    label = "Badge"
    icon = "bi-tag"
    group = "Visualização"

    @property
    def default_properties(self):
        return {"text": "Novo", "variant": "primary", "pill": False, "font_size": 12}

    @property
    def default_size(self):
        return {"width": 70, "height": 28}

    def render_html(self, comp_id, name, props, x, y, width, height, z_index):
        pos = self.position_style(x, y, width, height, z_index)
        pill = "rounded-pill" if props.get("pill") else ""
        return (
            f'<div style="{pos}">'
            f'<span id="{comp_id}" class="badge bg-{props.get("variant","primary")} {pill}" '
            f'style="font-size:{props.get("font_size",12)}px;" data-dsb="{name}">'
            f'{props.get("text","Novo")}</span></div>'
        )


class ProgressBarComponent(BaseComponent):
    type = "progressbar"
    label = "Progress Bar"
    icon = "bi-bar-chart-steps"
    group = "Visualização"

    @property
    def default_properties(self):
        return {
            "value": 60,
            "min": 0,
            "max": 100,
            "variant": "primary",
            "striped": False,
            "animated": False,
            "show_text": True,
            "height": 20,
        }

    @property
    def default_size(self):
        return {"width": 280, "height": 28}

    @property
    def available_events(self):
        return ["onComplete", "onProgress"]

    def render_html(self, comp_id, name, props, x, y, width, height, z_index):
        pos = self.position_style(x, y, width, height, z_index)
        val = int(props.get("value", 60))
        mx = int(props.get("max", 100))
        pct = round(val / mx * 100) if mx else 0
        ext = (
            (
                "progress-bar-striped "
                + ("progress-bar-animated" if props.get("animated") else "")
            )
            if props.get("striped")
            else ""
        )
        txt = f"{pct}%" if props.get("show_text") else ""
        h = props.get("height", 20)
        return (
            f'<div style="{pos}">'
            f'<div id="{comp_id}" class="progress" style="height:{h}px;" data-dsb="{name}">'
            f'<div class="progress-bar bg-{props.get("variant","primary")} {ext}" '
            f'role="progressbar" style="width:{pct}%" '
            f'aria-valuenow="{val}" aria-valuemin="{props.get("min",0)}" aria-valuemax="{mx}">'
            f"{txt}</div></div></div>"
        )


class StatusBarComponent(BaseComponent):
    type = "statusbar"
    label = "Status Bar"
    icon = "bi-info-circle"
    group = "Visualização"

    @property
    def default_properties(self):
        return {
            "text": "Pronto",
            "icon": "bi-check-circle",
            "bg_color": "#d1e7dd",
            "text_color": "#0a3622",
            "font_size": 13,
        }

    @property
    def default_size(self):
        return {"width": 300, "height": 32}

    def render_html(self, comp_id, name, props, x, y, width, height, z_index):
        pos = self.position_style(
            x,
            y,
            width,
            height,
            z_index,
            "display:flex;align-items:center;gap:6px;"
            f"padding:4px 12px;border-radius:4px;"
            f"background:{props.get('bg_color','#d1e7dd')};"
            f"color:{props.get('text_color','#0a3622')};",
        )
        return (
            f'<div id="{comp_id}" style="{pos}" data-dsb="{name}">'
            f'<i class="bi {props.get("icon","bi-check-circle")}"></i>'
            f'<span style="font-size:{props.get("font_size",13)}px;">'
            f'{props.get("text","Pronto")}</span></div>'
        )


class SeparatorComponent(BaseComponent):
    type = "separator"
    label = "Divisor"
    icon = "bi-hr"
    group = "Visualização"

    @property
    def default_properties(self):
        return {
            "color": "#dee2e6",
            "thickness": 2,
            "style": "solid",
        }  # solid|dashed|dotted

    @property
    def default_size(self):
        return {"width": 300, "height": 8}

    def render_html(self, comp_id, name, props, x, y, width, height, z_index):
        pos = self.position_style(
            x, y, width, height, z_index, "display:flex;align-items:center;"
        )
        style = (
            f"width:100%;border:none;border-top:{props.get('thickness',2)}px "
            f"{props.get('style','solid')} {props.get('color','#dee2e6')};margin:0;"
        )
        return f'<div style="{pos}"><hr id="{comp_id}" style="{style}" data-dsb="{name}"></div>'


class SpinnerComponent(BaseComponent):
    type = "spinner"
    label = "Spinner"
    icon = "bi-arrow-repeat"
    group = "Visualização"

    @property
    def default_properties(self):
        return {"variant": "primary", "size": "md", "type": "border"}  # border|grow

    @property
    def default_size(self):
        return {"width": 50, "height": 50}

    def render_html(self, comp_id, name, props, x, y, width, height, z_index):
        pos = self.position_style(
            x,
            y,
            width,
            height,
            z_index,
            "display:flex;align-items:center;justify-content:center;",
        )
        sz = "spinner-border-sm" if props.get("size") == "sm" else ""
        t = props.get("type", "border")
        return (
            f'<div style="{pos}">'
            f'<div id="{comp_id}" class="spinner-{t} text-{props.get("variant","primary")} {sz}" '
            f'role="status" data-dsb="{name}"><span class="visually-hidden">...</span></div></div>'
        )


# ═══════════════════════════════════════════════════════════════
#  CONTAINER / LAYOUT
# ═══════════════════════════════════════════════════════════════


class PanelComponent(BaseComponent):
    type = "panel"
    label = "Painel"
    icon = "bi-bounding-box"
    group = "Container"

    @property
    def default_properties(self):
        return {
            "bg_color": "#f8f9fa",
            "border": "#dee2e6",
            "padding": "16px",
            "border_radius": 4,
            "shadow": False,
        }

    @property
    def default_size(self):
        return {"width": 320, "height": 180}

    @property
    def available_events(self):
        return ["onClick", "onMouseEnter"]

    def render_html(self, comp_id, name, props, x, y, width, height, z_index):
        pos = self.position_style(
            x,
            y,
            width,
            height,
            z_index,
            f"background:{props.get('bg_color','#f8f9fa')};"
            f"border:1px solid {props.get('border','#dee2e6')};"
            f"padding:{props.get('padding','16px')};"
            f"border-radius:{props.get('border_radius',4)}px;"
            + ("box-shadow:0 2px 10px rgba(0,0,0,.1);" if props.get("shadow") else ""),
        )
        return f'<div id="{comp_id}" style="{pos}" data-dsb="{name}"></div>'


class CardComponent(BaseComponent):
    type = "card"
    label = "Card"
    icon = "bi-card-text"
    group = "Container"

    @property
    def default_properties(self):
        return {
            "title": "Título do Card",
            "subtitle": "",
            "body": "Conteúdo...",
            "footer": "",
            "shadow": True,
            "border_radius": 8,
            "header_bg": "#4154f1",
            "header_color": "#fff",
        }

    @property
    def default_size(self):
        return {"width": 300, "height": 200}

    def render_html(self, comp_id, name, props, x, y, width, height, z_index):
        shadow = "shadow-sm" if props.get("shadow") else ""
        pos = self.position_style(
            x,
            y,
            width,
            height,
            z_index,
            f"border-radius:{props.get('border_radius',8)}px;overflow:hidden;",
        )
        hbg = props.get("header_bg", "#4154f1")
        hcol = props.get("header_color", "#fff")
        sub = (
            f'<h6 class="card-subtitle text-muted">{props["subtitle"]}</h6>'
            if props.get("subtitle")
            else ""
        )
        foot = (
            f'<div class="card-footer">{props["footer"]}</div>'
            if props.get("footer")
            else ""
        )
        return (
            f'<div id="{comp_id}" class="card {shadow}" style="{pos}" data-dsb="{name}">'
            f'<div class="card-header" style="background:{hbg};color:{hcol};">'
            f'<strong>{props.get("title","Card")}</strong></div>'
            f'<div class="card-body"><p class="card-text">{props.get("body","")}</p>{sub}</div>'
            f"{foot}</div>"
        )


class GroupBoxComponent(BaseComponent):
    type = "groupbox"
    label = "GroupBox"
    icon = "bi-collection"
    group = "Container"

    @property
    def default_properties(self):
        return {
            "title": "Grupo",
            "bg_color": "#fff",
            "border": "#ced4da",
            "collapsible": False,
            "font_size": 13,
        }

    @property
    def default_size(self):
        return {"width": 300, "height": 160}

    def render_html(self, comp_id, name, props, x, y, width, height, z_index):
        pos = self.position_style(x, y, width, height, z_index)
        return (
            f'<fieldset id="{comp_id}" style="{pos};border:1px solid {props.get("border","#ced4da")};"'
            f' data-dsb="{name}">'
            f'<legend style="font-size:{props.get("font_size",13)}px;padding:0 8px;width:auto;">'
            f'{props.get("title","Grupo")}</legend></fieldset>'
        )


class TabsComponent(BaseComponent):
    type = "tabs"
    label = "Abas (Tabs)"
    icon = "bi-folder-symlink"
    group = "Container"

    @property
    def default_properties(self):
        return {
            "tabs": ["Aba 1", "Aba 2", "Aba 3"],
            "active_tab": 0,
            "variant": "tabs",
        }  # tabs|pills

    @property
    def default_size(self):
        return {"width": 400, "height": 200}

    @property
    def available_events(self):
        return ["onTabChange"]

    def render_html(self, comp_id, name, props, x, y, width, height, z_index):
        pos = self.position_style(x, y, width, height, z_index)
        tabs = props.get("tabs", ["Aba 1", "Aba 2"])
        v = props.get("variant", "tabs")
        nav = "".join(
            f'<li class="nav-item"><a class="nav-link {"active" if i==0 else ""}" '
            f'href="#">{t}</a></li>'
            for i, t in enumerate(tabs)
        )
        return (
            f'<div id="{comp_id}" style="{pos}" data-dsb="{name}">'
            f'<ul class="nav nav-{v}">{nav}</ul>'
            f'<div class="tab-content border border-top-0 p-3" style="height:calc(100% - 42px);">'
            f"</div></div>"
        )


class AccordionComponent(BaseComponent):
    type = "accordion"
    label = "Accordion"
    icon = "bi-layout-accordion-collapsed"
    group = "Container"

    @property
    def default_properties(self):
        return {"sections": ["Seção 1", "Seção 2", "Seção 3"], "flush": False}

    @property
    def default_size(self):
        return {"width": 360, "height": 150}

    def render_html(self, comp_id, name, props, x, y, width, height, z_index):
        pos = self.position_style(x, y, width, height, z_index)
        fl = "accordion-flush" if props.get("flush") else ""
        items = "".join(
            f'<div class="accordion-item">'
            f'<h2 class="accordion-header">'
            f'<button class="accordion-button {"collapsed" if i>0 else ""}" type="button">'
            f"{s}</button></h2>"
            f'<div class="accordion-collapse collapse {"show" if i==0 else ""}">'
            f'<div class="accordion-body"></div></div></div>'
            for i, s in enumerate(props.get("sections", ["Seção 1"]))
        )
        return (
            f'<div id="{comp_id}" class="accordion {fl}" style="{pos}" data-dsb="{name}">'
            f"{items}</div>"
        )


# ═══════════════════════════════════════════════════════════════
#  DADOS
# ═══════════════════════════════════════════════════════════════


class DataGridComponent(BaseComponent):
    type = "datagrid"
    label = "DataGrid / Tabela"
    icon = "bi-table"
    group = "Dados"

    @property
    def default_properties(self):
        return {
            "columns": ["ID", "Nome", "Valor"],
            "rows": [["1", "Item A", "R$ 10,00"], ["2", "Item B", "R$ 20,00"]],
            "striped": True,
            "hover": True,
            "bordered": False,
            "small": False,
            "pagination": False,
            "sortable": True,
            "searchable": False,
        }

    @property
    def default_size(self):
        return {"width": 480, "height": 200}

    @property
    def available_events(self):
        return ["onRowClick", "onCellEdit", "onSort"]

    def render_html(self, comp_id, name, props, x, y, width, height, z_index):
        pos = self.position_style(x, y, width, height, z_index, "overflow:auto;")
        cls = (
            ("table-striped " if props.get("striped") else "")
            + ("table-hover " if props.get("hover") else "")
            + ("table-bordered " if props.get("bordered") else "")
            + ("table-sm " if props.get("small") else "")
        )
        hdrs = "".join(
            f'<th scope="col">{c}</th>' for c in (props.get("columns") or [])
        )
        rows = "".join(
            "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>"
            for row in (props.get("rows") or [])
        )
        return (
            f'<div id="{comp_id}" style="{pos}" data-dsb="{name}">'
            f'<table class="table {cls}"><thead class="table-dark"><tr>{hdrs}</tr></thead>'
            f"<tbody>{rows}</tbody></table></div>"
        )


class ChartComponent(BaseComponent):
    type = "chart"
    label = "Gráfico"
    icon = "bi-bar-chart"
    group = "Dados"

    @property
    def default_properties(self):
        return {
            "chart_type": "bar",  # bar|line|pie|doughnut
            "labels": ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun"],
            "data": [12, 19, 3, 5, 2, 3],
            "label": "Dados",
            "color": "#4154f1",
        }

    @property
    def default_size(self):
        return {"width": 400, "height": 260}

    @property
    def available_events(self):
        return ["onDataPointClick"]

    def render_html(self, comp_id, name, props, x, y, width, height, z_index):
        pos = self.position_style(x, y, width, height, z_index)
        # Gera script Chart.js inline
        t = props.get("chart_type", "bar")
        lbls = str(props.get("labels", []))
        data = str(props.get("data", []))
        color = props.get("color", "#4154f1")
        lbl = props.get("label", "Dados")
        return (
            f'<div style="{pos}">'
            f'<canvas id="{comp_id}" data-dsb="{name}"></canvas>'
            f'<script>new Chart(document.getElementById("{comp_id}"),{{'
            f'type:"{t}",data:{{labels:{lbls},'
            f'datasets:[{{label:"{lbl}",data:{data},'
            f'backgroundColor:"{color}"}}]}},'
            f"options:{{responsive:true,maintainAspectRatio:false}}}});</script></div>"
        )

    def render_js(self, comp_id, events, rules):
        # Chart.js inicializado inline no render_html
        return ""


class PaginationComponent(BaseComponent):
    type = "pagination"
    label = "Paginação"
    icon = "bi-arrow-left-right"
    group = "Dados"

    @property
    def default_properties(self):
        return {"total": 50, "per_page": 10, "current": 1, "size": "md"}  # sm|md|lg

    @property
    def default_size(self):
        return {"width": 280, "height": 40}

    @property
    def available_events(self):
        return ["onPageChange"]

    def render_html(self, comp_id, name, props, x, y, width, height, z_index):
        pos = self.position_style(x, y, width, height, z_index)
        total = int(props.get("total", 50))
        pp = int(props.get("per_page", 10))
        cur = int(props.get("current", 1))
        pages = max(1, -(-total // pp))  # ceil division
        sz = {"sm": "pagination-sm", "lg": "pagination-lg", "md": ""}.get(
            props.get("size", "md"), ""
        )
        items = (
            f'<li class="page-item{"disabled" if cur<=1 else ""}"><a class="page-link" href="#">«</a></li>'
            + "".join(
                f'<li class="page-item{"active" if i==cur else ""}"><a class="page-link" href="#">{i}</a></li>'
                for i in range(max(1, cur - 2), min(pages + 1, cur + 3))
            )
            + f'<li class="page-item{"disabled" if cur>=pages else ""}"><a class="page-link" href="#">»</a></li>'
        )
        return (
            f'<div style="{pos}">'
            f'<ul id="{comp_id}" class="pagination {sz} mb-0" data-dsb="{name}">{items}</ul></div>'
        )


# ═══════════════════════════════════════════════════════════════
#  FEEDBACK
# ═══════════════════════════════════════════════════════════════


class AlertComponent(BaseComponent):
    type = "alert"
    label = "Alert"
    icon = "bi-info-circle"
    group = "Feedback"

    @property
    def default_properties(self):
        return {
            "text": "Mensagem de alerta.",
            "variant": "info",
            "dismissible": False,
            "icon": "bi-info-circle-fill",
            "font_size": 14,
        }

    @property
    def default_size(self):
        return {"width": 340, "height": 56}

    def render_html(self, comp_id, name, props, x, y, width, height, z_index):
        pos = self.position_style(x, y, width, height, z_index)
        dis = "alert-dismissible fade show" if props.get("dismissible") else ""
        btn = (
            '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>'
            if props.get("dismissible")
            else ""
        )
        ic = (
            f'<i class="bi {props.get("icon","bi-info-circle-fill")} me-2"></i>'
            if props.get("icon")
            else ""
        )
        return (
            f'<div id="{comp_id}" class="alert alert-{props.get("variant","info")} {dis}" '
            f'style="{pos};font-size:{props.get("font_size",14)}px;" data-dsb="{name}">'
            f'{ic}{props.get("text","")}{btn}</div>'
        )


class ModalComponent(BaseComponent):
    type = "modal"
    label = "Dialog/Modal"
    icon = "bi-window-stack"
    group = "Feedback"

    @property
    def default_properties(self):
        return {
            "title": "Título do Dialog",
            "body": "Conteúdo do modal...",
            "size": "md",  # sm|md|lg|xl
            "close_on_backdrop": True,
            "trigger_label": "Abrir Dialog",
        }

    @property
    def default_size(self):
        return {"width": 200, "height": 40}

    @property
    def available_events(self):
        return ["onOpen", "onClose", "onConfirm", "onCancel"]

    def render_html(self, comp_id, name, props, x, y, width, height, z_index):
        pos = self.position_style(x, y, width, height, z_index)
        sz_c = {"sm": "modal-sm", "lg": "modal-lg", "xl": "modal-xl", "md": ""}.get(
            props.get("size", "md"), ""
        )
        backdrop = (
            "" if props.get("close_on_backdrop", True) else 'data-bs-backdrop="static"'
        )
        return (
            f'<div style="{pos}">'
            f'<button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#{comp_id}_m">'
            f'{props.get("trigger_label","Abrir")}</button></div>'
            f'<div class="modal fade" id="{comp_id}_m" {backdrop} tabindex="-1">'
            f'<div class="modal-dialog {sz_c}">'
            f'<div class="modal-content">'
            f'<div class="modal-header"><h5 class="modal-title">{props.get("title","Dialog")}</h5>'
            f'<button class="btn-close" data-bs-dismiss="modal"></button></div>'
            f'<div class="modal-body">{props.get("body","")}</div>'
            f'<div class="modal-footer">'
            f'<button class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>'
            f'<button class="btn btn-primary" data-bs-dismiss="modal" id="{comp_id}" data-dsb="{name}">OK</button>'
            f"</div></div></div></div>"
        )


# ═══════════════════════════════════════════════════════════════
#  NAVEGAÇÃO
# ═══════════════════════════════════════════════════════════════


class NavbarComponent(BaseComponent):
    type = "navbar"
    label = "Navbar"
    icon = "bi-layout-text-sidebar-reverse"
    group = "Navegação"

    @property
    def default_properties(self):
        return {
            "brand": "Meu Site",
            "links": ["Início", "Sobre", "Contato"],
            "variant": "dark",
            "bg": "primary",
            "expand": "lg",
        }

    @property
    def default_size(self):
        return {"width": 600, "height": 56}

    def render_html(self, comp_id, name, props, x, y, width, height, z_index):
        pos = self.position_style(x, y, width, height, z_index)
        links = "".join(
            f'<a class="nav-link" href="#">{l}</a>' for l in (props.get("links") or [])
        )
        return (
            f'<nav id="{comp_id}" class="navbar navbar-expand-{props.get("expand","lg")} '
            f'navbar-{props.get("variant","dark")} bg-{props.get("bg","primary")}" '
            f'style="{pos}" data-dsb="{name}">'
            f'<div class="container-fluid">'
            f'<a class="navbar-brand" href="#">{props.get("brand","Meu Site")}</a>'
            f'<div class="navbar-nav">{links}</div></div></nav>'
        )


class BreadcrumbComponent(BaseComponent):
    type = "breadcrumb"
    label = "Breadcrumb"
    icon = "bi-chevron-right"
    group = "Navegação"

    @property
    def default_properties(self):
        return {"items": ["Início", "Produtos", "Detalhe"]}

    @property
    def default_size(self):
        return {"width": 280, "height": 32}

    def render_html(self, comp_id, name, props, x, y, width, height, z_index):
        pos = self.position_style(x, y, width, height, z_index)
        items = props.get("items", ["Home"])
        crumbs = "".join(
            f'<li class="breadcrumb-item {"active" if i==len(items)-1 else ""}">'
            f'{"<a href=#>" if i<len(items)-1 else ""}{it}'
            f'{"</a>" if i<len(items)-1 else ""}</li>'
            for i, it in enumerate(items)
        )
        return (
            f'<nav id="{comp_id}" style="{pos}" data-dsb="{name}">'
            f'<ol class="breadcrumb mb-0">{crumbs}</ol></nav>'
        )


class StepperComponent(BaseComponent):
    type = "stepper"
    label = "Stepper"
    icon = "bi-list-ol"
    group = "Navegação"

    @property
    def default_properties(self):
        return {
            "steps": ["Dados", "Endereço", "Pagamento", "Confirmação"],
            "current": 1,
            "variant": "primary",
        }

    @property
    def default_size(self):
        return {"width": 480, "height": 60}

    @property
    def available_events(self):
        return ["onStepChange"]

    def render_html(self, comp_id, name, props, x, y, width, height, z_index):
        pos = self.position_style(
            x, y, width, height, z_index, "display:flex;align-items:center;gap:0;"
        )
        steps = props.get("steps", [])
        cur = int(props.get("current", 1))
        v = props.get("variant", "primary")
        items = []
        for i, s in enumerate(steps, 1):
            active = i == cur
            done = i < cur
            circle_bg = f"bg-{v}" if done or active else "bg-secondary"
            items.append(
                f'<div style="display:flex;flex-direction:column;align-items:center;flex:1;">'
                f'<div class="rounded-circle {circle_bg} text-white d-flex align-items-center justify-content-center" '
                f'style="width:30px;height:30px;font-size:13px;font-weight:bold;">'
                f'{"✓" if done else i}</div>'
                f'<small style="margin-top:4px;font-size:11px;{"font-weight:600;" if active else ""}">{s}</small></div>'
                + (
                    f'<div style="flex:1;height:2px;background:{"var(--bs-"+v+")" if done else "#dee2e6"};margin-top:-20px;"></div>'
                    if i < len(steps)
                    else ""
                )
            )
        return f'<div id="{comp_id}" style="{pos}" data-dsb="{name}">{"".join(items)}</div>'


# ═══════════════════════════════════════════════════════════════
#  TEMPO / TAREFAS
# ═══════════════════════════════════════════════════════════════


class TimerComponent(BaseComponent):
    type = "timer"
    label = "Timer"
    icon = "bi-alarm"
    group = "Tempo"

    @property
    def default_properties(self):
        return {
            "interval_ms": 1000,
            "enabled": False,
            "repeat": True,
            "label": "Timer1",
        }

    @property
    def default_size(self):
        return {"width": 150, "height": 40}

    @property
    def available_events(self):
        return ["onTick"]

    def render_html(self, comp_id, name, props, x, y, width, height, z_index):
        pos = self.position_style(
            x,
            y,
            width,
            height,
            z_index,
            "display:flex;align-items:center;gap:6px;"
            "background:#fff3cd;border:1px solid #ffc107;"
            "padding:4px 10px;border-radius:4px;",
        )
        return (
            f'<div id="{comp_id}" style="{pos}" data-dsb="{name}" '
            f'data-interval="{props.get("interval_ms",1000)}" '
            f'data-enabled="{str(props.get("enabled",False)).lower()}">'
            f'<i class="bi bi-alarm text-warning"></i>'
            f'<span style="font-size:12px;">{props.get("label","Timer")} '
            f'({props.get("interval_ms",1000)}ms)</span></div>'
        )


class CountdownComponent(BaseComponent):
    type = "countdown"
    label = "Countdown"
    icon = "bi-stopwatch"
    group = "Tempo"

    @property
    def default_properties(self):
        return {
            "seconds": 60,
            "format": "MM:SS",
            "auto_start": False,
            "font_size": 32,
            "color": "#4154f1",
        }

    @property
    def default_size(self):
        return {"width": 150, "height": 60}

    @property
    def available_events(self):
        return ["onTick", "onComplete"]

    def render_html(self, comp_id, name, props, x, y, width, height, z_index):
        pos = self.position_style(
            x,
            y,
            width,
            height,
            z_index,
            "display:flex;align-items:center;justify-content:center;",
        )
        fs = props.get("font_size", 32)
        col = props.get("color", "#4154f1")
        sec = int(props.get("seconds", 60))
        mm, ss = divmod(sec, 60)
        display = f"{mm:02d}:{ss:02d}"
        return (
            f'<div id="{comp_id}" style="{pos}" data-dsb="{name}" '
            f'data-seconds="{sec}" data-auto="{str(props.get("auto_start",False)).lower()}">'
            f'<span class="countdown-display" style="font-size:{fs}px;color:{col};font-weight:bold;'
            f'font-family:monospace;">{display}</span></div>'
        )
