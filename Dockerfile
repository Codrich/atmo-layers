FROM python:3.12-slim
WORKDIR /app
COPY src ./src
COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir fastapi uvicorn
EXPOSE 8000
CMD ["python", "-m", "src.atmo_layers", "--serve"]
