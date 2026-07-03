"""The handoff primitive: agent-to-agent control transfer + context passing.

A handoff is the core multi-agent operation — one agent delegates a
*self-contained* sub-task to another and passes just the context that task
needs (a fresh context window, per Anthropic's sub-agent design). Modelling it
explicitly (rather than as an implicit function call) is what makes the trace
legible and mirrors the `handoff` table in the data model.
"""

from pydantic import BaseModel, Field

from agentfleet_worker.publish import Emitter, StepStatus, StepType


class Handoff(BaseModel):
    from_agent: str
    to_agent: str
    task: str  # the self-contained instruction the receiver executes
    context: dict[str, str] = Field(default_factory=dict)  # shared refs it may need


async def perform_handoff(emitter: Emitter, handoff: Handoff) -> Handoff:
    """Record a handoff as a step event and return it (control now transfers
    to `to_agent`). Emitting here — not inside either node — keeps the transfer
    a first-class, independently traceable event.
    """
    await emitter.emit(
        agent=handoff.from_agent,
        type=StepType.HANDOFF,
        status=StepStatus.COMPLETED,
        title=f"Hand off to {handoff.to_agent}",
        detail={
            "to_agent": handoff.to_agent,
            "task": handoff.task,
            "context": handoff.context,
        },
    )
    return handoff
