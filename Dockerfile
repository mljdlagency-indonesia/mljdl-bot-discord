FROM python:3.11-slim

# Fix DNS resolution di HF Spaces
RUN echo "nameserver 8.8.8.8" > /etc/resolv.conf && \
    echo "nameserver 8.8.4.4" >> /etc/resolv.conf

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# HF Spaces requires port 7860 — simple health check endpoint
EXPOSE 7860

CMD ["python", "run.py"]
