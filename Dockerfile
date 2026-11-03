FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY publisher.py .
RUN useradd -m -u 10001 publisher && mkdir -p /app/data && chown publisher:publisher /app/data
USER publisher
CMD ["python", "-u", "publisher.py", "serve"]
