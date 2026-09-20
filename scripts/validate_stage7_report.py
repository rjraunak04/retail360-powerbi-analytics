from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "powerbi" / "Retail360.Report" / "definition"
PAGES = REPORT / "pages"
MODEL_TABLES = ROOT / "powerbi" / "Retail360.SemanticModel" / "definition" / "tables"

EXPECTED_VISIBLE = [
    "Executive Overview",
    "Sales & Growth",
    "Product & Profitability",
    "Customer Analytics",
    "Channel / Reseller Analytics",
    "Geography & Territory",
    "Promotion Analysis",
    "Inventory Analytics",
    "Drill-through Detail",
    "Model / Data Quality",
]
ALLOWED_VISUALS = {"textbox", "cardVisual", "slicer", "lineChart", "barChart", "tableEx"}
EXPECTED_TOTAL_VISUALS = 62
EXPECTED_VISIBLE_VISUALS_PER_PAGE = 6
EXPECTED_TOOLTIP_VISUALS = 2


def fail(msg: str) -> None:
    raise SystemExit(f"Stage 7 report UX validation FAILED: {msg}")


def load(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid JSON {path.relative_to(ROOT)}: {exc}")


def model_contract():
    columns: dict[str, set[str]] = {}
    measures: set[str] = set()
    for path in MODEL_TABLES.glob("*.tmdl"):
        text = path.read_text(encoding="utf-8")
        table_match = re.search(r"^table\s+([^\n]+)", text, re.M)
        if not table_match:
            continue
        table = table_match.group(1).strip().strip("'")
        cols = set()
        for m in re.finditer(r"^\s*column\s+(?:'([^']+)'|([^\n]+))$", text, re.M):
            cols.add((m.group(1) or m.group(2)).strip())
        columns[table] = cols
        for m in re.finditer(r"^\s*measure\s+(?:'([^']+)'|([^=\n]+?))\s*=", text, re.M):
            measures.add((m.group(1) or m.group(2)).strip())
    return columns, measures


def field_refs(node):
    if isinstance(node, dict):
        if "Measure" in node and isinstance(node["Measure"], dict):
            m = node["Measure"]
            entity = (((m.get("Expression") or {}).get("SourceRef") or {}).get("Entity"))
            prop = m.get("Property")
            if entity and prop:
                yield ("measure", entity, prop)
        if "Column" in node and isinstance(node["Column"], dict):
            c = node["Column"]
            entity = (((c.get("Expression") or {}).get("SourceRef") or {}).get("Entity"))
            prop = c.get("Property")
            if entity and prop:
                yield ("column", entity, prop)
        for value in node.values():
            yield from field_refs(value)
    elif isinstance(node, list):
        for value in node:
            yield from field_refs(value)


def overlaps(a, b):
    return not (
        a["x"] + a["width"] <= b["x"] or
        b["x"] + b["width"] <= a["x"] or
        a["y"] + a["height"] <= b["y"] or
        b["y"] + b["height"] <= a["y"]
    )


def main() -> None:
    columns, measures = model_contract()
    metadata = load(PAGES / "pages.json")
    order = metadata.get("pageOrder", [])
    if len(order) != 11:
        fail(f"expected 11 report pages (10 visible + 1 tooltip), found {len(order)}")
    if metadata.get("activePageName") != order[0]:
        fail("Executive Overview is not the active page")

    visible_names = []
    visual_types = set()
    total_visuals = 0
    drillthrough_ok = False
    tooltip_ok = False

    for page_id in order:
        if not re.fullmatch(r"[0-9a-f]{20}", page_id):
            fail(f"page id is not a 20-char lowercase hex id: {page_id}")
        page_dir = PAGES / page_id
        page = load(page_dir / "page.json")
        if page.get("name") != page_id:
            fail(f"page name/path mismatch: {page_id}")
        if page.get("displayName") != "Product Tooltip":
            visible_names.append(page.get("displayName"))
            if page.get("width") != 1280 or page.get("height") != 720:
                fail(f"{page.get('displayName')} must use 1280x720 canvas")
            if page.get("displayOption") != "FitToPage":
                fail(f"{page.get('displayName')} must use FitToPage")
            annotations = page.get("annotations") or []
            if not any(a.get("name") == "Retail360.Stage7Purpose" and a.get("value") for a in annotations):
                fail(f"{page.get('displayName')} is missing Retail360.Stage7Purpose annotation")
        else:
            if page.get("visibility") != "HiddenInViewMode" or page.get("type") != "Tooltip":
                fail("Product Tooltip must be a hidden tooltip page")
            if page.get("pageBinding", {}).get("type") != "Tooltip":
                fail("Product Tooltip pageBinding is missing")
            tooltip_ok = True

        if page.get("displayName") == "Drill-through Detail":
            if page.get("type") != "Drillthrough":
                fail("Drill-through Detail page type is missing")
            binding = page.get("pageBinding", {})
            filters = page.get("filterConfig", {}).get("filters", [])
            if binding.get("type") != "Drillthrough" or not binding.get("parameters") or not filters:
                fail("Drill-through Detail is not fully bound")
            if binding["parameters"][0].get("boundFilter") != filters[0].get("name"):
                fail("Drillthrough parameter/filter binding mismatch")
            drillthrough_ok = True

        visual_dir = page_dir / "visuals"
        visuals = []
        if visual_dir.exists():
            for vpath in visual_dir.glob("*/visual.json"):
                v = load(vpath)
                if v.get("name") != vpath.parent.name:
                    fail(f"visual name/path mismatch: {vpath.relative_to(ROOT)}")
                if not re.fullmatch(r"[0-9a-f]{20}", v.get("name", "")):
                    fail(f"visual id is not 20-char lowercase hex: {v.get('name')}")
                pos = v.get("position", {})
                for key in ("x", "y", "width", "height"):
                    if key not in pos:
                        fail(f"visual {v.get('name')} missing position.{key}")
                if pos["x"] < 0 or pos["y"] < 0 or pos["width"] <= 0 or pos["height"] <= 0:
                    fail(f"invalid visual bounds on {page.get('displayName')}: {v.get('name')}")
                if pos["x"] + pos["width"] > page["width"] or pos["y"] + pos["height"] > page["height"]:
                    fail(f"visual exceeds page bounds on {page.get('displayName')}: {v.get('name')}")

                vtype = (v.get("visual") or {}).get("visualType")
                if vtype not in ALLOWED_VISUALS:
                    fail(f"unsupported Stage 7 visual type: {vtype}")
                visual_types.add(vtype)

                if vtype == "cardVisual":
                    q = (((v.get("visual") or {}).get("query") or {}).get("queryState") or {})
                    if "Data" not in q or "Fields" in q:
                        fail(f"cardVisual {v.get('name')} must use Data role")
                if vtype == "slicer":
                    q = (((v.get("visual") or {}).get("query") or {}).get("queryState") or {})
                    if set(q) != {"Values"}:
                        fail(f"slicer {v.get('name')} must use only Values role")
                if vtype == "tableEx":
                    objects = (v.get("visual") or {}).get("objects") or {}
                    headers = objects.get("columnHeaders") or []
                    if not headers:
                        fail(f"tableEx {v.get('name')} missing grow-to-fit header config")

                for kind, entity, prop in field_refs(v):
                    if kind == "measure":
                        if entity != "KPI_Measures" or prop not in measures:
                            fail(f"unknown measure binding {entity}.{prop}")
                    else:
                        if entity not in columns or prop not in columns[entity]:
                            fail(f"unknown column binding {entity}.{prop}")

                visuals.append(v)

        total_visuals += len(visuals)
        expected_count = EXPECTED_TOOLTIP_VISUALS if page.get("displayName") == "Product Tooltip" else EXPECTED_VISIBLE_VISUALS_PER_PAGE
        if len(visuals) != expected_count:
            fail(f"{page.get('displayName')} has {len(visuals)} visuals; expected exactly {expected_count}")

        tab_orders = [v.get("position", {}).get("tabOrder") for v in visuals]
        if any(not isinstance(x, int) for x in tab_orders):
            fail(f"{page.get('displayName')} has a visual without integer tabOrder")
        if sorted(tab_orders) != list(range(len(visuals))):
            fail(f"{page.get('displayName')} tabOrder must be contiguous 0..{len(visuals)-1}")

        z_orders = [v.get("position", {}).get("z") for v in visuals]
        if len(z_orders) != len(set(z_orders)):
            fail(f"{page.get('displayName')} has duplicate z-order values")

        if page.get("displayName") != "Product Tooltip":
            title_boxes = []
            for vis in visuals:
                if ((vis.get("visual") or {}).get("visualType")) != "textbox":
                    continue
                text_blob = json.dumps((vis.get("visual") or {}).get("objects") or {})
                if page.get("displayName") in text_blob:
                    title_boxes.append(vis)
            if len(title_boxes) != 1:
                fail(f"{page.get('displayName')} must have exactly one page-title textbox")

        # No accidental layout overlaps.
        for i, a in enumerate(visuals):
            for b in visuals[i+1:]:
                if overlaps(a["position"], b["position"]):
                    fail(f"visual overlap on {page.get('displayName')}: {a['name']} vs {b['name']}")

    if total_visuals != EXPECTED_TOTAL_VISUALS:
        fail(f"expected exactly {EXPECTED_TOTAL_VISUALS} visual containers, found {total_visuals}")

    if visible_names != EXPECTED_VISIBLE:
        fail(f"visible page order mismatch: {visible_names}")
    if not drillthrough_ok:
        fail("drillthrough page validation did not run")
    if not tooltip_ok:
        fail("tooltip page validation did not run")

    required_types = {"textbox", "cardVisual", "slicer", "lineChart", "barChart", "tableEx"}
    missing = required_types - visual_types
    if missing:
        fail(f"missing required visual types: {sorted(missing)}")

    print("Retail360 Stage 7 report UX")
    print("-" * 76)
    print("Visible pages:            10/10 PASS")
    print("Hidden tooltip pages:      1/1 PASS")
    print(f"Visual containers:         {total_visuals}/{EXPECTED_TOTAL_VISUALS} PASS")
    print("Page purpose/title policy: PASS")
    print("Tab/z-order policy:        PASS")
    print("Canvas bounds/overlap:     PASS")
    print("Semantic field bindings:   PASS")
    print("KPI measure bindings:      PASS")
    print("Slicer/card role policy:   PASS")
    print("Drillthrough binding:      PASS")
    print("Report-page tooltip:       PASS")
    print("Table grow-to-fit policy:  PASS")
    print("-" * 76)
    print("Stage 7 PBIR report UX validation PASSED.")


if __name__ == "__main__":
    main()
