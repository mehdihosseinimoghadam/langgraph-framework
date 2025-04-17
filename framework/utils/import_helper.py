import importlib
from typing import Any, Callable, Type


def import_from_string(import_string: str) -> Any:
    """
    Import a dotted module path and return the attribute/class designated by the
    last name in the path.

    Example:
        import_from_string('module.submodule.MyClass')
    """
    try:
        module_path, class_name = import_string.rsplit('.', 1)
    except ValueError:
        raise ImportError(f"{import_string} doesn't look like a module path")

    module = importlib.import_module(module_path)

    try:
        return getattr(module, class_name)
    except AttributeError:
        raise ImportError(
            f"Module '{module_path}' does not define a '{class_name}' attribute/class")
