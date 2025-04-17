from typing import Dict, Any, List, Optional, Union
import importlib
import logging
from pydantic import BaseModel

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from typing_extensions import TypedDict, Annotated

from .config import PipelineConfig, NodeConfig
from .node import LLMNode, ToolNode
from .errors import ConfigError, NodeError
from ..utils.import_helper import import_from_string

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PipelineEngine:
    """Main engine for executing the pipeline defined in the configuration."""

    def __init__(self, config: PipelineConfig):
        self.config = config
        self.nodes = {}
        self.graph = None
        self.checkpointer = MemorySaver()

        # Initialize nodes
        self._initialize_nodes()

    def _initialize_nodes(self):
        """Initialize all nodes defined in the configuration."""
        for node_config in self.config.nodes:
            if node_config.type == "llm":
                self.nodes[node_config.id] = LLMNode(
                    id=node_config.id,
                    role=node_config.role,
                    model=node_config.model,
                    prompt_template=node_config.prompt_template,
                    temperature=node_config.temperature or 0.7,
                    output_type=node_config.output.get(
                        "type", "raw") if node_config.output else "raw",
                    output_schema=node_config.output.get(
                        "schema") if node_config.output else None
                )
            elif node_config.type == "tool":
                self.nodes[node_config.id] = ToolNode(
                    id=node_config.id,
                    role=node_config.role,
                    tool_path=node_config.tool,
                    output_type=node_config.output.get(
                        "type", "raw") if node_config.output else "raw",
                    output_schema=node_config.output.get(
                        "schema") if node_config.output else None
                )

    def _create_state_class(self):
        """Create a TypedDict class for the state based on node outputs."""
        # Define the state class dynamically
        from typing import Any
        import types

        # Create base dictionary with messages field
        state_dict = {
            "messages": Annotated[list, add_messages],
            "inputs": dict,  # Store input values
        }

        # Add fields for each node's output with a prefix to avoid conflicts
        for node_id in self.nodes:
            state_dict[f"node_output_{node_id}"] = Any

        # Create the TypedDict class using types.new_class
        namespace = {'__annotations__': state_dict}
        State = types.new_class("State", (TypedDict,),
                                {}, lambda ns: ns.update(namespace))

        return State

    def _create_node_functions(self):
        """Create functions for each node to be used in the graph."""
        node_functions = {}

        for node_id, node in self.nodes.items():
            def create_node_func(node):
                def node_func(state):
                    # Extract relevant context from state
                    context = {
                        # Include original inputs
                        **state.get("inputs", {}),
                    }

                    # Add node outputs to context with their original IDs
                    for k, v in state.items():
                        if k.startswith("node_output_"):
                            # Remove "node_output_" prefix
                            original_id = k[12:]
                            context[original_id] = v

                    # Special handling for specific node types
                    if node.id == "novel_creator" and "topic_generator" in context:
                        # Make topic_generator output available as novel_topics
                        context["novel_topics"] = context["topic_generator"]

                    if node.id == "novel_combiner" and "novel_creator" in context:
                        # Make novel_creator output available as novel_outlines
                        context["novel_outlines"] = context["novel_creator"]

                    # Process the node
                    result = node.process(context)

                    # Return the node's output with a prefixed key to avoid conflict
                    return {f"node_output_{node.id}": result.get(node.id)}

                return node_func

            # Use a unique name for the node in the graph
            graph_node_id = f"graph_node_{node_id}"
            node_functions[graph_node_id] = create_node_func(node)

        return node_functions

    def build_graph(self):
        """Build the LangGraph StateGraph based on the configuration."""
        # Create the state class
        State = self._create_state_class()

        # Create the graph builder
        graph_builder = StateGraph(State)

        # Create node functions
        node_functions = self._create_node_functions()

        # Add nodes to the graph
        for graph_node_id, node_func in node_functions.items():
            graph_builder.add_node(graph_node_id, node_func)

        # Add edges based on node order in config
        prev_graph_node = None
        for node_config in self.config.nodes:
            graph_node_id = f"graph_node_{node_config.id}"

            if prev_graph_node is None:
                # First node, connect from START
                graph_builder.add_edge(START, graph_node_id)
            else:
                # Connect from previous node
                graph_builder.add_edge(prev_graph_node, graph_node_id)

            prev_graph_node = graph_node_id

        # Connect last node to END
        if prev_graph_node:
            graph_builder.add_edge(prev_graph_node, END)

        # Compile the graph
        self.graph = graph_builder.compile(checkpointer=self.checkpointer)
        return self.graph

    def run(self, inputs: Dict[str, Any], thread_id: str = "default"):
        """Run the pipeline with the given inputs."""
        if not self.graph:
            self.build_graph()

        # Prepare the initial state
        initial_state = {
            "messages": [{"role": "user", "content": inputs.get("user_input", "")}],
            "inputs": inputs  # Store all inputs in a dedicated field
        }

        # Run the graph
        config = {"configurable": {"thread_id": thread_id}}
        result = self.graph.invoke(initial_state, config)

        # Process the result to extract node outputs
        processed_result = {}
        for key, value in result.items():
            if key.startswith("node_output_"):
                # Extract the original node ID from the output key
                node_id = key[12:]  # Remove "node_output_" prefix
                processed_result[node_id] = value
            elif key != "inputs":  # Skip the inputs field
                processed_result[key] = value

        return processed_result

    def stream(self, inputs: Dict[str, Any], thread_id: str = "default"):
        """Stream the pipeline execution with the given inputs."""
        if not self.graph:
            self.build_graph()

        # Prepare the initial state
        initial_state = {
            "messages": [{"role": "user", "content": inputs.get("user_input", "")}],
            "inputs": inputs  # Store all inputs in a dedicated field
        }

        # Stream the graph execution
        config = {"configurable": {"thread_id": thread_id}}
        for event in self.graph.stream(initial_state, config, stream_mode="values"):
            # Process the event to extract node outputs
            processed_event = {}
            for key, value in event.items():
                if key.startswith("node_output_"):
                    # Extract the original node ID from the output key
                    node_id = key[12:]  # Remove "node_output_" prefix
                    processed_event[node_id] = value
                elif key != "inputs":  # Skip the inputs field
                    processed_event[key] = value

            yield processed_event
