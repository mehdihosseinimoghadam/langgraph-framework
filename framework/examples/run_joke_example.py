from framework.examples.joke_pipeline import run_joke_pipeline, stream_joke_pipeline
import os
import sys
import json

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main():
    """Run the joke pipeline example."""
    print("LangGraph Agential Framework - Joke Pipeline Example")
    print("=" * 50)

    # Get the topic from command line arguments or use a default
    topic = sys.argv[1] if len(sys.argv) > 1 else "programming"

    print(f"Generating a joke about: {topic}")
    print("-" * 50)

    # Run the joke pipeline
    result = run_joke_pipeline(topic)

    # Print the joke
    joke = result.get("joke_generator", {})
    if isinstance(joke, dict) and "setup" in joke and "punchline" in joke:
        print("Joke:")
        print(f"Setup: {joke['setup']}")
        print(f"Punchline: {joke['punchline']}")
        print(f"Humor Rating: {joke['humor_rating']}/10")
        print(f"Tags: {', '.join(joke['tags'])}")
    else:
        print("Joke:", joke)

    print("-" * 50)

    # Print the critique
    critique = result.get("joke_critic", "")
    print("Critique:")
    print(critique)

    print("-" * 50)

    # Print the log status
    log_status = result.get("joke_logger", {})
    print("Log Status:")
    print(json.dumps(log_status, indent=2))


if __name__ == "__main__":
    main()
