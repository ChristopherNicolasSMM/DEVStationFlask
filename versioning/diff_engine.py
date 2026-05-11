"""
versioning/diff_engine.py — Motor de Diff entre Versões
=========================================================
Compara dois snapshots de página e retorna resumo das diferenças.
"""

import logging

log = logging.getLogger(__name__)


def diff_versions(snapshot_a: dict, snapshot_b: dict) -> dict:
    """
    Compara dois snapshots page.to_dict(include_components=True).

    Returns:
        {
            "added":   [comp_names],
            "removed": [comp_names],
            "changed": [comp_names],
            "canvas_changed": bool,
            "total_changes": N,
        }
    """
    comps_a = {c["name"]: c for c in (snapshot_a.get("components") or [])}
    comps_b = {c["name"]: c for c in (snapshot_b.get("components") or [])}

    names_a = set(comps_a.keys())
    names_b = set(comps_b.keys())

    added = sorted(names_b - names_a)
    removed = sorted(names_a - names_b)
    changed = []

    for name in names_a & names_b:
        ca = comps_a[name]
        cb = comps_b[name]
        if _comp_changed(ca, cb):
            changed.append(name)

    canvas_changed = (
        snapshot_a.get("canvas_w") != snapshot_b.get("canvas_w")
        or snapshot_a.get("canvas_h") != snapshot_b.get("canvas_h")
        or snapshot_a.get("canvas_bg") != snapshot_b.get("canvas_bg")
    )

    return {
        "added": added,
        "removed": removed,
        "changed": sorted(changed),
        "canvas_changed": canvas_changed,
        "total_changes": len(added)
        + len(removed)
        + len(changed)
        + (1 if canvas_changed else 0),
    }


def _comp_changed(a: dict, b: dict) -> bool:
    """Retorna True se houve mudança relevante num componente."""
    for key in (
        "x",
        "y",
        "width",
        "height",
        "z_index",
        "type",
        "properties",
        "events",
        "rules",
    ):
        if a.get(key) != b.get(key):
            return True
    return False
