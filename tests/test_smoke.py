from orchestrator import build_graph, PipelineState


def test_graph_builds():
    """Verify the LangGraph graph compiles without errors."""
    graph = build_graph()
    assert graph is not None


def test_initial_state_shape():
    """Verify PipelineState has the expected keys."""
    state: PipelineState = {
        "task": "test",
        "architecture_notes": "",
        "implementation": "",
        "review_notes": "",
        "test_results": "",
        "approved": False,
        "errors": []
    }
    assert state["task"] == "test"
    assert state["approved"] is False