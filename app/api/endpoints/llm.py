import json
import logging
import re
from typing import Optional, Union

from fastapi import APIRouter, HTTPException

from app.schemas.llm import LLMQueryRequest, LLMQueryResponse
from app.schemas.music import TrackStreamResponse
from app.services.llm.deepseek import deepseek_service
from app.services.music.yandex import yandex_music_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/llm", tags=["LLM"])

MUSIC_DETECTION_PROMPT = (
    "Ты анализируешь команды пользователя умного зеркала. Если он просит включить, проиграть,"
    " или воспроизвести музыку, песню, исполнителя или плейлист, ответь строго JSON без лишнего"
    " текста в формате {\"is_music_command\": true, \"query\": \"название\"}."
    " Если запрос не о музыке, верни {\"is_music_command\": false, \"query\": \"\"}."
    " Query должен содержать только исполнителя/трек без служебных слов."
)


def _parse_music_detection(raw_response: str) -> Optional[str]:
    """Parse LLM JSON response returned by the detection prompt."""
    try:
        data = json.loads(raw_response)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw_response, re.DOTALL)
        if not match:
            logger.warning("Unable to parse music detection response: %s", raw_response)
            return None
        try:
            data = json.loads(match.group(0))
        except json.JSONDecodeError:
            logger.warning("Unable to parse extracted detection JSON: %s", match.group(0))
            return None
    is_music = bool(data.get("is_music_command"))
    query = (data.get("query") or "").strip()
    if is_music and query:
        return query
    return None


async def _detect_music_command(text: str) -> Optional[str]:
    """Delegate intent detection to LLM."""
    detection_response = await deepseek_service.query(
        text=text,
        system_prompt=MUSIC_DETECTION_PROMPT,
    )
    return _parse_music_detection(detection_response)


async def _handle_music_command(query: str) -> TrackStreamResponse:
    """Search track and return direct stream URL for the first result."""
    try:
        tracks = await yandex_music_service.search_tracks(query=query, limit=1)
    except ValueError as e:
        logger.error(f"Music service configuration error: {str(e)}")
        raise HTTPException(status_code=500, detail="Music service not configured properly")
    except Exception as e:
        logger.error(f"Error searching music: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to search music: {str(e)}")

    if not tracks:
        logger.info(f"No tracks found for query: {query}")
        raise HTTPException(status_code=404, detail=f"No tracks found for query '{query}'")

    track_id = tracks[0].id
    try:
        stream_url = await yandex_music_service.get_track_download_url(track_id=track_id)
        return TrackStreamResponse(stream_url=stream_url)
    except ValueError as e:
        logger.error(f"Track unavailable: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting stream URL: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get stream URL: {str(e)}")


@router.post("/query", response_model=Union[LLMQueryResponse, TrackStreamResponse])
async def query_llm(request: LLMQueryRequest) -> Union[LLMQueryResponse, TrackStreamResponse]:
    """
    Send query to LLM and get response
    
    - **text**: User query text (string input)
    
    Returns text response from LLM
    """
    try:
        # First check if user asks to play music using LLM intent detection
        music_query = await _detect_music_command(request.text)
        if music_query:
            logger.info(f"Detected music command for query: {music_query}")
            return await _handle_music_command(music_query)

        logger.info(f"Processing LLM query: {request.text[:50]}...")
        
        # Query DeepSeek API for regular text requests
        response_text = await deepseek_service.query(
            text=request.text,
            system_prompt="Ты дружелюбный голосовой ассистент для умного зеркала. Отвечай кратко и по делу."
        )
        
        logger.info(f"LLM response received: {response_text[:50]}...")
        
        return LLMQueryResponse(response=response_text)
        
    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        raise HTTPException(status_code=500, detail="LLM service not configured properly")
    except Exception as e:
        logger.error(f"Error processing LLM query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process LLM query: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint for LLM service"""
    return {"status": "ok", "service": "llm"}
