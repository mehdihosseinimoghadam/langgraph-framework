import os
import yaml
from typing import Dict, Any
from framework.integrations.langfuse_integration import LangfuseTracer

# Get the absolute path to the framework directory
FRAMEWORK_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Define the pipeline configuration
novel_pipeline_config = {
    "name": "Novel Generator Pipeline",
    "version": "1.0",
    "description": "Generates novel topics, creates outlines, and combines them",

    "settings": {
        "default_model": "gpt-4o-mini",
        "cache_enabled": True,
        "max_retries": 2
    },

    "nodes": [
        {
            "id": "topic_generator",
            "role": "Generate novel topics",
            "type": "llm",
            "model": "gpt-4o-mini",
            "temperature": 0.9,
            "prompt_template": os.path.join(FRAMEWORK_DIR, "prompts", "topic_generator_prompt.txt"),
            "output": {
                "type": "pydantic",
                "schema": "framework.schemas.novel.NovelTopics"
            }
        },
        {
            "id": "novel_creator",
            "role": "Create novel outlines",
            "type": "llm",
            "model": "gpt-4o-mini",
            "temperature": 0.8,
            "prompt_template": os.path.join(FRAMEWORK_DIR, "prompts", "novel_creator_prompt.txt"),
            "output": {
                "type": "json"
            }
        },
        {
            "id": "novel_combiner",
            "role": "Combine the novels",
            "type": "llm",
            "model": "gpt-4o-mini",
            "temperature": 0.7,
            "prompt_template": os.path.join(FRAMEWORK_DIR, "prompts", "novel_combiner_prompt.txt"),
            "output": {
                "type": "pydantic",
                "schema": "framework.schemas.novel.CombinedNovel"
            }
        }
    ],

    "output": {
        "topics": "{{ topic_generator }}",
        "outlines": "{{ novel_creator }}",
        "combined_novel": "{{ novel_combiner }}"
    }
}

# Save the configuration to a YAML file


def save_config():
    config_dir = os.path.join(FRAMEWORK_DIR, "examples", "configs")
    os.makedirs(config_dir, exist_ok=True)

    config_path = os.path.join(config_dir, "novel_pipeline.yaml")
    with open(config_path, 'w') as f:
        yaml.dump(novel_pipeline_config, f, default_flow_style=False)

    return config_path

# Function to run the novel pipeline


def run_novel_pipeline(thread_id: str = "default"):
    from framework.core.config import ConfigLoader
    from framework.core.engine import PipelineEngine

    # Save the config to a file
    config_path = save_config()

    # Load the configuration
    config = ConfigLoader.load_config(config_path)

    # Create the pipeline engine
    engine = PipelineEngine(config)

    # Initialize Langfuse tracer
    tracer = LangfuseTracer(session_id="novel_pipeline",
                            user_id=f"user_{thread_id}")
    langfuse_handler = tracer.get_callback_handler()

    # Run the pipeline with Langfuse tracing
    result = engine.run(
        {"user_input": "Generate a creative novel concept"},
        thread_id=thread_id,
        callbacks=[langfuse_handler] if langfuse_handler else None
    )

    return result

# Function to stream the novel pipeline execution


def stream_novel_pipeline(thread_id: str = "default"):
    from framework.core.config import ConfigLoader
    from framework.core.engine import PipelineEngine

    # Save the config to a file
    config_path = save_config()

    # Load the configuration
    config = ConfigLoader.load_config(config_path)

    # Create the pipeline engine
    engine = PipelineEngine(config)

    # Initialize Langfuse tracer
    tracer = LangfuseTracer(session_id="novel_pipeline",
                            user_id=f"user_{thread_id}")
    langfuse_handler = tracer.get_callback_handler()

    # Stream the pipeline execution with Langfuse tracing
    for event in engine.stream(
        {"user_input": "Generate a creative novel concept"},
        thread_id=thread_id,
        callbacks=[langfuse_handler] if langfuse_handler else None
    ):
        yield event
