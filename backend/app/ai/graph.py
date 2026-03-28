"""Build the LangGraph StateGraph for Waypoint 360 AI analysis."""
from langgraph.graph import StateGraph, END

from .state import WaypointAnalysisState
from .nodes import (
    intent_classifier,
    scope_creep_detector,
    dependency_analyzer,
    gate_readiness_assessor,
    risk_aggregator,
    status_synthesizer,
    response_formatter,
)


def route_by_intent(state: WaypointAnalysisState) -> str:
    return state.get("query_type", "general")


def build_waypoint_graph():
    """Build and compile the Waypoint analysis StateGraph."""
    graph = StateGraph(WaypointAnalysisState)

    # Add nodes
    graph.add_node("intent_classifier", intent_classifier)
    graph.add_node("scope_creep_detector", scope_creep_detector)
    graph.add_node("dependency_analyzer", dependency_analyzer)
    graph.add_node("gate_readiness_assessor", gate_readiness_assessor)
    graph.add_node("risk_aggregator", risk_aggregator)
    graph.add_node("status_synthesizer", status_synthesizer)
    graph.add_node("response_formatter", response_formatter)

    # Entry point
    graph.set_entry_point("intent_classifier")

    # Conditional routing from intent classifier
    graph.add_conditional_edges(
        "intent_classifier",
        route_by_intent,
        {
            "scope_creep": "scope_creep_detector",
            "dependency": "dependency_analyzer",
            "gate_readiness": "gate_readiness_assessor",
            "risk": "risk_aggregator",
            "status": "status_synthesizer",
            "general": "response_formatter",
        },
    )

    # All analysis nodes flow to response formatter
    for node in [
        "scope_creep_detector",
        "dependency_analyzer",
        "gate_readiness_assessor",
        "risk_aggregator",
        "status_synthesizer",
    ]:
        graph.add_edge(node, "response_formatter")

    # Response formatter -> END
    graph.add_edge("response_formatter", END)

    return graph.compile()
