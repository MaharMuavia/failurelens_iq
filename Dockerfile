FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend ./backend
COPY data ./data
COPY knowledge ./knowledge
COPY scripts ./scripts
RUN adduser --disabled-password --gecos "" appuser \
    && mkdir -p /app/reports /app/data/uploads \
    && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

