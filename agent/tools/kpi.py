"""Governed KPI metadata for Retail360."""

from pathlib import Path
from typing import Any

from .base import ToolResult

ROOT = Path(__file__).resolve().parents[2]
DICTIONARY = ROOT / "docs" / "powerbi" / "kpi-dictionary.md"


def load_kpis(path: Path = DICTIONARY):
    section = ""
    result = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line.startswith("## "):
            section = line[3:].strip()
        elif line.startswith("| ") and line.count("|") >= 3:
            parts = [p.strip() for p in line.strip("|").split("|")]
            if len(parts) >= 2 and parts[0] != "Measure" and not parts[0].startswith("---"):
                result[parts[0]] = {"definition": parts[1], "section": section}
        elif section == "Inventory" and line.startswith("- ") and ":" in line:
            name, definition = line[2:].split(":", 1)
            result[name.strip()] = {"definition": definition.strip(), "section": section}
    return result


class KpiMetadataTool:
    name = "kpi_metadata"
    description = "Find governed Retail360 KPI definitions."

    def __init__(self, dictionary_path: Path = DICTIONARY):
        self.dictionary_path = dictionary_path

    def run(self, **kwargs: Any) -> ToolResult:
        query = str(kwargs.get("query", "")).casefold().strip()
        if not query:
            return ToolResult(tool_name=self.name, ok=False, error="query must be non-empty")
        kpis = load_kpis(self.dictionary_path)
        exact = [(n, v) for n, v in kpis.items() if n.casefold() == query]
        matches = exact or [(n, v) for n, v in kpis.items() if query in n.casefold() or query in v["definition"].casefold() or query in v["section"].casefold()]
        data = [{"measure": n, **v} for n, v in matches[:20]]
        return ToolResult(tool_name=self.name, ok=True, data=data, metadata={"match_count": len(matches), "source": "docs/powerbi/kpi-dictionary.md", "governed": True})
