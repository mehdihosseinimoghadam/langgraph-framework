from pydantic import BaseModel, Field
from typing import Optional, List
from .base import BaseOutput


class JokeOutput(BaseOutput):
    """Schema for joke output."""
    setup: str = Field(..., description="The setup part of the joke")
    punchline: str = Field(..., description="The punchline of the joke")
    humor_rating: float = Field(
        ..., description="A rating of how funny the joke is (0-10)", ge=0, le=10)
    tags: List[str] = Field(default_factory=list,
                            description="Tags categorizing the joke")

    class Config:
        schema_extra = {
            "example": {
                "setup": "Why don't scientists trust atoms?",
                "punchline": "Because they make up everything!",
                "humor_rating": 7.5,
                "tags": ["science", "pun"]
            }
        }
