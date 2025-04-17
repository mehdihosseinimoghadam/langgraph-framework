from pydantic import BaseModel, Field
from typing import List, Optional
from .base import BaseOutput


class NovelTopics(BaseOutput):
    """Schema for novel topics."""
    topic1: str = Field(..., description="First novel topic")
    topic2: str = Field(..., description="Second novel topic")
    genres: List[str] = Field(..., description="List of genres for the novels")

    class Config:
        schema_extra = {
            "example": {
                "topic1": "A time-traveling archaeologist discovers ancient technology",
                "topic2": "A chef who can taste emotions in food",
                "genres": ["science fiction", "drama", "adventure"]
            }
        }


class NovelOutline(BaseOutput):
    """Schema for a novel outline."""
    title: str = Field(..., description="Title of the novel")
    protagonist: str = Field(..., description="Main character of the novel")
    setting: str = Field(..., description="Setting of the novel")
    plot_summary: str = Field(..., description="Brief summary of the plot")
    themes: List[str] = Field(..., description="Main themes of the novel")

    class Config:
        schema_extra = {
            "example": {
                "title": "Echoes of Tomorrow",
                "protagonist": "Dr. Elena Reyes",
                "setting": "Split between modern day and ancient Egypt",
                "plot_summary": "An archaeologist discovers a device that allows her to communicate with the past, leading to unexpected consequences.",
                "themes": ["time", "responsibility", "cultural preservation"]
            }
        }


class CombinedNovel(BaseOutput):
    """Schema for a combined novel."""
    title: str = Field(..., description="Title of the combined novel")
    protagonist: str = Field(...,
                             description="Main character of the combined novel")
    supporting_characters: List[str] = Field(...,
                                             description="Supporting characters")
    setting: str = Field(..., description="Setting of the combined novel")
    plot_summary: str = Field(..., description="Summary of the combined plot")
    themes: List[str] = Field(..., description="Themes of the combined novel")
    potential_conflicts: List[str] = Field(...,
                                           description="Potential conflicts in the story")

    class Config:
        schema_extra = {
            "example": {
                "title": "Flavors of Time",
                "protagonist": "Dr. Elena Reyes",
                "supporting_characters": ["Chef Marco Bellini", "Professor Zhang", "Nefertiti"],
                "setting": "A culinary institute with a secret archaeological lab in the basement",
                "plot_summary": "An archaeologist and a chef discover that ancient recipes can trigger time travel, leading them on a journey through history's kitchens.",
                "themes": ["time", "cultural exchange", "sensory experience", "preservation"],
                "potential_conflicts": ["Rival archaeologist wants the recipes for profit", "Time paradoxes threaten to erase culinary history"]
            }
        }
