from fastapi import APIRouter, HTTPException
import logging

from app.schemas.llm import LLMQueryRequest, LLMQueryResponse
from app.services.llm.deepseek import deepseek_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/llm", tags=["LLM"])


@router.post("/query", response_model=LLMQueryResponse)
async def query_llm(request: LLMQueryRequest) -> LLMQueryResponse:
    """
    Send query to LLM and get response

    - **text**: User query text (string input)

    Returns text response from LLM
    """
    try:
        logger.info(f"Processing LLM query: {request.text[:50]}...")

        # Query DeepSeek API
        response_text = await deepseek_service.query(
            text=request.text,
            system_prompt="Ты дружелюбный голосовой ассистент для умного зеркала. Отвечай кратко и по делу.",
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
