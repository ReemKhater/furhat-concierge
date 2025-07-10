FROM python:3.9

RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libssl-dev \
    libgomp1 \ 
    bash \
    && apt-get clean

RUN pip install --no-cache-dir \
    langchain-text-splitters \
    langchain-chroma \
    langchain-community \
    pypdf \
    sentence-transformers \
    furhat_remote_api \
    python-dotenv \
    langdetect 

WORKDIR /app

ADD main.py .
ADD .env .

COPY Knowledge /app/Knowledge

VOLUME ["/app/conversation_logs", "/app/chroma_db"]

CMD ["python", "/app/main.py"]
