"""Classify user query intent to route to the appropriate analysis node."""
import json
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from app.config import settings
from app.ai.state import WaypointAnalysisState

SYSTEM_PROMPT = """You are an intent classifier for a program management AI assistant.
Classify the user's query into exactly ONE of these categories:

- scope_creep: Questions about scope changes, drift, additions/removals from baseline
- dependency: Questions about cross-workstream dependencies, blocking, critical path
- gate_readiness: Questions about gate progress, exit criteria, readiness assessments
- risk: Questions about risks, threats, mitigations, risk correlation across workstreams
- status: Questions about overall program status, executive summaries, progress updates
- general: Everything else (greetings, unclear questions, meta-questions)

Respond with ONLY a JSON object: {"intent": "<category>"}"""


async def intent_classifier(state: WaypointAnalysisState) -> dict:
    llm = ChatAnthropic(
        model=settings.AI_MODEL,
        anthropic_api_key=settings.ANTHROPIC_API_KEY,
        max_tokens=100,
    )
    response = await llm.ainvoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=state["query"]),
    ])

    try:
        parsed = json.loads(response.content)
        intent = parsed.get("intent", "general")
    except (json.JSONDecodeError, AttributeError):
        content = str(response.content).lower()
        for category in ["scope_creep", "dependency", "gate_readiness", "risk", "status"]:
            if category in content:
                intent = category
                break
        else:
            intent = "general"

    valid_intents = {"scope_creep", "dependency", "gate_readiness", "risk", "status", "general"}
    if intent not in valid_intents:
        intent = "general"

    return {"query_type": intent}
