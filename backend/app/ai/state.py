"""LangGraph state schema for Waypoint 360 AI analysis."""
from typing import TypedDict


class WaypointAnalysisState(TypedDict):
    query: str
    query_type: str
    workstream_data: dict
    dependency_graph: dict
    gate_data: dict
    analysis_results: list
    recommendations: list
    summary: str
