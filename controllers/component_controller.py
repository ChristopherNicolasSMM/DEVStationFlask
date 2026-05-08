"""controllers/component_controller.py — Componentes v3.0"""
from flask import Blueprint, jsonify, request
from models import db, Component, Page

bp = Blueprint("component", __name__)

@bp.route("/api/componentes/<int:cid>", methods=["PUT"])
def update_component(cid: int):
    comp = Component.query.get_or_404(cid)
    data = request.get_json(force=True) or {}
    for key in ("x","y","width","height","z_index","type","name","properties","events","rules"):
        if key in data:
            setattr(comp, key, data[key])
    db.session.commit()
    return jsonify(comp.to_dict())

@bp.route("/api/componentes/<int:cid>", methods=["DELETE"])
def delete_component(cid: int):
    comp = Component.query.get_or_404(cid)
    db.session.delete(comp)
    db.session.commit()
    return jsonify({"ok": True})

@bp.route("/api/paginas/<int:pgid>/componentes", methods=["POST"])
def add_component(pgid: int):
    Page.query.get_or_404(pgid)
    data = request.get_json(force=True) or {}
    count = Component.query.filter_by(page_id=pgid).count()
    comp = Component(
        page_id=pgid,
        type=data.get("type","label"),
        name=data.get("name", f"comp_{count+1}"),
        x=int(data.get("x", 100)), y=int(data.get("y", 100)),
        width=int(data.get("width", 150)), height=int(data.get("height", 40)),
        z_index=count+1,
        properties=data.get("properties",{}),
        events=data.get("events",{}),
        rules=data.get("rules",[]),
    )
    db.session.add(comp)
    db.session.commit()
    return jsonify(comp.to_dict()), 201
