from yandex_music import ClientAsync
from typing import List, Optional
import logging

from app.core.config import settings
from app.schemas.music import TrackInfo

logger = logging.getLogger(__name__)


class YandexMusicService:
    """Service for interacting with Yandex Music API"""
    
    def __init__(self):
        self.token = settings.yandex_music_token
        self._client: Optional[ClientAsync] = None
        
    async def _get_client(self) -> ClientAsync:
        """Get or create Yandex Music client"""
        if not self.token:
            raise ValueError("Yandex Music token not configured")
            
        if self._client is None:
            self._client = await ClientAsync(self.token).init()
        return self._client
    
    async def search_tracks(self, query: str, limit: int = 10) -> List[TrackInfo]:
        """
        Search for tracks by query
        
        Args:
            query: Search query string
            limit: Maximum number of results (default: 10)
            
        Returns:
            List[TrackInfo]: List of found tracks
        """
        try:
            client = await self._get_client()
            
            # Perform search
            search_result = await client.search(query, type_="track")
            
            if not search_result or not search_result.tracks:
                logger.info(f"No tracks found for query: {query}")
                return []
            
            tracks = []
            for track in search_result.tracks.results[:limit]:
                # Extract track information
                track_info = TrackInfo(
                    id=str(track.id),
                    title=track.title,
                    artist=", ".join([artist.name for artist in track.artists]) if track.artists else "Unknown",
                    album=track.albums[0].title if track.albums else None,
                    duration_ms=track.duration_ms,
                    cover_url=f"https://{track.cover_uri.replace('%%', '400x400')}" if track.cover_uri else None
                )
                tracks.append(track_info)
            
            logger.info(f"Found {len(tracks)} tracks for query: {query}")
            return tracks
            
        except Exception as e:
            logger.error(f"Error searching tracks: {str(e)}")
            raise
    
    async def get_track_download_url(self, track_id: str) -> str:
        """
        Get direct download/stream URL for a track
        
        Args:
            track_id: Track ID
            
        Returns:
            str: Direct download URL
        """
        try:
            client = await self._get_client()
            
            # Get track
            track = await client.tracks([track_id])
            if not track or len(track) == 0:
                raise ValueError(f"Track {track_id} not found")
            
            # Get download info
            download_info = await track[0].get_download_info_async()
            
            if not download_info:
                raise ValueError(f"No download info available for track {track_id}")
            
            # Get highest quality download
            best_quality = max(download_info, key=lambda x: x.bitrate_in_kbps)
            
            # Get direct link
            direct_link = await best_quality.get_direct_link_async()
            
            logger.info(f"Got stream URL for track {track_id}")
            return direct_link
            
        except Exception as e:
            logger.error(f"Error getting track download URL: {str(e)}")
            raise
    
    async def close(self):
        """Close client connection"""
        if self._client:
            # Yandex Music client doesn't have explicit close method
            self._client = None


# Singleton instance
yandex_music_service = YandexMusicService()

