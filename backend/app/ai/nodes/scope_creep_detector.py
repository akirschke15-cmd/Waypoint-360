"""Detect scope creep by comparing baseline vs current scope across workstreams."""
import json
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from app.config import settings
from app.ai.state import WaypointAnalysisState

SYSTEM_PROMPT = """You are a scope creep analyst for Project Waypoint at Southwest Airlines.
Analyze workstream scope data to detect drift between baseline and current scope.

For each workstream, compare baseline_scope with current scope_in/scope_out.
Flag any additions, removals, or modifications. Assess risk level of scope changes.

Provide analysis as JSON:
{
  "workstreams_flagged": [
    {"workstream": "name", "finding": "description of drift", "risk_level": "high/medium/low"}
  ],
  "overall_assessment": "summary",
  "recommendations": ["recommendation1", "recommendation2"]
}"""


async def scope_creep_detector(state: WaypointAnalysisState) -> dict:
    llm = ChatAnthropic(
        model=settings.AI_MODEL,
        anthropic_api_key=settings.ANTHROPIC_API_KEY,
        max_tokens=2000,
    )

    context = json.dumps(state["workstream_data"], indent=2)
    response = await llm.ainvoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"User query: {state['query']}\n\nWorkstream data:\n{context}"),
    ])

    results = state.get("analysis_results", []).copy()
    results.append({"type": "scope_creep", "content": str(response.content)})

    try:
        parsed = json.loads(str(response.content))
        recommendations = parsed.get("recommendations", [])
    except (json.JSONDecodeError, AttributeError):
        recommendations = []

    existing_recs = state.get("recommendations", []).copy()
    existing_recs.extend(recommendations)

    return {"analysis_results": results, "recommendations": existing_recs}
