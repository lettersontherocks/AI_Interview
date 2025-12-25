from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime


class Message(BaseModel):
    """Chat message model"""
    role: Literal["user", "assistant"] = Field(..., description="Role of the message sender")
    content: str = Field(..., description="Content of the message")


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    messages: List[Message] = Field(..., description="List of conversation messages")
    model: Optional[str] = Field(None, description="Claude model to use (defaults to config)")
    max_tokens: Optional[int] = Field(4096, description="Maximum tokens in response", ge=1, le=8192)
    temperature: Optional[float] = Field(1.0, description="Sampling temperature", ge=0.0, le=1.0)
    top_p: Optional[float] = Field(None, description="Nucleus sampling parameter", ge=0.0, le=1.0)
    top_k: Optional[int] = Field(None, description="Top-k sampling parameter", ge=0)
    stream: Optional[bool] = Field(False, description="Enable streaming response")
    system: Optional[str] = Field(None, description="System prompt")

    class Config:
        json_schema_extra = {
            "example": {
                "messages": [
                    {"role": "user", "content": "Hello! How are you?"}
                ],
                "max_tokens": 1024,
                "temperature": 0.7
            }
        }


class Usage(BaseModel):
    """Token usage information"""
    input_tokens: int
    output_tokens: int
    total_tokens: int


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    id: str = Field(..., description="Unique response identifier")
    model: str = Field(..., description="Model used for generation")
    content: str = Field(..., description="Generated response content")
    role: str = Field(default="assistant", description="Role of the responder")
    stop_reason: Optional[str] = Field(None, description="Reason for stopping generation")
    usage: Optional[Usage] = Field(None, description="Token usage statistics")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class CompletionRequest(BaseModel):
    """Request model for text completion endpoint"""
    prompt: str = Field(..., description="Text prompt for completion")
    model: Optional[str] = Field(None, description="Claude model to use")
    max_tokens: Optional[int] = Field(2048, description="Maximum tokens in response", ge=1, le=8192)
    temperature: Optional[float] = Field(1.0, description="Sampling temperature", ge=0.0, le=1.0)
    top_p: Optional[float] = Field(None, description="Nucleus sampling parameter")
    top_k: Optional[int] = Field(None, description="Top-k sampling parameter")
    system: Optional[str] = Field(None, description="System prompt")

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Write a short poem about the ocean",
                "max_tokens": 512,
                "temperature": 0.8
            }
        }


class CompletionResponse(BaseModel):
    """Response model for completion endpoint"""
    id: str = Field(..., description="Unique response identifier")
    model: str = Field(..., description="Model used for generation")
    completion: str = Field(..., description="Generated completion text")
    stop_reason: Optional[str] = Field(None, description="Reason for stopping")
    usage: Optional[Usage] = Field(None, description="Token usage statistics")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(default="healthy", description="Service health status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")
    version: str = Field(..., description="API version")


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
