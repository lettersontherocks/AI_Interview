from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from contextlib import asynccontextmanager
import logging
import uuid
from datetime import datetime
from anthropic import APIError

from config import get_settings, Settings
from models import (
    ChatRequest,
    ChatResponse,
    CompletionRequest,
    CompletionResponse,
    HealthResponse,
    ErrorResponse,
    Usage,
)
from claude_service import get_claude_service, ClaudeService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    logger.info("Starting Claude API Service Platform...")
    yield
    logger.info("Shutting down Claude API Service Platform...")


# Initialize FastAPI app
settings = get_settings()
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="RESTful API service platform for Anthropic Claude",
    lifespan=lifespan,
)

# Configure CORS
origins = settings.allow_origins.split(",") if settings.allow_origins != "*" else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=settings.allow_credentials,
    allow_methods=settings.allow_methods.split(",") if settings.allow_methods != "*" else ["*"],
    allow_headers=settings.allow_headers.split(",") if settings.allow_headers != "*" else ["*"],
)


@app.exception_handler(APIError)
async def anthropic_exception_handler(request, exc: APIError):
    """Handle Anthropic API errors"""
    logger.error(f"Anthropic API error: {str(exc)}")
    return JSONResponse(
        status_code=exc.status_code if hasattr(exc, "status_code") else 500,
        content=ErrorResponse(
            error="AnthropicAPIError",
            message=str(exc),
            details={"type": type(exc).__name__},
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="InternalServerError",
            message="An unexpected error occurred",
            details={"type": type(exc).__name__},
        ).model_dump(),
    )


@app.get("/", response_model=HealthResponse)
async def root(settings: Settings = Depends(get_settings)):
    """Root endpoint - health check"""
    return HealthResponse(
        status="healthy",
        version=settings.api_version,
    )


@app.get("/health", response_model=HealthResponse)
async def health_check(settings: Settings = Depends(get_settings)):
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version=settings.api_version,
    )


@app.get("/models")
async def list_models(claude_service: ClaudeService = Depends(get_claude_service)):
    """List available Claude models"""
    models = await claude_service.get_available_models()
    return {
        "models": models,
        "default": get_settings().default_claude_model,
    }


@app.post("/v1/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    claude_service: ClaudeService = Depends(get_claude_service),
):
    """
    Chat with Claude using conversational messages

    Send a list of messages and receive a response from Claude.
    Supports system prompts, temperature control, and other parameters.
    """
    try:
        if request.stream:
            # Return streaming response
            async def generate():
                async for chunk in claude_service.chat_stream(
                    messages=request.messages,
                    model=request.model,
                    max_tokens=request.max_tokens,
                    temperature=request.temperature,
                    top_p=request.top_p,
                    top_k=request.top_k,
                    system=request.system,
                ):
                    yield chunk

            return StreamingResponse(generate(), media_type="text/plain")

        # Non-streaming response
        response = await claude_service.chat(
            messages=request.messages,
            model=request.model,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p,
            top_k=request.top_k,
            system=request.system,
        )

        # Extract content from response
        content = response.content[0].text if response.content else ""

        # Build usage stats
        usage = Usage(
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            total_tokens=response.usage.input_tokens + response.usage.output_tokens,
        )

        return ChatResponse(
            id=response.id,
            model=response.model,
            content=content,
            role=response.role,
            stop_reason=response.stop_reason,
            usage=usage,
        )

    except APIError as e:
        logger.error(f"Claude API error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/v1/completions", response_model=CompletionResponse)
async def completions(
    request: CompletionRequest,
    claude_service: ClaudeService = Depends(get_claude_service),
):
    """
    Generate text completions from a prompt

    Provide a text prompt and receive a completion from Claude.
    This is a simpler interface than chat for single-turn interactions.
    """
    try:
        response = await claude_service.complete(
            prompt=request.prompt,
            model=request.model,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p,
            top_k=request.top_k,
            system=request.system,
        )

        # Extract content from response
        completion = response.content[0].text if response.content else ""

        # Build usage stats
        usage = Usage(
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            total_tokens=response.usage.input_tokens + response.usage.output_tokens,
        )

        return CompletionResponse(
            id=response.id,
            model=response.model,
            completion=completion,
            stop_reason=response.stop_reason,
            usage=usage,
        )

    except APIError as e:
        logger.error(f"Claude API error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Error in completions endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level="info",
    )
