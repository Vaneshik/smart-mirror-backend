from pydantic import BaseModel, Field


class LLMQueryRequest(BaseModel):
    """Request schema for LLM query"""
    text: str = Field(..., min_length=1, max_length=2000, description="User query text")


class LLMQueryResponse(BaseModel):
    """Response schema for LLM query"""
    response: str = Field(..., description="LLM generated response")
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "Здравствуйте! Хорошо, спасибо!"
            }
        }

