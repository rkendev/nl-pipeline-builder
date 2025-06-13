import pytest
from nlpipeline.llm_agent import generate_pipeline_spec
from nlpipeline.models import PipelineSpec

def test_prompt_roundtrip(monkeypatch):
    # stub out the LLM call
    sample = {
        "sources": [{"type": "weather_api", "params": {"lat": 52.5, "lon": 13.4}}],
        "transforms": [{"name": "filter_fields", "params": {"fields": ["temperature_2m"]}}],
        "load": {"type": "postgres", "params": {"table": "weather"}},
        "viz": {"type": "matplotlib", "params": {"plot_type": "line"}}
    }
    monkeypatch.setattr(
        "nlpipeline.llm_agent._chain.run",
        lambda **kwargs: json.dumps(sample)
    )
    raw = generate_pipeline_spec("dummy")
    spec = PipelineSpec.parse_raw(raw)
    assert spec.sources[0].type == "weather_api"
    assert spec.viz.type == "matplotlib"
