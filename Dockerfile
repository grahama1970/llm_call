FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 3010

CMD ["uvicorn", "claude_openai_proxy:app", "--host", "0.0.0.0", "--port", "3010"]
