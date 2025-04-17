import os
from typing import Dict, Any, Optional
from langfuse.callback import CallbackHandler


class LangfuseTracer:
    """Integration with Langfuse for tracing and monitoring LangGraph pipelines."""

    def __init__(
        self,
        public_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        host: Optional[str] = None,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None
    ):
        """Initialize the Langfuse tracer.

        Args:
            public_key: Langfuse public key. Defaults to LANGFUSE_PUBLIC_KEY env var.
            secret_key: Langfuse secret key. Defaults to LANGFUSE_SECRET_KEY env var.
            host: Langfuse host. Defaults to LANGFUSE_HOST env var or https://cloud.langfuse.com.
            session_id: Optional session ID for grouping related traces.
            user_id: Optional user ID for attributing traces to specific users.
        """
        # Use provided keys or get from environment
        self.public_key = public_key or os.getenv("LANGFUSE_PUBLIC_KEY")
        self.secret_key = secret_key or os.getenv("LANGFUSE_SECRET_KEY")
        self.host = host or os.getenv(
            "LANGFUSE_HOST", "https://cloud.langfuse.com")

        # Validate keys
        if not self.public_key or not self.secret_key:
            print("Warning: Langfuse keys not provided. Tracing will be disabled.")
            self.enabled = False
        else:
            self.enabled = True

        # Create callback handler
        self.handler = CallbackHandler(
            session_id=session_id,
            user_id=user_id
        ) if self.enabled else None

    def get_callback_handler(self) -> Optional[CallbackHandler]:
        """Get the Langfuse callback handler for LangChain."""
        return self.handler

    def add_score(self, trace_id: str, name: str, value: float, comment: Optional[str] = None) -> None:
        """Add a score to a trace.

        Args:
            trace_id: The ID of the trace to score.
            name: The name of the score.
            value: The score value (typically between 0 and 1).
            comment: Optional comment explaining the score.
        """
        if not self.enabled:
            print("Warning: Langfuse tracing is disabled. Score not added.")
            return

        from langfuse import Langfuse

        langfuse = Langfuse()
        langfuse.score(
            trace_id=trace_id,
            name=name,
            value=value,
            comment=comment
        )
