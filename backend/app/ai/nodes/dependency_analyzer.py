"""Analyze cross-workstream dependencies, critical path, and cascading risks."""
import json
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from app.config import settings
from app.ai.state import WaypointAnalysisState

SYSTEM_PROMPT = """You are a dependency analyst for Project Waypoint at Southwest Airlines.
Analyze the dependency graph across 11 workstreams to identify:

1. Critical path issues (blocked or at-risk critical dependencies)
2. Cascading delay risks (if workstream A slips, what downstream workstreams are affected)
3. Dependency bottlenecks (workstreams with too many inbound dependencies)
4. Unresolved blocking dependencies

Provide analysis as JSON:
{
  "critical_path_issues": [{"description": "...", "affected_workstreams": ["..."]}],
  "cascading_risks": [{"trigger": "...", "downstream_impact": "..."}],
  "bottlenecks": [{"workstream": "...", "inbound_count": N, "concern": "..."}],
  "recommendations": ["recommendation1", "recommendation2"]
}"""


async def dependency_analyzer(state: WaypointAnalysisState) -> dict:
    llm = ChatAnthropic(
        model=settings.AI_MODEL,
        anthropic_api_key=settings.ANTHROPIC_API_KEY,
        max_tokens=2000,
    )

    context = json.dumps(state["dependency_graph"], indent=2)
    response = await llm.ainvoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"User query: {state['query']}\n\nDependency graph:\n{context}"),
    ])

    results = state.get("analysis_results", []).copy()
    results.append({"type": "dependency", "content": str(response.content)})

    try:
        parsed = json.loads(str(response.content))
        recommendations = parsed.get("recommendations", [])
    except (json.JSONDecodeError, AttributeError):
        recommendations = []

    existing_recs = state.get("recommendations", []).copy()
    existing_recs.extend(recommendations)

    return {"analysis_results": results, "recommendations": existing_recs}
