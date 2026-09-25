"""Governed semantic metadata access for Retail360."""

import json
from pathlib import Path
from typing import Any

from .base import ToolResult

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "powerbi" / "semantic-model-contract.json"


class SemanticMetadataTool:
    name = "semantic_metadata"
    description = "Inspect governed Retail360 semantic model metadata."

    def __init__(self, contract_path: Path = CONTRACT):
        self.contract_path = contract_path

    def run(self, **kwargs: Any) -> ToolResult:
        model = json.loads(self.contract_path.read_text(encoding="utf-8"))
        action = kwargs.get("action", "summary")
        if action == "summary":
            data = {"model_name": model["modelName"], "storage_mode": model["storageMode"], "source": model["source"], "date_table": model["dateTable"], "tables": sorted(model["tables"]), "relationship_count": len(model["relationships"])}
        elif action == "table":
            name = kwargs.get("table")
            table = model["tables"].get(name)
            if table is None:
                return ToolResult(tool_name=self.name, ok=False, error=f"Unknown semantic table: {name}")
            data = {"table": name, **table}
        elif action == "relationships":
            name = kwargs.get("table")
            data = model["relationships"]
            if name:
                data = [r for r in data if name in (r["from"][0], r["to"][0])]
        elif action == "search":
            needle = str(kwargs.get("query", "")).casefold().strip()
            if not needle:
                return ToolResult(tool_name=self.name, ok=False, error="search requires a query")
            data = []
            for table_name, table in model["tables"].items():
                for display, source, dtype in table["columns"]:
                    if needle in display.casefold() or needle in source.casefold():
                        data.append({"table": table_name, "source_table": table["source"], "column": display, "source_column": source, "data_type": dtype})
        else:
            return ToolResult(tool_name=self.name, ok=False, error=f"Unsupported metadata action: {action}")
        return ToolResult(tool_name=self.name, ok=True, data=data, metadata={"source": "powerbi/semantic-model-contract.json", "governed": True})
