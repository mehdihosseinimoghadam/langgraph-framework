from framework.examples.novel_pipeline import run_novel_pipeline, stream_novel_pipeline
import os
import sys
import json
from pydantic import BaseModel

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Helper function to convert Pydantic models to dictionaries


def pydantic_to_dict(obj):
    if isinstance(obj, BaseModel):
        return obj.dict()
    raise TypeError(
        f"Object of type {type(obj).__name__} is not JSON serializable")


def main():
    """Run the novel pipeline example."""
    print("LangGraph Agential Framework - Novel Pipeline Example")
    print("=" * 60)

    print("Generating novel topics, creating outlines, and combining them...")
    print("-" * 60)

    # Run the novel pipeline
    result = run_novel_pipeline()

    # Print the topics
    topics = result.get("topic_generator", {})
    if isinstance(topics, BaseModel):
        # Convert Pydantic model to dict
        topics_dict = topics.dict()
        print("NOVEL TOPICS:")
        print(f"Topic 1: {topics_dict['topic1']}")
        print(f"Topic 2: {topics_dict['topic2']}")
        print(f"Genres: {', '.join(topics_dict['genres'])}")
    else:
        print("Topics:", topics)

    print("-" * 60)

    # Print the novel outlines
    outlines = result.get("novel_creator", {})
    if isinstance(outlines, dict) and "novel1" in outlines and "novel2" in outlines:
        print("NOVEL OUTLINES:")

        print("\nNOVEL 1:")
        novel1 = outlines["novel1"]
        print(f"Title: {novel1['title']}")
        print(f"Protagonist: {novel1['protagonist']}")
        print(f"Setting: {novel1['setting']}")
        print(f"Plot: {novel1['plot_summary']}")
        print(f"Themes: {', '.join(novel1['themes'])}")

        print("\nNOVEL 2:")
        novel2 = outlines["novel2"]
        print(f"Title: {novel2['title']}")
        print(f"Protagonist: {novel2['protagonist']}")
        print(f"Setting: {novel2['setting']}")
        print(f"Plot: {novel2['plot_summary']}")
        print(f"Themes: {', '.join(novel2['themes'])}")
    else:
        print("Outlines:", json.dumps(outlines, indent=2))

    print("-" * 60)

    # Print the combined novel
    combined = result.get("novel_combiner", {})
    if isinstance(combined, BaseModel):
        # Convert Pydantic model to dict
        combined_dict = combined.dict()
        print("COMBINED NOVEL:")
        print(f"Title: {combined_dict['title']}")
        print(f"Protagonist: {combined_dict['protagonist']}")
        print(
            f"Supporting Characters: {', '.join(combined_dict['supporting_characters'])}")
        print(f"Setting: {combined_dict['setting']}")
        print(f"Plot: {combined_dict['plot_summary']}")
        print(f"Themes: {', '.join(combined_dict['themes'])}")
        print(f"Potential Conflicts:")
        for i, conflict in enumerate(combined_dict['potential_conflicts'], 1):
            print(f"  {i}. {conflict}")
    else:
        # Use custom JSON encoder for Pydantic models
        print("Combined Novel:", json.dumps(
            combined, indent=2, default=pydantic_to_dict))


if __name__ == "__main__":
    main()
