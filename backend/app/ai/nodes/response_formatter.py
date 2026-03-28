"""Format accumulated analysis results into a coherent response for the UI."""
import json
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from app.config import settings
from app.ai.state import WaypointAnalysisState

SYSTEM_PROMPT = """You are a response formatter for a program management AI assistant.
Take the accumulated analysis results and format them into a clear, concise response
for program leadership at Southwest Airlines.

The response should be:
- Professional and direct
- Actionable with specific next steps
- Structured with clear sections

Respond with a well-formatted text summary (not JSON). Use markdown formatting.
Keep it under 500 words."""


async def response_formatter(state: WaypointAnalysisState) -> dict:
    analysis = state.get("analysis_results", [])
    recommendations = state.get("recommendations", [])
    query = state.get("query", "")
    query_type = state.get("query_type", "general")

    if not analysis:
        return {
            "summary": f"I don't have enough data to analyze that query. "
                       f"Try asking about workstream status, gate readiness, "
                       f"dependencies, risks, or scope changes."
        }

    llm = ChatAnthropic(
        model=settings.AI_MODEL,
        anthropic_api_key=settings.ANTHROPIC_API_KEY,
        max_tokens=1500,
    )

    analysis_text = "\n\n".join(
        f"--- {a['type'].upper()} ANALYSIS ---\n{a['content']}"
        for a in analysis
    )
    recs_text = "\n".join(f"- {r}" for r in recommendations) if recommendations else "None"

    response = await llm.ainvoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=(
            f"Original query: {query}\n"
            f"Analysis type: {query_type}\n\n"
            f"Analysis results:\n{analysis_text}\n\n"
            f"Recommendations:\n{recs_text}"
        )),
    ])

    return {"summary": str(response.content)}
