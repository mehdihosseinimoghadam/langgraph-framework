import os
import yaml
import json
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field
from ..utils.import_helper import import_from_string
from .errors import ConfigError


class NodeConfig(BaseModel):
    """Configuration for a single node in the pipeline."""
    id: str
    role: str
    type: str
    model: Optional[str] = None
    temperature: Optional[float] = None
    prompt_template: Optional[str] = None
    tool: Optional[str] = None
    output: Optional[Dict[str, str]] = None

    def validate_node_config(self):
        """Validate that the node configuration is consistent."""
        if self.type == "llm":
            if not self.model:
                raise ConfigError(
                    f"Node {self.id} is of type 'llm' but has no model specified")
            if not self.prompt_template:
                raise ConfigError(
                    f"Node {self.id} is of type 'llm' but has no prompt_template specified")
        elif self.type == "tool":
            if not self.tool:
                raise ConfigError(
                    f"Node {self.id} is of type 'tool' but has no tool specified")
        else:
            raise ConfigError(f"Node {self.id} has unknown type: {self.type}")

        return True


class PipelineConfig(BaseModel):
    """Configuration for the entire pipeline."""
    name: str
    version: str = "1.0"
    description: Optional[str] = None
    settings: Optional[Dict[str, Any]] = Field(default_factory=dict)
    inputs: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    nodes: List[NodeConfig]
    output: Optional[Dict[str, str]] = None


class ConfigLoader:
    """Loads and validates configuration files."""

    @staticmethod
    def load_config(config_path: str) -> PipelineConfig:
        """Load a configuration file from the given path."""
        if not os.path.exists(config_path):
            raise ConfigError(f"Config file not found: {config_path}")

        _, ext = os.path.splitext(config_path)

        try:
            if ext.lower() == '.yaml' or ext.lower() == '.yml':
                with open(config_path, 'r') as f:
                    config_data = yaml.safe_load(f)
            elif ext.lower() == '.json':
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
            else:
                raise ConfigError(f"Unsupported config file format: {ext}")

            # Convert nodes to NodeConfig objects if they're not already
            if 'nodes' in config_data and isinstance(config_data['nodes'], list):
                config_data['nodes'] = [
                    NodeConfig(**node) if not isinstance(node,
                                                         NodeConfig) else node
                    for node in config_data['nodes']
                ]

            # Validate each node configuration
            for node in config_data.get('nodes', []):
                if isinstance(node, dict):
                    NodeConfig(**node).validate_node_config()
                else:
                    node.validate_node_config()

            return PipelineConfig(**config_data)

        except (yaml.YAMLError, json.JSONDecodeError) as e:
            raise ConfigError(f"Error parsing config file: {e}")
        except Exception as e:
            raise ConfigError(f"Error loading config: {e}")
