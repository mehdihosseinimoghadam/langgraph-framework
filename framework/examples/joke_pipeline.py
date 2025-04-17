import os
import yaml
from typing import Dict, Any

# Get the absolute path to the framework directory
FRAMEWORK_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Define the pipeline configuration
joke_pipeline_config = {
    "name": "Joke Generator Pipeline",
    "version": "1.0",
    "description": "Generates and critiques jokes on a given topic",

    "settings": {
        "default_model": "gpt-4o-mini",
        "cache_enabled": True,
        "max_retries": 2
    },

    "inputs": [
        {
            "name": "topic",
            "type": "string",
            "description": "Topic for the joke",
            "required": True
        }
    ],

    "nodes": [
        {
            "id": "joke_generator",
            "role": "Generate a joke about a topic",
            "type": "llm",
            "model": "gpt-4o-mini",
            "temperature": 0.9,
            "prompt_template": os.path.join(FRAMEWORK_DIR, "prompts", "joke_prompt.txt"),
            "output": {
                "type": "pydantic",
                "schema": "framework.schemas.joke.JokeOutput"
            }
        },
        {
            "id": "joke_critic",
            "role": "Critique the joke",
            "type": "llm",
            "model": "gpt-4o-mini",
            "temperature": 0.6,
            "prompt_template": os.path.join(FRAMEWORK_DIR, "prompts", "critic_prompt.txt"),
            "output": {
                "type": "raw"
            }
        },
        {
            "id": "joke_logger",
            "role": "Log the joke and critique",
            "type": "tool",
            "tool": "framework.tools.file_logger.log_output",
            "output": {
                "type": "raw"
            }
        }
    ],

    "output": {
        "joke": "{{ joke_generator }}",
        "critique": "{{ joke_critic }}",
        "log_status": "{{ joke_logger }}"
    }
}

# Save the configuration to a YAML file


def save_config():
    config_dir = os.path.join(FRAMEWORK_DIR, "examples", "configs")
    os.makedirs(config_dir, exist_ok=True)

    config_path = os.path.join(config_dir, "joke_pipeline.yaml")
    with open(config_path, 'w') as f:
        yaml.dump(joke_pipeline_config, f, default_flow_style=False)

    return config_path

# Function to run the joke pipeline


def run_joke_pipeline(topic: str, thread_id: str = "default"):
    from framework.core.config import ConfigLoader
    from framework.core.engine import PipelineEngine

    # Save the config to a file
    config_path = save_config()

    # Load the configuration
    config = ConfigLoader.load_config(config_path)

    # Create the pipeline engine
    engine = PipelineEngine(config)

    # Run the pipeline
    result = engine.run(
        {"user_input": f"Tell me a joke about {topic}", "topic": topic}, thread_id)

    return result

# Function to stream the joke pipeline execution


def stream_joke_pipeline(topic: str, thread_id: str = "default"):
    from framework.core.config import ConfigLoader
    from framework.core.engine import PipelineEngine

    # Save the config to a file
    config_path = save_config()

    # Load the configuration
    config = ConfigLoader.load_config(config_path)

    # Create the pipeline engine
    engine = PipelineEngine(config)

    # Stream the pipeline execution
    for event in engine.stream({"user_input": f"Tell me a joke about {topic}", "topic": topic}, thread_id):
        yield event
