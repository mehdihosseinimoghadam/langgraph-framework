import os
import jinja2
from typing import Dict, Any
from ..core.errors import PromptError


class TemplateRenderer:
    """Renders templates using Jinja2."""

    def __init__(self, templates_dir: str = None):
        self.templates_dir = templates_dir or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "prompts")
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.templates_dir),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )

    def render(self, template_path: str, context: Dict[str, Any]) -> str:
        """
        Render a template with the given context.

        Args:
            template_path: Path to the template file, relative to templates_dir
            context: Dictionary of variables to use in the template

        Returns:
            Rendered template as a string
        """
        try:
            # Check if template_path is a file path or a template string
            if os.path.exists(template_path):
                with open(template_path, 'r') as f:
                    template_str = f.read()
                template = jinja2.Template(template_str)
            elif os.path.exists(os.path.join(self.templates_dir, template_path)):
                template = self.env.get_template(template_path)
            else:
                # Assume it's a template string
                template = jinja2.Template(template_path)

            return template.render(**context)
        except jinja2.exceptions.TemplateError as e:
            raise PromptError(f"Error rendering template {template_path}: {e}")
        except Exception as e:
            raise PromptError(f"Error loading template {template_path}: {e}")
