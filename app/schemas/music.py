from pydantic import BaseModel, Field
from typing import List, Optional


class TrackInfo(BaseModel):
    """Track information schema"""
    id: str = Field(..., description="Track ID")
    title: str = Field(..., description="Track title")
    artist: str = Field(..., description="Artist name")
    album: Optional[str] = Field(None, description="Album name")
    duration_ms: Optional[int] = Field(None, description="Track duration in milliseconds")
    cover_url: Optional[str] = Field(None, description="Album cover URL")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123456",
                "title": "Enter Sandman",
                "artist": "Metallica",
                "album": "Metallica",
                "duration_ms": 331000,
                "cover_url": "https://avatars.yandex.net/..."
            }
        }


class MusicSearchResponse(BaseModel):
    """Music search response schema"""
    tracks: List[TrackInfo] = Field(default_factory=list, description="List of found tracks")
    total: int = Field(0, description="Total number of results")
    

class TrackStreamResponse(BaseModel):
    """Track stream URL response"""
    stream_url: str = Field(..., description="Direct download/stream URL for the track")
    
    class Config:
        json_schema_extra = {
            "example": {
                "stream_url": "https://storage.mds.yandex.net/..."
            }
        }

