FROM python:3.10-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1 \
        tesseract-ocr \
        tesseract-ocr-all \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "src/dashboard/run.py", "--server.address=0.0.0.0"]