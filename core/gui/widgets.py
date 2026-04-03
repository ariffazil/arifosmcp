"""
arifOS MCP - GUI Widgets for ChatGPT Apps SDK
══════════════════════════════════════════════════════════════════════════════

This module provides reusable UI components for rendering dashboards
in ChatGPT when mode="gui" is passed to tools.

Reference: https://github.com/openai/openai-apps-sdk-examples
"""

from typing import Optional, Any


class GUIWidget:
    """Base class for GUI widgets."""
    
    def to_component(self) -> dict:
        """Convert to ChatGPT Apps SDK component format."""
        raise NotImplementedError


class Stat(GUIWidget):
    """KPI card with title and value."""
    
    def __init__(self, title: str, value: str, trend: Optional[str] = None):
        self.title = title
        self.value = value
        self.trend = trend
    
    def to_component(self) -> dict:
        return {
            "type": "component",
            "kind": "stat",
            "title": self.title,
            "value": self.value,
            "trend": self.trend
        }


class Badge(GUIWidget):
    """Status badge."""
    
    STATUS_MAP = {
        "healthy": "success",
        "operational": "success",
        "stable": "success",
        "degraded": "warning",
        "warning": "warning",
        "error": "error",
        "critical": "error",
    }
    
    def __init__(self, label: str, status: str = "default"):
        self.label = label
        self.status = self.STATUS_MAP.get(status.lower(), status.lower())
    
    def to_component(self) -> dict:
        return {
            "type": "component",
            "kind": "badge",
            "label": self.label,
            "status": self.status
        }


class Progress(GUIWidget):
    """Progress bar with labels and values."""
    
    def __init__(self, labels: list[str], values: list[int]):
        self.labels = labels
        self.values = values
    
    def to_component(self) -> dict:
        return {
            "type": "component",
            "kind": "progress",
            "labels": self.labels,
            "values": self.values
        }


class TableColumn:
    """Table column definition."""
    
    def __init__(self, key: str, label: str):
        self.key = key
        self.label = label


class Table(GUIWidget):
    """Data table."""
    
    def __init__(self, columns: list[TableColumn], rows: list[dict]):
        self.columns = columns
        self.rows = rows
    
    def to_component(self) -> dict:
        return {
            "type": "component",
            "kind": "table",
            "columns": [{"key": c.key, "label": c.label} for c in self.columns],
            "rows": self.rows
        }


class Text(GUIWidget):
    """Text component with optional styling."""
    
    def __init__(self, text: str, font_size: Optional[str] = None, 
                 font_weight: Optional[str] = None, color: Optional[str] = None):
        self.text = text
        self.font_size = font_size
        self.font_weight = font_weight
        self.color = color
    
    def to_component(self) -> dict:
        result = {"type": "component", "kind": "text", "text": self.text}
        if self.font_size or self.font_weight or self.color:
            result["font"] = {}
            if self.font_size:
                result["font"]["size"] = self.font_size
            if self.font_weight:
                result["font"]["weight"] = self.font_weight
            if self.color:
                result["color"] = self.color
        return result


class Container(GUIWidget):
    """Container for layout (vstack/hstack/grid)."""
    
    def __init__(self, kind: str = "vstack", gap: int = 4, children: Optional[list] = None):
        self.kind = kind
        self.gap = gap
        self.children = children or []
    
    def add(self, widget: GUIWidget):
        """Add child widget."""
        self.children.append(widget.to_component())
        return self
    
    def to_component(self) -> dict:
        return {
            "type": "container",
            "kind": self.kind,
            "gap": self.gap,
            "children": self.children
        }


def header(text: str) -> Text:
    """Create header text."""
    return Text(text, font_size="xl", font_weight="bold")


def muted(text: str) -> Text:
    """Create muted text."""
    return Text(text, color="muted")


def kpi(title: str, value: str, trend: Optional[str] = None) -> Stat:
    """Create KPI stat."""
    return Stat(title, value, trend)


def status_badge(label: str, status: str) -> Badge:
    """Create status badge."""
    return Badge(label, status)


def progress_bar(labels: list[str], values: list[int]) -> Progress:
    """Create progress bar."""
    return Progress(labels, values)


def data_table(columns: list[TableColumn], rows: list[dict]) -> Table:
    """Create data table."""
    return Table(columns, rows)