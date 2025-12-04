from fastapi import APIRouter, HTTPException, Query
import logging

from app.schemas.music import MusicSearchResponse, TrackStreamResponse
from app.services.music.yandex import yandex_music_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/music", tags=["Music"])


@router.get("/search", response_model=MusicSearchResponse)
async def search_music(
    q: str = Query(..., min_length=1, max_length=100, description="Search query"),
) -> MusicSearchResponse:
    """
    Search for music tracks

    - **q**: Search query string (artist, title, album, etc.)

    Returns list of found tracks
    """
    try:
        logger.info(f"Searching music for query: {q}")

        tracks = await yandex_music_service.search_tracks(query=q, limit=10)

        logger.info(f"Found {len(tracks)} tracks")

        return MusicSearchResponse(tracks=tracks, total=len(tracks))

    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        raise HTTPException(status_code=500, detail="Music service not configured properly")
    except Exception as e:
        logger.error(f"Error searching music: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to search music: {str(e)}")


@router.get("/track/{track_id}/stream", response_model=TrackStreamResponse)
async def get_track_stream(track_id: str) -> TrackStreamResponse:
    """
    Get direct stream/download URL for a track

    - **track_id**: Track ID from search results

    Returns direct download URL that client can use to stream/download the track
    """
    try:
        logger.info(f"Getting stream URL for track: {track_id}")

        stream_url = await yandex_music_service.get_track_download_url(track_id=track_id)

        logger.info(f"Stream URL obtained for track: {track_id}")

        return TrackStreamResponse(stream_url=stream_url)

    except ValueError as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting stream URL: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get stream URL: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint for music service"""
    return {"status": "ok", "service": "music"}
