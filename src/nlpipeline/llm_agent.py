import os
import re
import json

from pydantic import ValidationError
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

from nlpipeline.models import PipelineSpec

# 1. Load your OpenAI key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Please set the OPENAI_API_KEY environment variable.")

# 2. Initialize the Chat model
llm = ChatOpenAI(
    model_name="gpt-3.5-turbo",
    openai_api_key=OPENAI_API_KEY,
    temperature=0.0,
)

# 3. Prompt template (wrapped ≤100 chars per line for Ruff)
prompt = PromptTemplate(
    input_variables=["description"],
    template_format="jinja2",
    template=(
        "You are an AI data engineer. Given a plain-English pipeline request,\n"
        "produce **only** a JSON object matching our PipelineSpec schema\n"
        "filled with concrete values—no placeholders or extra text.\n\n"
        "### Example\n"
        "**Request:** \"Ingest New York weather data daily, filter out temp\n"
        "and humidity, load into Postgres table weather_ny, then plot average\n"
        "daily temperature.\"\n\n"
        "**Output:**\n```json\n"
        "{\n"
        "  \"sources\": [ {\"type\": \"weather_api\",\n"
        "      \"params\": {\"lat\": 40.71, \"lon\": -74.01,\n"
        "        \"frequency\": \"daily\"}} ],\n"
        "  \"transforms\": [ {\"name\": \"filter_fields\",\n"
        "      \"params\": {\"fields\": [\"temperature_2m\",\n"
        "        \"relative_humidity_2m\"]}} ],\n"
        "  \"load\": {\"type\": \"postgres\",\n"
        "    \"params\": {\"table\": \"weather_ny\",\n"
        "      \"connection\":\n"
        "        \"postgresql://airflow:airflow@postgres/airflow\"}},\n"
        "  \"viz\": {\"type\": \"matplotlib\",\n"
        "    \"params\": {\"chart\": \"line\", \"x\": \"date\",\n"
        "      \"y\": \"temperature_2m\",\n"
        "      \"output\": \"monthly_avg_ny.png\"}} \n"
        "}\n```\n\n"
        "### Now you\n**Request:** \"{{ description }}\"\n\n"
        "**Output:**\n```json\n"
        "{\n"
        "  \"sources\": [ { \"type\": string, \"params\": object } ],\n"
        "  \"transforms\": [ { \"name\": string, \"params\": object } ],\n"
        "  \"load\": { \"type\": string, \"params\": object },\n"
        "  \"viz\": { \"type\": string, \"params\": object }\n"
        "}\n```\n"
    ),
)

chain = LLMChain(llm=llm, prompt=prompt)

# 4. Generate, clean, validate, pretty-print
def generate_pipeline_spec(description: str) -> str:
    """
    1) Call LLM → raw (may include ``` fences).
    2) Strip markdown fences.
    3) Validate with Pydantic v2’s model_validate_json().
    4) Return pretty-printed JSON.
    """
    try:
        raw = chain.run(description=description)
        cleaned = re.sub(r"```(?:json)?\s*|\s*```", "", raw).strip()
        spec = PipelineSpec.model_validate_json(cleaned)  # :contentReference[oaicite:1]{index=1}
        return json.dumps(spec.model_dump(), indent=2)

    except ValidationError as ve:
        err = ve.json()
        raise RuntimeError(
            f"Schema validation error:\n{err}\n\nCleaned output was:\n{cleaned}"
        )
    except Exception as e:
        raise RuntimeError(f"Error generating pipeline spec: {e}")
