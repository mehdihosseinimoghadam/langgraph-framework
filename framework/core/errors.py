class FrameworkError(Exception):
    """Base exception for all framework errors."""
    pass


class ConfigError(FrameworkError):
    """Error in configuration."""
    pass


class NodeError(FrameworkError):
    """Error in node execution."""
    pass


class SchemaError(FrameworkError):
    """Error in schema validation."""
    pass


class PromptError(FrameworkError):
    """Error in prompt template."""
    pass


class ToolError(FrameworkError):
    """Error in tool execution."""
    pass
