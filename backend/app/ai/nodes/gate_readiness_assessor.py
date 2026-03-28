"""Assess gate readiness by evaluating exit criteria and deliverable status."""
import json
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from app.config import settings
from app.ai.state import WaypointAnalysisState

SYSTEM_PROMPT = """You are a gate readiness assessor for Project Waypoint at Southwest Airlines.
Evaluate the readiness of stage gates based on exit criteria status and workstream deliverables.

For each gate (or the specific gate asked about), assess:
1. Exit criteria completion status
2. Per-workstream deliverable progress
3. Blockers preventing gate passage
4. Overall confidence score (0-100%)

Provide analysis as JSON:
{
  "gate_assessments": [
    {
      "gate": "name",
      "confidence_pct": N,
      "criteria_met": N,
      "criteria_total": N,
      "blockers": ["blocker1"],
      "workstream_readiness": [{"workstream": "name", "status": "ready/at_risk/blocked"}]
    }
  ],
  "overall_assessment": "summary",
  "recommendations": ["recommendation1"]
}"""


async def gate_readiness_assessor(state: WaypointAnalysisState) -> dict:
    llm = ChatAnthropic(
        model=settings.AI_MODEL,
        anthropic_api_key=settings.ANTHROPIC_API_KEY,
        max_tokens=2000,
    )

    context = json.dumps(state["gate_data"], indent=2)
    ws_context = json.dumps(state["workstream_data"], indent=2)
    response = await llm.ainvoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"User query: {state['query']}\n\nGate data:\n{context}\n\nWorkstream context:\n{ws_context}"),
    ])

    results = state.get("analysis_results", []).copy()
    results.append({"type": "gate_readiness", "content": str(response.content)})

    try:
        parsed = json.loads(str(response.content))
        recommendations = parsed.get("recommendations", [])
    except (json.JSONDecodeError, AttributeError):
        recommendations = []

    existing_recs = state.get("recommendations", []).copy()
    existing_recs.extend(recommendations)

    return {"analysis_results": results, "recommendations": existing_recs}
