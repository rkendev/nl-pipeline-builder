# Dockerfile
# syntax=docker/dockerfile:1
FROM python:3.12-slim

WORKDIR /workspace

# install only runtime deps
RUN pip install --no-cache-dir \
      streamlit \
      psycopg2-binary \
      sqlalchemy

# copy your app code
COPY src/nlpipeline ./src/nlpipeline

# expose Streamlit
EXPOSE 8501

# one-line JSON CMD
CMD ["streamlit","run","src/nlpipeline/streamlit_app.py","--server.port=8501","--server.enableCORS=false"]
