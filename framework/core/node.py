from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Type, Union
from pydantic import BaseModel
from ..utils.template import TemplateRenderer
from ..utils.import_helper import import_from_string
from .errors import NodeError, SchemaError


class Node(ABC):
    """Base class for all nodes in the pipeline."""

    def __init__(self, id: str, role: str):
        self.id = id
        self.role = role

    @abstractmethod
    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process the input context and return an updated context."""
        pass

    def validate_output(self, output: Any, schema_path: Optional[str] = None) -> Any:
        """Validate the output against a schema if provided."""
        if not schema_path:
            return output

        try:
            schema_class = import_from_string(schema_path)
            if not issubclass(schema_class, BaseModel):
                raise SchemaError(
                    f"Schema {schema_path} is not a Pydantic model")

            # If output is already an instance of the schema class, return it
            if isinstance(output, schema_class):
                return output

            # Otherwise, validate and convert
            return schema_class.parse_obj(output)
        except ImportError:
            raise SchemaError(f"Could not import schema: {schema_path}")
        except Exception as e:
            raise SchemaError(
                f"Error validating output with schema {schema_path}: {e}")


class LLMNode(Node):
    """Node that processes input using a language model."""

    def __init__(
        self,
        id: str,
        role: str,
        model: str,
        prompt_template: str,
        temperature: float = 0.7,
        output_type: str = "raw",
        output_schema: Optional[str] = None
    ):
        super().__init__(id, role)
        self.model = model
        self.prompt_template = prompt_template
        self.temperature = temperature
        self.output_type = output_type
        self.output_schema = output_schema
        self.template_renderer = TemplateRenderer()

    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process the input using the language model."""
        try:
            # Render the prompt template with the current context
            prompt = self.template_renderer.render(
                self.prompt_template, context)

            # Import the appropriate LLM class based on the model name
            if "gpt" in self.model.lower() or "openai" in self.model.lower():
                try:
                    from langchain_openai import ChatOpenAI
                except ImportError:
                    raise ImportError(
                        "langchain_openai is not installed. Please install it with: "
                        "pip install langchain-openai"
                    )
                llm = ChatOpenAI(model=self.model,
                                 temperature=self.temperature)
            elif "claude" in self.model.lower() or "anthropic" in self.model.lower():
                try:
                    from langchain_anthropic import ChatAnthropic
                except ImportError:
                    raise ImportError(
                        "langchain_anthropic is not installed. Please install it with: "
                        "pip install langchain-anthropic"
                    )
                llm = ChatAnthropic(
                    model=self.model, temperature=self.temperature)
            else:
                # Fallback to a mock LLM for testing or when specific models aren't available
                from langchain.llms.fake import FakeListLLM
                llm = FakeListLLM(
                    responses=["This is a mock response from the LLM."])
                print(
                    f"WARNING: Using mock LLM for model '{self.model}'. Install appropriate packages for real LLM usage.")

            # Invoke the LLM
            response = llm.invoke(prompt)

            # Process the output based on the specified output type
            if self.output_type == "raw":
                output = response.content
            elif self.output_type == "json":
                import json
                try:
                    output = json.loads(response.content)
                except json.JSONDecodeError:
                    raise NodeError(
                        f"LLM response is not valid JSON: {response.content}")
            elif self.output_type == "pydantic":
                if not self.output_schema:
                    raise NodeError(
                        "Output type is 'pydantic' but no schema specified")

                import json
                try:
                    # First try to parse as JSON
                    json_output = json.loads(response.content)
                    output = self.validate_output(
                        json_output, self.output_schema)
                except json.JSONDecodeError:
                    # If not JSON, try to extract structured data from text
                    try:
                        from langchain.output_parsers import PydanticOutputParser
                    except ImportError:
                        raise ImportError(
                            "langchain is not installed. Please install it with: "
                            "pip install langchain"
                        )
                    parser = PydanticOutputParser(
                        pydantic_object=import_from_string(self.output_schema))
                    output = parser.parse(response.content)
            else:
                raise NodeError(f"Unsupported output type: {self.output_type}")

            return {self.id: output}

        except ImportError as e:
            raise NodeError(f"Missing dependency in LLM node {self.id}: {e}")
        except Exception as e:
            raise NodeError(f"Error in LLM node {self.id}: {e}")


class ToolNode(Node):
    """Node that executes a tool function."""

    def __init__(
        self,
        id: str,
        role: str,
        tool_path: str,
        output_type: str = "raw",
        output_schema: Optional[str] = None
    ):
        super().__init__(id, role)
        self.tool_path = tool_path
        self.output_type = output_type
        self.output_schema = output_schema

        # Import the tool function
        try:
            self.tool_function = import_from_string(tool_path)
        except ImportError:
            raise NodeError(f"Could not import tool: {tool_path}")

    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool function with the current context."""
        try:
            # Execute the tool function
            result = self.tool_function(context)

            # Process the output based on the specified output type
            if self.output_type == "pydantic" and self.output_schema:
                result = self.validate_output(result, self.output_schema)

            return {self.id: result}

        except Exception as e:
            raise NodeError(f"Error in tool node {self.id}: {e}")
