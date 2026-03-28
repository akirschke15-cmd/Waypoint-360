"""Cross-workstream risk correlation and compound risk identification."""
import json
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from app.config import settings
from app.ai.state import WaypointAnalysisState

SYSTEM_PROMPT = """You are a risk analyst for Project Waypoint at Southwest Airlines.
Analyze risks across all 11 workstreams to identify:

1. Compound risks: multiple workstreams citing the same root cause (e.g., resource constraints)
2. Risk correlations: risks that amplify each other across workstreams
3. Highest-severity risks requiring immediate attention
4. Risks without adequate mitigation plans

Provide analysis as JSON:
{
  "compound_risks": [{"theme": "...", "affected_workstreams": ["..."], "severity": "..."}],
  "correlations": [{"risk_a": "...", "risk_b": "...", "amplification": "..."}],
  "immediate_attention": [{"workstream": "...", "risk": "...", "reason": "..."}],
  "mitigation_gaps": [{"workstream": "...", "risk": "...", "gap": "..."}],
  "overall_risk_score": "high/medium/low",
  "recommendations": ["recommendation1"]
}"""


async def risk_aggregator(state: WaypointAnalysisState) -> dict:
    llm = ChatAnthropic(
        model=settings.AI_MODEL,
        anthropic_api_key=settings.ANTHROPIC_API_KEY,
        max_tokens=2000,
    )

    ws_data = json.dumps(state["workstream_data"], indent=2)
    response = await llm.ainvoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"User query: {state['query']}\n\nWorkstream data with risks:\n{ws_data}"),
    ])

    results = state.get("analysis_results", []).copy()
    results.append({"type": "risk", "content": str(response.content)})

    try:
        parsed = json.loads(str(response.content))
        recommendations = parsed.get("recommendations", [])
    except (json.JSONDecodeError, AttributeError):
        recommendations = []

    existing_recs = state.get("recommendations", []).copy()
    existing_recs.extend(recommendations)

    return {"analysis_results": results, "recommendations": existing_recs}
