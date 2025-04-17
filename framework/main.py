import os
import argparse
import json
import yaml
from typing import Dict, Any

from framework.core.config import ConfigLoader
from framework.core.engine import PipelineEngine


def main():
    """Main entry point for the framework CLI."""
    parser = argparse.ArgumentParser(
        description="LangGraph Agential Framework")

    # Add subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run a pipeline")
    run_parser.add_argument(
        "config", help="Path to the pipeline configuration file")
    run_parser.add_argument(
        "--input", "-i", help="JSON string or path to JSON file with input data")
    run_parser.add_argument(
        "--thread-id", "-t", default="default", help="Thread ID for conversation state")

    # Stream command
    stream_parser = subparsers.add_parser(
        "stream", help="Stream a pipeline execution")
    stream_parser.add_argument(
        "config", help="Path to the pipeline configuration file")
    stream_parser.add_argument(
        "--input", "-i", help="JSON string or path to JSON file with input data")
    stream_parser.add_argument(
        "--thread-id", "-t", default="default", help="Thread ID for conversation state")

    # Example command
    example_parser = subparsers.add_parser(
        "example", help="Run an example pipeline")
    example_parser.add_argument(
        "name", choices=["joke"], help="Name of the example to run")
    example_parser.add_argument(
        "--topic", "-t", default="programming", help="Topic for the joke example")
    example_parser.add_argument(
        "--stream", "-s", action="store_true", help="Stream the execution")

    # Add Langfuse configuration options
    parser.add_argument("--langfuse-public-key", help="Langfuse public key")
    parser.add_argument("--langfuse-secret-key", help="Langfuse secret key")
    parser.add_argument("--langfuse-host", help="Langfuse host URL")

    args = parser.parse_args()

    # Set Langfuse environment variables if provided
    if args.langfuse_public_key:
        os.environ["LANGFUSE_PUBLIC_KEY"] = args.langfuse_public_key
    if args.langfuse_secret_key:
        os.environ["LANGFUSE_SECRET_KEY"] = args.langfuse_secret_key
    if args.langfuse_host:
        os.environ["LANGFUSE_HOST"] = args.langfuse_host

    # Handle commands
    if args.command == "run":
        run_pipeline(args.config, args.input, args.thread_id)
    elif args.command == "stream":
        stream_pipeline(args.config, args.input, args.thread_id)
    elif args.command == "example":
        run_example(args.name, args)
    else:
        parser.print_help()


def load_input_data(input_arg: str) -> Dict[str, Any]:
    """Load input data from a JSON string or file."""
    if not input_arg:
        return {}

    if os.path.exists(input_arg):
        with open(input_arg, 'r') as f:
            if input_arg.endswith('.json'):
                return json.load(f)
            elif input_arg.endswith(('.yaml', '.yml')):
                return yaml.safe_load(f)

    try:
        return json.loads(input_arg)
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON input: {input_arg}")


def run_pipeline(config_path: str, input_arg: str, thread_id: str):
    """Run a pipeline with the given configuration and input."""
    # Load the configuration
    config = ConfigLoader.load_config(config_path)

    # Load input data
    inputs = load_input_data(input_arg) if input_arg else {}

    # Create the pipeline engine
    engine = PipelineEngine(config)

    # Run the pipeline
    result = engine.run(inputs, thread_id)

    # Print the result
    print(json.dumps(result, indent=2, default=str))


def stream_pipeline(config_path: str, input_arg: str, thread_id: str):
    """Stream a pipeline execution with the given configuration and input."""
    # Load the configuration
    config = ConfigLoader.load_config(config_path)

    # Load input data
    inputs = load_input_data(input_arg) if input_arg else {}

    # Create the pipeline engine
    engine = PipelineEngine(config)

    # Stream the pipeline execution
    for event in engine.stream(inputs, thread_id):
        print(f"Event: {json.dumps(event, indent=2, default=str)}")
        print("-" * 50)


def run_example(example_name: str, args):
    """Run an example pipeline."""
    if example_name == "joke":
        from framework.examples.joke_pipeline import run_joke_pipeline, stream_joke_pipeline

        if args.stream:
            for event in stream_joke_pipeline(args.topic):
                print(f"Event: {json.dumps(event, indent=2, default=str)}")
                print("-" * 50)
        else:
            result = run_joke_pipeline(args.topic)
            print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
