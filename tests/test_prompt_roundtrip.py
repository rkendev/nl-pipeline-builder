import os
import json

from langchain.chains import LLMChain

def test_prompt_roundtrip(monkeypatch):
    # 1) Set API key before importing llm_agent
    os.environ["OPENAI_API_KEY"] = "test-key"

    # 2) Defer import until after env var is set
    from nlpipeline.llm_agent import generate_pipeline_spec
    from nlpipeline.models import PipelineSpec

    # 3) Stub LLMChain.run for a known sample
    sample = {
        "sources": [{"type": "weather_api", "params": {"lat": 52.5, "lon": 13.4}}],
        "transforms": [{"name": "filter_fields", "params": {"fields": ["temperature_2m"]}}],
        "load":    {"type": "postgres", "params": {"table": "weather"}},
        "viz":     {"type": "matplotlib", "params": {"plot_type": "line"}}
    }
    monkeypatch.setattr(
        LLMChain,
        "run",
        lambda self, **kwargs: json.dumps(sample)
    )

    # 4) Generate, validate, assert
    raw = generate_pipeline_spec("dummy description")
    spec = PipelineSpec.model_validate_json(raw)  # :contentReference[oaicite:2]{index=2}

    assert spec.sources[0].type == "weather_api"
    assert spec.viz.type == "matplotlib"
