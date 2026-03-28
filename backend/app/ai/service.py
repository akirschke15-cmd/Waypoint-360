"""AI service that orchestrates LangGraph analysis."""
import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.graph import build_waypoint_graph
from app.ai.state import WaypointAnalysisState
from app.ai.data_loader import (
    load_all_workstreams,
    load_dependency_graph,
    load_gate_data,
)

logger = logging.getLogger(__name__)


class AIService:
    def __init__(self):
        self.graph = build_waypoint_graph()

    async def _load_context(self, db: AsyncSession, gate_id: int | None = None) -> dict:
        """Pre-load all data needed for analysis."""
        workstream_data = await load_all_workstreams(db)
        dependency_graph = await load_dependency_graph(db)
        gate_data = await load_gate_data(db, gate_id=gate_id)
        return {
            "workstream_data": workstream_data,
            "dependency_graph": dependency_graph,
            "gate_data": gate_data,
        }

    async def query(self, query: str, db: AsyncSession) -> dict:
        """Run a natural language query through the full LangGraph pipeline."""
        context = await self._load_context(db)
        initial_state: WaypointAnalysisState = {
            "query": query,
            "query_type": "",
            "workstream_data": context["workstream_data"],
            "dependency_graph": context["dependency_graph"],
            "gate_data": context["gate_data"],
            "analysis_results": [],
            "recommendations": [],
            "summary": "",
        }

        result = await self.graph.ainvoke(initial_state)
        return {
            "query": query,
            "intent": result.get("query_type", "general"),
            "response": result.get("summary", ""),
            "recommendations": result.get("recommendations", []),
            "sources": [a["type"] for a in result.get("analysis_results", [])],
            "confidence": 0.85,
        }

    async def gate_readiness(self, gate_id: int, db: AsyncSession) -> dict:
        """Direct gate readiness assessment (bypasses intent classifier)."""
        context = await self._load_context(db, gate_id=gate_id)
        from app.ai.nodes import gate_readiness_assessor, response_formatter

        state: WaypointAnalysisState = {
            "query": f"Assess readiness for gate {gate_id}",
            "query_type": "gate_readiness",
            "workstream_data": context["workstream_data"],
            "dependency_graph": context["dependency_graph"],
            "gate_data": context["gate_data"],
            "analysis_results": [],
            "recommendations": [],
            "summary": "",
        }

        state_after = await gate_readiness_assessor(state)
        merged = {**state, **state_after}
        final = await response_formatter(merged)
        merged.update(final)

        return {
            "gate_id": gate_id,
            "status": "analyzed",
            "message": merged.get("summary", ""),
            "confidence": 0.8,
            "workstream_readiness": [],
            "blockers": [],
            "recommendations": merged.get("recommendations", []),
        }

    async def scope_creep(self, db: AsyncSession) -> dict:
        """Direct scope creep detection."""
        context = await self._load_context(db)
        from app.ai.nodes import scope_creep_detector, response_formatter

        state: WaypointAnalysisState = {
            "query": "Detect scope creep across all workstreams",
            "query_type": "scope_creep",
            "workstream_data": context["workstream_data"],
            "dependency_graph": context["dependency_graph"],
            "gate_data": context["gate_data"],
            "analysis_results": [],
            "recommendations": [],
            "summary": "",
        }

        state_after = await scope_creep_detector(state)
        merged = {**state, **state_after}
        final = await response_formatter(merged)
        merged.update(final)

        return {
            "status": "analyzed",
            "message": merged.get("summary", ""),
            "workstreams_flagged": [],
            "total_changes": 0,
        }

    async def correlated_risks(self, db: AsyncSession) -> dict:
        """Direct cross-workstream risk correlation."""
        context = await self._load_context(db)
        from app.ai.nodes import risk_aggregator, response_formatter

        state: WaypointAnalysisState = {
            "query": "Identify correlated risks across all workstreams",
            "query_type": "risk",
            "workstream_data": context["workstream_data"],
            "dependency_graph": context["dependency_graph"],
            "gate_data": context["gate_data"],
            "analysis_results": [],
            "recommendations": [],
            "summary": "",
        }

        state_after = await risk_aggregator(state)
        merged = {**state, **state_after}
        final = await response_formatter(merged)
        merged.update(final)

        return {
            "status": "analyzed",
            "message": merged.get("summary", ""),
            "correlated_risks": [],
            "compound_risk_score": 0.0,
        }

    async def executive_summary(self, db: AsyncSession) -> dict:
        """Direct executive summary generation."""
        context = await self._load_context(db)
        from app.ai.nodes import status_synthesizer, response_formatter

        state: WaypointAnalysisState = {
            "query": "Generate executive summary of program status",
            "query_type": "status",
            "workstream_data": context["workstream_data"],
            "dependency_graph": context["dependency_graph"],
            "gate_data": context["gate_data"],
            "analysis_results": [],
            "recommendations": [],
            "summary": "",
        }

        state_after = await status_synthesizer(state)
        merged = {**state, **state_after}
        final = await response_formatter(merged)
        merged.update(final)

        return {
            "status": "analyzed",
            "message": merged.get("summary", ""),
            "summary": merged.get("summary", ""),
            "key_highlights": [],
            "action_items": merged.get("recommendations", []),
        }


# Singleton
ai_service = AIService()
