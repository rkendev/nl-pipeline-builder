import os
import re
import json
from pydantic import ValidationError
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

from nlpipeline.models import PipelineSpec

# -----------------------------------------------------------------------------
# 1. Load your OpenAI key
# -----------------------------------------------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Please set the OPENAI_API_KEY environment variable.")

# -----------------------------------------------------------------------------
# 2. Initialize the Chat model
# -----------------------------------------------------------------------------
llm = ChatOpenAI(
    model_name="gpt-3.5-turbo",
    openai_api_key=OPENAI_API_KEY,
    temperature=0.0,
)

# -----------------------------------------------------------------------------
# 3. Jinja2 prompt with few-shot example
# -----------------------------------------------------------------------------
prompt = PromptTemplate(
    input_variables=["description"],
    template_format="jinja2",
    template=(
        "You are an AI data engineer.  Given a plain-English pipeline request, produce\n"
        "**only** a JSON object matching our PipelineSpec schema, with actual values.\n\n"
        "### Example\n"
        "**Request:** \"Ingest New York weather data daily, filter out temp and humidity, "
        "load into Postgres table weather_ny, then plot average daily temperature.\"\n\n"
        "**Output:**\n```json\n"
        "{\n"
        "  \"sources\": [\n"
        "    {\n"
        "      \"type\": \"weather_api\",\n"
        "      \"params\": { \"lat\": 40.71, \"lon\": -74.01, \"frequency\": \"daily\" }\n"
        "    }\n"
        "  ],\n"
        "  \"transforms\": [\n"
        "    { \"name\": \"filter_fields\", \"params\": { \"fields\": [\"temperature_2m\", "
        "\"relative_humidity_2m\"] } }\n"
        "  ],\n"
        "  \"load\": { \"type\": \"postgres\", \"params\": "
        "{ \"table\": \"weather_ny\", \"connection\": \"postgresql://airflow:airflow@postgres/airflow\" } },\n"
        "  \"viz\": { \"type\": \"matplotlib\", \"params\": "
        "{ \"chart\": \"line\", \"x\": \"date\", \"y\": \"temperature_2m\", \"output\": \"monthly_avg_ny.png\" } }\n"
        "}\n```\n\n"
        "### Now you\n"
        "**Request:** \"{{ description }}\"\n\n"
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

# -----------------------------------------------------------------------------
# 4. Generate, clean, validate, and pretty-print the spec
# -----------------------------------------------------------------------------
def generate_pipeline_spec(description: str) -> str:
    """
    1) Invoke the LLM to get a raw string (may include ```json fences).
    2) Strip out any markdown code fences.
    3) Parse & validate with PipelineSpec.
    4) Return a pretty-printed JSON string.
    """
    try:
        raw = chain.run(description=description)

        # Remove any ```json or ``` fences (and surrounding newlines)
        cleaned = re.sub(r"```(?:json)?\s*|\s*```", "", raw).strip()

        # Validate & parse
        spec = PipelineSpec.parse_raw(cleaned)

        # Pretty-print via Python's json module
        return json.dumps(spec.model_dump(), indent=2)

    except ValidationError as ve:
        err = ve.json()
        raise RuntimeError(f"Schema validation error:\n{err}\n\nCleaned output was:\n{cleaned}")
    except Exception as e:
        raise RuntimeError(f"Error generating pipeline spec: {e}")
