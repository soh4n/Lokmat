"""
LokMat API — Assistant chat router.

POST /chat        — Full response (JSON)
POST /chat/stream — Streaming response (SSE / EventSource)

All endpoints require a valid Bearer token (per GEMINI.md security rules).

Implements the context pipeline from GEMINI.md:
1. Intent Classification (Gemini Flash)
2. Prompt Construction (system prompt + context)
3. Model Routing (Flash default → Pro for complex)
4. Gemini Inference (streaming for chat, batch for fallback)
5. Response Validation (safety check)
6. Structured Output (typed response)
"""

import logging
from uuid import uuid4

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from api.schemas.schemas import ChatRequest, ChatResponse, IntentType
from api.services.gemini_service import (
    classify_intent,
    generate_chat_response,
    generate_chat_stream,
)
from api.utils.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Assistant"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user_id: str = Depends(get_current_user),
) -> ChatResponse:
    """
    Process a chat message through the election AI assistant pipeline.

    Requires a valid Bearer token. Row-level data is scoped to the
    authenticated user’s session.

    Pipeline:
    1. Classify intent (query/action/clarify/out_of_scope)
    2. Generate response with conversation context
    3. Return structured response with suggestions

    Args:
        request: ChatRequest with message, session_id, and history.
        user_id: Authenticated user identifier from Bearer token.

    Returns:
        ChatResponse with AI response, intent, and suggestions.
    """
    session_id = request.session_id or str(uuid4())

    try:
        # Step 1: Intent Classification
        intent = await classify_intent(request.message)
        logger.info(
            "Intent classified",
            extra={"intent": intent, "session_id": session_id, "user_id": user_id},
        )

        # Step 2: Handle out-of-scope
        if intent == "out_of_scope":
            return ChatResponse(
                message=(
                    "I'm specialized in election guidance. Please ask about voting, candidates,"
                    " booth locations, or the electoral process. I'm here to help with your voting journey."
                ),
                intent=IntentType.OUT_OF_SCOPE,
                session_id=session_id,
                suggestions=[
                    "How do I find my polling booth?",
                    "What documents do I need to vote?",
                    "Tell me about NOTA",
                ],
            )

        # Step 3: Generate response with context (model routed internally)
        history = [{"role": m.role, "content": m.content} for m in request.history]
        response_text, suggestions, model_used = await generate_chat_response(
            request.message,
            history,
        )

        logger.info(
            "Chat response generated",
            extra={
                "session_id": session_id,
                "user_id": user_id,
                "intent": intent,
                "response_length": len(response_text),
                "model": model_used,
            },
        )

        return ChatResponse(
            message=response_text,
            intent=IntentType(intent),
            session_id=session_id,
            suggestions=suggestions,
            model_used=model_used,
        )

    except Exception as e:
        logger.error(
            "Chat generation failed",
            extra={"error": str(e), "session_id": session_id, "user_id": user_id},
        )
        # Graceful fallback per GEMINI.md
        return ChatResponse(
            message=(
                "I apologize, but I'm experiencing technical difficulties right now."
                " Please try again in a moment, or call the Election Helpline at 1950 for immediate assistance."
            ),
            intent=IntentType.QUERY,
            session_id=session_id,
            suggestions=[
                "Try asking again",
                "Call 1950 helpline",
            ],
            is_fallback=True,
        )


@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    user_id: str = Depends(get_current_user),
) -> StreamingResponse:
    """
    Streaming chat endpoint using Server-Sent Events (SSE).

    Requires a valid Bearer token. First token appears within 500ms
    per GEMINI.md UX requirements.

    SSE events emitted:
        {type: "chunk", text: "...", model: "gemini-2.5-flash"}
        {type: "done", suggestions: [...], model: "gemini-2.5-flash"}
        {type: "error", message: "..."}

    Args:
        request: ChatRequest with message, session_id, and history.
        user_id: Authenticated user identifier from Bearer token.

    Returns:
        StreamingResponse with text/event-stream content type.
    """
    session_id = request.session_id or str(uuid4())
    history = [{"role": m.role, "content": m.content} for m in request.history]

    logger.info(
        "Streaming chat request",
        extra={"session_id": session_id, "user_id": user_id, "msg_len": len(request.message)},
    )

    return StreamingResponse(
        generate_chat_stream(request.message, history),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",   # Disable nginx buffering
            "Connection": "keep-alive",
        },
    )
