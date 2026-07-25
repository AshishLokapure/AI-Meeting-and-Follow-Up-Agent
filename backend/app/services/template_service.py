from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape


class TemplateService:
    def __init__(self) -> None:
        template_dir = Path(__file__).resolve().parents[1] / "templates" / "emails"
        self.env = Environment(loader=FileSystemLoader(str(template_dir)), autoescape=select_autoescape(["html", "xml"]))

    def render(self, template_name: str, context: dict[str, Any]) -> str:
        template = self.env.get_template(f"{template_name}.html")
        return template.render(**context)
