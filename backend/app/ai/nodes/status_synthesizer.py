"""Generate executive summary from workstream status updates and program data."""
import json
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from app.config import settings
from app.ai.state import WaypointAnalysisState

SYSTEM_PROMPT = """You are an executive briefing assistant for Project Waypoint at Southwest Airlines.
Synthesize data from all workstreams into a concise executive summary.

Include:
1. Overall program health (green/yellow/red)
2. Key highlights (what's going well)
3. Key concerns (what needs attention)
4. Critical decisions needed
5. Next 2-week outlook

Provide analysis as JSON:
{
  "program_health": "green/yellow/red",
  "highlights": ["highlight1", "highlight2"],
  "concerns": ["concern1", "concern2"],
  "decisions_needed": ["decision1"],
  "outlook": "2-week outlook summary",
  "recommendations": ["recommendation1"]
}"""


async def status_synthesizer(state: WaypointAnalysisState) -> dict:
    llm = ChatAnthropic(
        model=settings.AI_MODEL,
        anthropic_api_key=settings.ANTHROPIC_API_KEY,
        max_tokens=2000,
    )

    ws_data = json.dumps(state["workstream_data"], indent=2)
    gate_data = json.dumps(state["gate_data"], indent=2)
    dep_data = json.dumps(state["dependency_graph"], indent=2)

    response = await llm.ainvoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"User query: {state['query']}\n\nWorkstreams:\n{ws_data}\n\nGates:\n{gate_data}\n\nDependencies:\n{dep_data}"),
    ])

    results = state.get("analysis_results", []).copy()
    results.append({"type": "status", "content": str(response.content)})

    try:
        parsed = json.loads(str(response.content))
        recommendations = parsed.get("recommendations", [])
    except (json.JSONDecodeError, AttributeError):
        recommendations = []

    existing_recs = state.get("recommendations", []).copy()
    existing_recs.extend(recommendations)

    return {"analysis_results": results, "recommendations": existing_recs}
