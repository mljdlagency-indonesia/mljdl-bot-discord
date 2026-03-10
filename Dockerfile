FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# HF Spaces requires port 7860 — simple health check endpoint
EXPOSE 7860

CMD ["python", "run.py"]
