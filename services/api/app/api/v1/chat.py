import json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sse_starlette.sse import EventSourceResponse
from app.db.session import get_db
from app.models import User, AgentRun, ToolCall
from app.schemas.common import ChatRequest
from app.api.deps import get_current_user
from app.services.ai import get_ai_provider
from app.services.ai.tools import TOOL_DEFINITIONS, execute_tool
from app.services.audit import write_audit

router = APIRouter()

SYSTEM_PROMPT = (
    "Eres JARVIS Engineering, asistente de ingeniería MEP/eléctrico/hidráulico/energía. "
    "Usa herramientas de cálculo determinísticas cuando haya números. "
    "Nunca inventes resultados de cálculo — llama a las tools. "
    "Responde en español técnico claro. Marca datos DEMO cuando aplique."
)


@router.post("")
async def chat(
    body: ChatRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    provider = get_ai_provider()
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend([m.model_dump() for m in body.messages])

    run = AgentRun(
        org_id=user.org_id,
        user_id=user.id,
        provider=provider.name,
        model="grok" if provider.is_available() else "none",
        status="running",
        prompt=body.messages[-1].content if body.messages else "",
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    tools = TOOL_DEFINITIONS if body.use_tools else None
    result = await provider.chat(messages, tools=tools)

    tool_results = []
    for tc in result.get("tool_calls") or []:
        args = tc.get("arguments") or "{}"
        try:
            parsed = json.loads(args) if isinstance(args, str) else args
        except json.JSONDecodeError:
            parsed = {}
        out = execute_tool(tc["name"], parsed, db)
        tool_results.append({"tool": tc["name"], "arguments": parsed, "result": out})
        db.add(
            ToolCall(
                agent_run_id=run.id,
                tool_name=tc["name"],
                arguments=parsed,
                result=out,
                status="ok" if "error" not in out else "error",
            )
        )
        messages.append(
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": tc.get("id") or "call_1",
                        "type": "function",
                        "function": {"name": tc["name"], "arguments": json.dumps(parsed)},
                    }
                ],
            }
        )
        messages.append(
            {
                "role": "tool",
                "tool_call_id": tc.get("id") or "call_1",
                "content": json.dumps(out),
            }
        )

    final_content = result.get("content") or ""
    if tool_results and provider.is_available() and not final_content:
        follow = await provider.chat(messages, tools=None)
        final_content = follow.get("content") or ""
    if tool_results and not final_content:
        final_content = "Resultados de herramientas (modo degradado):\n" + json.dumps(
            tool_results, indent=2, ensure_ascii=False
        )

    run.response = final_content
    run.status = "completed"
    run.finished_at = datetime.now(timezone.utc)
    run.meta = {"degraded": result.get("degraded", False), "tool_count": len(tool_results)}
    db.commit()

    write_audit(
        db,
        action="chat",
        resource_type="agent_run",
        resource_id=str(run.id),
        user_id=user.id,
        org_id=user.org_id,
    )
    return {
        "run_id": str(run.id),
        "content": final_content,
        "tool_results": tool_results,
        "degraded": result.get("degraded", False),
        "model": result.get("model"),
    }


@router.post("/stream")
async def chat_stream(
    body: ChatRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    provider = get_ai_provider()
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend([m.model_dump() for m in body.messages])

    async def event_gen():
        async for token in provider.chat_stream(messages, tools=None):
            yield {"event": "token", "data": token}
        yield {"event": "done", "data": "[DONE]"}

    return EventSourceResponse(event_gen())
